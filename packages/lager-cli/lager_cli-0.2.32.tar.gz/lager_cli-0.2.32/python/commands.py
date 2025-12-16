"""
    lager.python.commands

    Commands for running lager python
"""
import os
import shutil
import gzip
import json
import uuid
import sys
import threading
import pathlib
import itertools
import functools
import signal
import tempfile
import requests
import click
import trio
from ..debug.tunnel import serve_tunnel
from ..context import get_default_gateway
from ..util import (
    stream_python_output, zip_dir, SizeLimitExceeded,
    FAILED_TO_RETRIEVE_EXIT_CODE,
    SIGTERM_EXIT_CODE,
    SIGKILL_EXIT_CODE,
    StreamDatatypes,
    stdout_is_stderr,
)
from ..paramtypes import EnvVarType, PortForwardType
from ..exceptions import OutputFormatNotSupported

MAX_ZIP_SIZE = 20_000_000  # Max size of zipped folder in bytes

# Handle SIGPIPE for pipeline support (e.g., lager python script.py | head)
# When the downstream process in a pipeline closes, we should exit gracefully
if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

_ORIGINAL_SIGINT_HANDLER = signal.getsignal(signal.SIGINT)

def sigint_handler(kill_python, _sig, _frame):
    """
        Handle Ctrl+C by restoring the old signal handler (so that subsequent Ctrl+C will actually
        stop python), and send the SIGTERM to the running docker container.
    """
    click.echo(' Attempting to stop Lager Python job')
    signal.signal(signal.SIGINT, _ORIGINAL_SIGINT_HANDLER)
    kill_python(signal.SIGINT)

def _do_exit(exit_code, box, session, downloads):
    if exit_code == FAILED_TO_RETRIEVE_EXIT_CODE:
        click.secho('Failed to retrieve script exit code.', fg='red', err=True)
    elif exit_code == SIGTERM_EXIT_CODE:
        click.secho('Gateway script terminated due to timeout.', fg='red', err=True)
    elif exit_code == SIGKILL_EXIT_CODE:
        click.secho('Gateway script forcibly killed due to timeout.', fg='red', err=True)

    for filename in downloads:
        try:
            with session.download_file(box, filename) as resp:
                # Check for HTTP errors
                if resp.status_code >= 400:
                    if resp.status_code == 404:
                        click.secho(f'Failed to download {filename}: File not found', fg='red', err=True)
                    else:
                        try:
                            error_msg = resp.json().get('error', resp.text)
                        except:
                            error_msg = resp.text
                        click.secho(f'Failed to download {filename}: HTTP {resp.status_code} - {error_msg}', fg='red', err=True)
                    continue

                basename = os.path.basename(filename)
                # DirectHTTPSession returns raw files, backend returns gzipped
                # Detect format by checking magic bytes (gzip starts with 0x1f8b)
                content = resp.content

                # Check if content is gzipped by looking at first 2 bytes
                is_gzipped = len(content) >= 2 and content[0] == 0x1f and content[1] == 0x8b

                with open(basename, 'wb') as f_out:
                    if is_gzipped:
                        # Decompress gzipped content
                        f_out.write(gzip.decompress(content))
                    else:
                        # Write raw content
                        f_out.write(content)
        except requests.HTTPError as exc:
            if hasattr(exc, 'response') and exc.response.status_code == 404:
                click.secho(f'Failed to download {filename}: File not found', fg='red', err=True)
            else:
                click.secho(f'Failed to download {filename}: {exc}', fg='red', err=True)
        except Exception as exc:  # pylint: disable=broad-except
            click.secho(f'Failed to download {filename}: {exc}', fg='red', err=True)
    sys.exit(exit_code)

def debug_tunnel(ctx, box):
    host = 'localhost'
    port = 5555
    connection_params = ctx.obj.websocket_connection_params(socktype='pdb', gateway_id=box)
    try:
        trio.run(serve_tunnel, host, port, connection_params, None)
    except PermissionError as exc:
        click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        if ctx.obj.debug:
            raise

_SIGNAL_MAP = {
    'SIGINT': 2,
    'SIGQUIT': 3,
    'SIGABRT': 6,
    'SIGKILL': 9,
    'SIGUSR1': 10,
    'SIGUSR2': 12,
    'SIGTERM': 15,
    'SIGSTOP': 19,
}

_SIGNAL_CHOICES = click.Choice(list(_SIGNAL_MAP.keys()), case_sensitive=False)

def _get_signal_number(name):
    return _SIGNAL_MAP[name.upper()]

def collect_output_callback(datatype, content, context):
    if context is None:
        context = b''
    if datatype == StreamDatatypes.EXIT:
        return (True, context)
    elif datatype == StreamDatatypes.STDOUT:
        context += content
    elif datatype == StreamDatatypes.STDERR:
        click.echo(content.decode("utf-8", errors="ignore"), nl=False, err=True)
    elif datatype == StreamDatatypes.OUTPUT:
        click.echo(content)
    return False, context

def run_python_internal_get_output(ctx, runnable, box, image, env, passenv, kill, download, allow_overwrite, signum, timeout, detach, port, org, args, extra_files=None):
    return run_python_internal(ctx, runnable, box, image, env, passenv, kill, download, allow_overwrite, signum, timeout, detach, port, org, args, extra_files=None, callback=collect_output_callback)

def run_python_internal(ctx, runnable, box, image, env, passenv, kill, download, allow_overwrite, signum, timeout, detach, port, org, args, extra_files=None, callback=None, dut_name=None):
    if extra_files is None:
        extra_files = []

    # Use appropriate session based on whether box is an IP address
    gateway = box
    if gateway is None:
        gateway = get_default_gateway(ctx)

    # Auto-detect dut_name if not provided
    # This allows username lookup to work even when commands don't explicitly pass dut_name
    if dut_name is None and gateway:
        from ..dut_storage import get_dut_ip, get_dut_name_by_ip

        # Try forward lookup: is gateway a DUT name?
        resolved_ip = get_dut_ip(gateway)
        if resolved_ip:
            dut_name = gateway  # Preserve the DUT name for username lookup
            gateway = resolved_ip  # Use the IP for the session
        else:
            # Try reverse lookup: is gateway an IP with a saved DUT name?
            dut_name = get_dut_name_by_ip(gateway)
            # If found, dut_name is set; if not, it stays None (will use default username)

    session = ctx.obj.get_session_for_gateway(gateway, dut_name=dut_name)

    if kill:
        signum = _get_signal_number(signum)
        resp = session.kill_python(gateway, None, signum)
        resp.raise_for_status()
        return

    thread = threading.Thread(target=debug_tunnel, args=(ctx, gateway), daemon=True)
    thread.start()

    post_data = [
        ('image', image),
        ('stdout_is_stderr', stdout_is_stderr()),
        ('detach', '1' if detach else '0'),
    ]
    if org:
        post_data.append(('org', org))

    post_data.extend(
        zip(itertools.repeat('args'), args)
    )
    post_data.extend(
        zip(itertools.repeat('env'), env)
    )
    lager_process_id = str(uuid.uuid4())
    post_data.append(('env', f'LAGER_PROCESS_ID={lager_process_id}'))
    post_data.append(('env', f'LAGER_RUNNABLE={runnable}'))
    post_data.extend(
        zip(itertools.repeat('env'), [f'{name}={os.environ[name]}' for name in passenv])
    )
    post_data.extend(
        zip(itertools.repeat('portforwards'), [json.dumps(p._asdict()) for p in port])
    )

    if timeout is not None:
        post_data.append(('timeout', timeout))

    # Find and read includes from nearest .lager file
    include_dirs = {}
    if os.path.isfile(runnable):
        search_path = os.path.dirname(os.path.abspath(runnable))
    elif os.path.isdir(runnable):
        search_path = os.path.abspath(runnable)
    else:
        search_path = os.getcwd()

    # Search for .lager file starting from runnable location
    from ..config import make_config_path, get_includes_from_config, LAGER_CONFIG_FILE_NAME
    config_search_dir = search_path
    config_file = None
    while True:
        potential_config = make_config_path(config_search_dir)
        if os.path.exists(potential_config):
            config_file = potential_config
            break
        parent = os.path.dirname(config_search_dir)
        if parent == config_search_dir:
            break
        config_search_dir = parent

    if config_file:
        include_dirs = get_includes_from_config(config_file)
        # Validate includes and warn if paths don't exist
        for dest_path, source_path in list(include_dirs.items()):
            if not os.path.exists(source_path):
                click.secho(f'Warning: Include path "{source_path}" (for "{dest_path}") does not exist, skipping', fg='yellow', err=True)
                del include_dirs[dest_path]
            elif not os.path.isdir(source_path):
                click.secho(f'Warning: Include path "{source_path}" (for "{dest_path}") is not a directory, skipping', fg='yellow', err=True)
                del include_dirs[dest_path]

    if os.path.isfile(runnable):
        if extra_files or include_dirs:
            # Single file with extra files or includes: create temp dir, zip everything as a module
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy the main script to the temp directory as main.py
                # (gateway expects main.py when running a module)
                temp_script_path = os.path.join(temp_dir, 'main.py')
                shutil.copy2(runnable, temp_script_path)

                try:
                    max_content_size = MAX_ZIP_SIZE * 2
                    zipped_folder = zip_dir(temp_dir, extra_files, max_content_size=max_content_size, include_dirs=include_dirs)
                except SizeLimitExceeded:
                    click.secho(f'Folder content exceeds max size of {max_content_size:,} bytes', err=True, fg='red')
                    ctx.exit(1)

                if len(zipped_folder) > MAX_ZIP_SIZE:
                    click.secho(f'Zipped module content exceeds max size of {MAX_ZIP_SIZE:,} bytes', err=True, fg='red')
                    ctx.exit(1)

                post_data.append(('module', zipped_folder))
        else:
            # Single file without extra files or includes: upload as script (original behavior)
            with open(runnable, 'rb') as f:
                script_content = f.read()
            # Use BytesIO to create a file-like object that can be read multiple times
            import io
            script_file = io.BytesIO(script_content)
            post_data.append(('script', (os.path.basename(runnable), script_file, 'application/octet-stream')))
    elif os.path.isdir(runnable):
        try:
            max_content_size = MAX_ZIP_SIZE * 2
            zipped_folder = zip_dir(runnable, extra_files, max_content_size=max_content_size, include_dirs=include_dirs)
        except SizeLimitExceeded:
            click.secho(f'Folder content exceeds max size of {max_content_size:,} bytes', err=True, fg='red')
            ctx.exit(1)

        if len(zipped_folder) > MAX_ZIP_SIZE:
            click.secho(f'Zipped module content exceeds max size of {MAX_ZIP_SIZE:,} bytes', err=True, fg='red')
            ctx.exit(1)

        post_data.append(('module', zipped_folder))
    else:
        raise ValueError(f'Could not find runnable {runnable}')

    resp = session.run_python(gateway, files=post_data)

    # Check for HTTP errors before trying to parse streaming response
    if resp.status_code >= 400:
        click.secho(f'Gateway returned error (HTTP {resp.status_code})', fg='red', err=True)
        try:
            # Try to extract error message from JSON response
            error_data = resp.json()
            if 'error' in error_data:
                click.secho(f'Error: {error_data["error"]}', fg='red', err=True)
            else:
                click.echo(resp.text, err=True)
        except Exception:
            click.echo(resp.text, err=True)
        ctx.exit(1)

    kill_python = functools.partial(session.kill_python, gateway, lager_process_id)
    handler = functools.partial(sigint_handler, kill_python)
    signal.signal(signal.SIGINT, handler)

    try:
        done = False
        context = None
        for (datatype, content) in stream_python_output(resp):
            if callback:
                done, context = callback(datatype, content, context)
                if done:
                    return context
            else:
                if datatype == StreamDatatypes.EXIT:
                    _do_exit(content, gateway, session, download)
                elif datatype == StreamDatatypes.STDOUT:
                    click.echo(content.decode("utf-8", errors="ignore"), nl=False)
                elif datatype == StreamDatatypes.STDERR:
                    click.echo(content.decode("utf-8", errors="ignore"), nl=False, err=True)
                elif datatype == StreamDatatypes.OUTPUT:
                    click.echo(content)

    except BrokenPipeError:
        # Pipeline downstream closed (e.g., lager python script.py | head)
        # Kill the remote process and exit gracefully
        kill_python(signal.SIGTERM)
        sys.exit(0)
    except OutputFormatNotSupported:
        click.secho('Response format not supported. Please upgrade lager-cli', fg='red', err=True)
        sys.exit(1)

@click.command()
@click.pass_context
@click.argument('runnable', required=False, type=click.Path(exists=True))
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--image', default='lagerdata/gatewaypy3:v0.1.84', help='Docker image', show_default=True)
@click.option(
    '--env',
    multiple=True, type=EnvVarType(), help='Environment variable (FOO=BAR)')
@click.option(
    '--passenv',
    multiple=True, help='Environment variable to inherit')
@click.option('--kill', is_flag=True, default=False, help='Terminate running script')
@click.option('--download', type=click.Path(exists=False, dir_okay=False), multiple=True, help='File to download after completion')
@click.option('--allow-overwrite', is_flag=True, default=False, help='Overwrite existing files when downloading')
@click.option('--signal', 'signum', default='SIGTERM', type=_SIGNAL_CHOICES, help='Signal to use with --kill', show_default=True)
@click.option('--timeout', type=click.INT, default=0, required=False, help='Max runtime in seconds (s)')
@click.option('--detach', '-d', is_flag=True, required=False, default=False, help='Detach')
@click.option('--port', '-p', multiple=True, help='Port forwarding (SRC_PORT[:DST_PORT][/PROTOCOL])', type=PortForwardType())
@click.option('--org', default=None, hidden=True)
@click.option('--add-file', type=click.Path(exists=True, dir_okay=False), multiple=True, help='File to upload with script')
@click.argument('args', nargs=-1)
def python(ctx, runnable, box, dut, image, env, passenv, kill, download, allow_overwrite, signum, timeout, detach, port, org, add_file, args):
    """Run Python script on gateway"""
    from ..dut_storage import resolve_and_validate_dut

    # Resolve and validate the box/dut name
    box_name = box or dut
    gateway = resolve_and_validate_dut(ctx, box_name)

    if not runnable and not kill:
        raise click.UsageError('Please supply a RUNNABLE or the --kill option')

    if not allow_overwrite:
        for filename in download:
            basename = os.path.basename(filename)
            file = pathlib.Path(basename)
            if file.exists():
                raise click.UsageError(f'File {basename} exists; please rename it or use the --allow-overwrite flag')

    # Pass the box name as an environment variable
    env = list(env) if env else []
    if box_name:
        env.append(f'LAGER_BOX={box_name}')

    run_python_internal(ctx, runnable, gateway, image, env, passenv, kill, download, allow_overwrite, signum, timeout, detach, port, org, args, add_file, dut_name=box_name)
