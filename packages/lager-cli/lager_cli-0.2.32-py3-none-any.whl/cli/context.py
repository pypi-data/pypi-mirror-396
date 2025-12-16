"""
    lager.context

    CLI context management
"""
from enum import Enum
import functools
import os
import json
import signal
import ssl

from uuid import uuid4

import urllib.parse
import urllib3
import requests
import click
from requests_toolbelt.sessions import BaseUrlSession
from . import __version__
from .exceptions import GatewayTimeoutError

_DEFAULT_HOST = 'https://app.lagerdata.com'
_DEFAULT_WEBSOCKET_HOST = 'wss://app.lagerdata.com'
DEFAULT_REGION = 'us-west-1'

def print_openocd_error(error):
    """
        Parse an openocd log file and print the error lines
    """
    if not error:
        return
    parsed = json.loads(error)
    logfile = parsed['logfile']
    if not logfile:
        return
    error_printed = False
    for line in logfile.splitlines():
        if 'Error: ' in line:
            error_printed = True
            click.secho(line, fg='red', err=True)

    if not error_printed:
        click.secho('OpenOCD failed to start', fg='red', err=True)

def print_docker_error(ctx, error):
    """
        Parse an openocd log file and print the error lines
    """
    if not error:
        return
    parsed = json.loads(error)
    stdout = parsed['stdout']
    stderr = parsed['stderr']
    click.echo(stdout, nl=False)
    click.secho(stderr, fg='red', err=True, nl=False)
    ctx.exit(parsed['returncode'])

def print_canbus_error(ctx, error):
    if not error:
        return
    parsed = json.loads(error)
    if parsed['stdout']:
        click.secho(parsed['stdout'], fg='red', nl=False)
    if parsed['stderr']:
        click.secho(parsed['stderr'], fg='red', err=True, nl=False)
        if parsed['stderr'] == 'Cannot find device "can0"\n':
            click.secho('Please check adapter connection', fg='red', err=True)


OPENOCD_ERROR_CODES = {
    'openocd_start_failed',
}

DOCKER_ERROR_CODES = set()

CANBUS_ERROR_CODES = {
    'canbus_up_failed',
}

class ElfHashMismatch(Exception):
    pass


def quote(gateway):
    return urllib.parse.quote(str(gateway), safe='')


def is_ip_address(address):
    """Check if the address is an IP address (instead of gateway ID)"""
    try:
        import ipaddress
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


class DirectIPSession:
    """
    Direct session for communicating with DUT IPs via SSH + docker exec
    """

    def __init__(self, ip_address, dut_name=None, *args, **kwargs):
        from .dut_storage import get_dut_user

        self.ip_address = ip_address

        # Look up username from DUT storage if DUT name is provided
        username = None
        if dut_name:
            username = get_dut_user(dut_name)

        # Default to 'lagerdata' if no username found
        if not username:
            username = 'lagerdata'

        self.ssh_host = f'{username}@{ip_address}'

    def _create_streaming_response(self, process):
        """Create a streaming mock response for a subprocess"""
        class StreamingMockResponse:
            def __init__(self, process):
                self.process = process
                self.headers = {'Lager-Output-Version': '1'}
                self._returncode = None

            def iter_content(self, chunk_size=1024):
                """Stream output in real-time using v1 protocol format"""
                import select
                import os
                import fcntl

                # Set stdout and stderr to non-blocking mode
                flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
                fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                flags = fcntl.fcntl(self.process.stderr, fcntl.F_GETFL)
                fcntl.fcntl(self.process.stderr, fcntl.F_SETFL, flags | os.O_NONBLOCK)

                # Buffers for line-based output
                stdout_buffer = b''
                stderr_buffer = b''

                def flush_buffer(buffer, fileno):
                    """Yield a buffer as a protocol message"""
                    if buffer:
                        header = f"{fileno} {len(buffer)} ".encode()
                        for byte in header:
                            yield bytes([byte])
                        for byte in buffer:
                            yield bytes([byte])

                # Stream output until process completes
                while True:
                    # Check if process has terminated
                    poll_result = self.process.poll()

                    # Use select to wait for data with timeout
                    readable, _, _ = select.select(
                        [self.process.stdout, self.process.stderr],
                        [], [],
                        0.1  # 100ms timeout
                    )

                    # Read from stdout if available
                    if self.process.stdout in readable:
                        try:
                            chunk = self.process.stdout.read(chunk_size)
                            if chunk:
                                stdout_buffer += chunk
                                # Flush complete lines
                                while b'\n' in stdout_buffer:
                                    line, stdout_buffer = stdout_buffer.split(b'\n', 1)
                                    line += b'\n'
                                    yield from flush_buffer(line, 1)
                        except BlockingIOError:
                            pass

                    # Read from stderr if available
                    if self.process.stderr in readable:
                        try:
                            chunk = self.process.stderr.read(chunk_size)
                            if chunk:
                                stderr_buffer += chunk
                                # Flush complete lines
                                while b'\n' in stderr_buffer:
                                    line, stderr_buffer = stderr_buffer.split(b'\n', 1)
                                    line += b'\n'
                                    yield from flush_buffer(line, 2)
                        except BlockingIOError:
                            pass

                    # If process has ended, read any remaining data and exit
                    if poll_result is not None:
                        # Read any remaining buffered data
                        while True:
                            try:
                                chunk = self.process.stdout.read(chunk_size)
                                if not chunk:
                                    break
                                stdout_buffer += chunk
                            except (BlockingIOError, ValueError):
                                break

                        while True:
                            try:
                                chunk = self.process.stderr.read(chunk_size)
                                if not chunk:
                                    break
                                stderr_buffer += chunk
                            except (BlockingIOError, ValueError):
                                break

                        # Flush any remaining complete lines
                        while b'\n' in stdout_buffer:
                            line, stdout_buffer = stdout_buffer.split(b'\n', 1)
                            line += b'\n'
                            yield from flush_buffer(line, 1)
                        while b'\n' in stderr_buffer:
                            line, stderr_buffer = stderr_buffer.split(b'\n', 1)
                            line += b'\n'
                            yield from flush_buffer(line, 2)

                        # Flush any remaining partial lines
                        yield from flush_buffer(stdout_buffer, 1)
                        yield from flush_buffer(stderr_buffer, 2)

                        # Send exit code
                        self._returncode = self.process.returncode
                        exit_code_str = str(self._returncode)
                        exit_code_bytes = exit_code_str.encode('utf-8')
                        header = f"- {len(exit_code_bytes)} ".encode()
                        for byte in header:
                            yield bytes([byte])
                        for byte in exit_code_bytes:
                            yield bytes([byte])
                        break

        return StreamingMockResponse(process)

    def run_python(self, gateway, files):
        """
        Run python directly in the container via SSH + docker exec
        """
        import subprocess
        import tempfile
        import os

        # Extract the script content and arguments from files
        script_content = None
        module_content = None
        args = []
        env_vars = []

        for name, content in files:
            if name == 'script':
                if hasattr(content, 'read'):
                    script_content = content.read().decode('utf-8')
                else:
                    script_content = content.decode('utf-8')
            elif name == 'module':
                # Module is a zipped directory
                module_content = content
            elif name == 'args':
                args.append(content)
            elif name == 'env':
                env_vars.append(content)

        if not script_content and not module_content:
            raise ValueError("No script or module content found")

        # Handle module (zipped directory) case
        if module_content:
            # Create temporary local zip file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False) as f:
                f.write(module_content)
                temp_zip = f.name

            try:
                # Generate unique remote paths
                import uuid
                remote_id = str(uuid.uuid4())[:8]
                remote_zip = f'/tmp/lager_module_{remote_id}.zip'
                remote_dir = f'/tmp/lager_module_{remote_id}'

                # Transfer zip to gateway
                subprocess.run(
                    ['scp', '-q', '-o', 'LogLevel=ERROR', temp_zip, f'{self.ssh_host}:{remote_zip}'],
                    check=True
                )

                # Extract on gateway using Python (since unzip might not be available)
                extract_cmd = f'python3 -c "import zipfile; z = zipfile.ZipFile(\'{remote_zip}\'); z.extractall(\'{remote_dir}\')"'
                result = subprocess.run(
                    ['ssh', '-o', 'LogLevel=ERROR', self.ssh_host, extract_cmd],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to extract module on gateway: {result.stderr}")

                # Copy the extracted module into the container
                container_dir = f'/tmp/lager_module_{remote_id}'
                subprocess.run(
                    ['ssh', '-o', 'LogLevel=ERROR', self.ssh_host,
                     f'docker cp {remote_dir}/. python:{container_dir}'],
                    check=True
                )

                # Build the remote command
                import shlex
                docker_cmd_parts = ['docker', 'exec', '-i']
                for env_var in env_vars:
                    docker_cmd_parts.extend(['-e', shlex.quote(env_var)])

                # Set working directory and add module directory to PYTHONPATH
                # Prepend container_dir to PYTHONPATH so imports from the module work
                # Include /app/gateway_python for lager module access
                docker_cmd_parts.extend(['-w', container_dir])
                docker_cmd_parts.extend(['-e', 'PYTHONPATH=.:/app/gateway_python:/app'])
                # Set LAGER_HOST_MODULE_FOLDER for error reporting
                docker_cmd_parts.extend(['-e', f'LAGER_HOST_MODULE_FOLDER={container_dir}'])

                # Run main.py (working directory is already set to container_dir)
                docker_cmd_parts.extend(['python', 'python3', 'main.py'])

                # Add script arguments
                for arg in args:
                    docker_cmd_parts.append(shlex.quote(arg))

                docker_cmd = ' '.join(docker_cmd_parts)
                cmd = ['ssh', '-o', 'LogLevel=ERROR', self.ssh_host, docker_cmd]

                # Execute
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False
                )

                # Get the streaming response
                response = self._create_streaming_response(process)

                # Schedule cleanup after execution
                import atexit
                def cleanup():
                    # Clean up files from container
                    subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', self.ssh_host,
                         f'docker exec python rm -rf {container_dir}'],
                        capture_output=True
                    )
                    # Clean up files from gateway host
                    subprocess.run(
                        ['ssh', '-o', 'LogLevel=ERROR', self.ssh_host,
                         f'rm -rf {remote_dir} {remote_zip}'],
                        capture_output=True
                    )
                atexit.register(cleanup)

                return response

            finally:
                # Clean up local temp file
                os.unlink(temp_zip)

        # Handle script case (existing logic)
        else:
            # Create a temporary file to transfer the script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                temp_script = f.name

            try:
                # Build the remote command that will run in the container
                # We need to properly quote arguments for shell execution through SSH
                import shlex

                # Build the docker exec command with environment variables
                docker_cmd_parts = ['docker', 'exec', '-i']
                for env_var in env_vars:
                    docker_cmd_parts.extend(['-e', shlex.quote(env_var)])

                # Add container name and python command
                docker_cmd_parts.extend(['python', 'python3', '-'])

                # Add script arguments with proper quoting
                for arg in args:
                    docker_cmd_parts.append(shlex.quote(arg))

                # Join into a single command string for SSH to execute
                docker_cmd = ' '.join(docker_cmd_parts)

                # Build the SSH command
                cmd = ['ssh', '-o', 'LogLevel=ERROR', self.ssh_host, docker_cmd]

                # Execute script in container by piping it via stdin
                # Use Popen instead of run() to enable real-time streaming output
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False  # Use binary mode for streaming
                )

                # Write the script to stdin and close it
                process.stdin.write(script_content.encode('utf-8'))
                process.stdin.close()

                # Create and return streaming response
                return self._create_streaming_response(process)

            finally:
                # Clean up temporary file
                os.unlink(temp_script)

    def gateway_hello(self, gateway):
        """
        Say hello directly to the DUT via container exec
        """
        import subprocess

        result = subprocess.run([
            'ssh', '-o', 'LogLevel=ERROR', self.ssh_host,
            'docker', 'exec', 'python',
            'python3', '-c', "print('Hello, world! Your gateway is connected.')"
        ], capture_output=True, text=True)

        class MockResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = status_code
                self.headers = {'Lager-Output-Version': '1'}

        return MockResponse(result.stdout)

    def kill_python(self, gateway, lager_process_id, sig=signal.SIGTERM):
        """Kill a running Python process on the gateway"""
        import requests
        import json

        # Use IP address only (not ssh_host which includes username)
        url = f'http://{self.ip_address}:5000/python/kill'
        payload = {
            'lager_process_id': lager_process_id,
            'signal': sig
        }

        try:
            response = requests.post(url, json=payload, timeout=5)
            return response
        except requests.exceptions.RequestException as e:
            # Return a mock response with error
            class ErrorResponse:
                def __init__(self, error):
                    self.text = str(error)
                    self.status_code = 500
                    self.headers = {}
            return ErrorResponse(e)

    def download_file(self, gateway, filename):
        """Download a file from gateway using scp"""
        import subprocess
        import tempfile
        import gzip
        import shutil

        class SCPResponse:
            """Response-like object for SCP downloads that supports context manager protocol"""
            def __init__(self, filepath):
                self.filepath = filepath
                self.gzipped_path = filepath + '.gz'
                self._file = None
                self.status_code = 200

            def __enter__(self):
                # Gzip the downloaded file (to match backend behavior)
                try:
                    with open(self.filepath, 'rb') as f_in:
                        with gzip.open(self.gzipped_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Open the gzipped file and expose it as .raw
                    self._file = open(self.gzipped_path, 'rb')
                    self.raw = self._file
                    return self
                except FileNotFoundError:
                    # File wasn't downloaded successfully
                    raise requests.HTTPError("File not found on gateway")

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self._file:
                    self._file.close()
                # Clean up temp files
                try:
                    if os.path.exists(self.filepath):
                        os.unlink(self.filepath)
                    if os.path.exists(self.gzipped_path):
                        os.unlink(self.gzipped_path)
                except Exception:
                    pass
                return False

            def raise_for_status(self):
                """Compatibility method for requests-like behavior"""
                if self.status_code >= 400:
                    raise requests.HTTPError(f"HTTP {self.status_code}")

        # Create a temporary file for the download
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_download')
        temp_file.close()

        # Download file using scp
        scp_cmd = ['scp', '-q', f'{self.ssh_host}:{filename}', temp_file.name]

        try:
            result = subprocess.run(scp_cmd, capture_output=True, check=True, timeout=60)
            return SCPResponse(temp_file.name)
        except subprocess.CalledProcessError as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

            # Check if it's a file not found error (scp exit code 1)
            error_msg = e.stderr.decode() if e.stderr else str(e)
            if 'No such file' in error_msg or e.returncode == 1:
                # Create a mock response that will raise HTTPError with 404
                class NotFoundResponse:
                    def __init__(self):
                        self.status_code = 404
                    def __enter__(self):
                        return self
                    def __exit__(self, *args):
                        return False
                    def raise_for_status(self):
                        err = requests.HTTPError("File not found")
                        err.response = self
                        raise err
                resp = NotFoundResponse()
                resp.raise_for_status()
            else:
                raise requests.HTTPError(f"Failed to download file: {error_msg}")
        except subprocess.TimeoutExpired:
            # Clean up temp file on timeout
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass
            raise requests.HTTPError("Download timeout")

    def run_pip(self, gateway, args):
        """
        Run pip commands in the python container via HTTP

        Args:
            gateway: Gateway identifier (IP address)
            args: List of pip arguments (e.g., ['install', 'pandas'])

        Returns:
            HTTP response with streaming output
        """
        import requests

        # Make HTTP request to the gateway's run-pip endpoint
        url = f'http://{self.ip_address}:5001/run/pip'

        try:
            response = requests.post(
                url,
                json={'args': args},
                stream=True,
                timeout=600  # 10 minute timeout for pip operations
            )

            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    pass
                raise requests.HTTPError(error_msg)

            return response

        except requests.exceptions.ConnectionError as e:
            raise requests.HTTPError(f"Failed to connect to gateway at {self.ip_address}: {e}")
        except requests.exceptions.Timeout:
            raise requests.HTTPError("Pip operation timed out")


class LagerSession(BaseUrlSession):
    """
        requests session wrapper
    """

    @staticmethod
    def handle_errors(ctx, r, *args, **kwargs):
        """
            Handle request errors
        """
        try:
            current_context = click.get_current_context()
            ctx = current_context
        except RuntimeError:
            pass
        if r.status_code == 404:
            parts = r.request.path_url.split('/')
            if len(parts) > 2 and 'download-file?filename=' in parts[-1]:
                r.raise_for_status()
            name = ctx.params.get('box') or ctx.params.get('dut') or ctx.obj.default_gateway
            click.secho('You don\'t have a Lagerbox with id `{}`'.format(name), fg='red', err=True)
            click.secho(
                'Please double check your login credentials and Lagerbox id',
                fg='red',
                err=True,
            )
            ctx.exit(1)
        if r.status_code == 422:
            error = r.json()['error']
            if error['code'] == 'gateway_timeout_error':
                raise GatewayTimeoutError(error['description'])
            if error['code'] == 'elf_hash_mismatch':
                raise ElfHashMismatch()

            if error['code'] in OPENOCD_ERROR_CODES:
                print_openocd_error(error['description'])
            elif error['code'] in DOCKER_ERROR_CODES or error['code'] == 'wifi_connection_failed':
                print_docker_error(ctx, error['description'])
            elif error['code'] in CANBUS_ERROR_CODES:
                print_canbus_error(ctx, error['description'])
            else:
                click.secho(error['description'], fg='red', err=True)
            ctx.exit(1)
        if r.status_code >= 500:
            if True:
                print(r.text)
            else:
                click.secho('Something went wrong with the Lager API', fg='red', err=True)
            ctx.exit(1)

        # Handle HTTP errors with user-friendly messages
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if r.status_code == 401:
                click.secho(f'Error: Authentication failed - invalid DUT/gateway identifier', fg='red', err=True)
                click.secho(f"Use 'lager duts' to list available DUTs", fg='yellow', err=True)
            elif r.status_code == 403:
                click.secho(f'Error: Access forbidden - you do not have permission to access this resource', fg='red', err=True)
            elif r.status_code == 404:
                click.secho(f'Error: Resource not found - the requested endpoint does not exist', fg='red', err=True)
            else:
                click.secho(f'Error: HTTP {r.status_code} - {e}', fg='red', err=True)

            if os.getenv('LAGER_DEBUG'):
                click.secho(f'\nDebug info: {r.url}', fg='yellow', err=True)
                click.secho(f'Response: {r.text[:500]}', fg='yellow', err=True)
            else:
                click.secho('(Set LAGER_DEBUG=1 to see full details)', fg='yellow', err=True)

            ctx.exit(1)

    def __init__(self, *args, response_hook=None, **kwargs):
        host = os.getenv('LAGER_HOST', _DEFAULT_HOST)
        base_url = '{}{}'.format(host, '/api/v1/')

        super().__init__(*args, base_url=base_url, **kwargs)
        verify = 'NOVERIFY' not in os.environ
        if not verify:
            urllib3.disable_warnings()

        self.headers.update({
            'Lager-Version': __version__,
            'Lager-Invocation-Id': str(uuid4()),
            })
        ci_env = get_ci_environment()
        if ci_env == CIEnvironment.HOST:
            self.headers.update({'Lager-CI-Active': 'False'})
        else:
            self.headers.update({'Lager-CI-Active': 'True'})
            self.headers.update({'Lager-CI-System': ci_env.name})

        self.verify = verify
        if response_hook:
            self.hooks['response'].append(response_hook)

    def should_strip_auth(self, old_url, new_url):
        """
            Decide whether Authorization header should be removed when redirecting, allowing for
            forwarding auth to region-specific lager servers
        """
        old = urllib.parse.urlparse(old_url)
        new = urllib.parse.urlparse(new_url)
        if old.hostname.endswith('.lagerdata.com') and new.hostname.endswith('.lagerdata.com'):
            return False

        return super().should_strip_auth(old_url, new_url)

    def request(self, *args, **kwargs):
        """
            Catch connection errors so they can be handled more cleanly
        """

        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update({'Lager-Request-Id': str(uuid4())})

        try:
            return super().request(*args, **kwargs)
        except requests.exceptions.ConnectTimeout:
            click.secho('Connection to Lager API timed out', fg='red', err=True)
            click.get_current_context().exit(1)
        except requests.exceptions.ConnectionError:
            click.secho('Could not connect to Lager API', fg='red', err=True)
            click.get_current_context().exit(1)

    def chip_erase(self, gateway, device, interface, transport, speed):
        """
            Chip-erase the DUT
        """
        url = 'gateway/{}/chip-erase'.format(quote(gateway))
        data = {
            'device': device,
            'interface': interface,
            'transport': transport,
            'speed': speed,
        }
        return self.post(url, json=data)

    def start_debugger(self, gateway, files):
        """
            Start the debugger on the gateway
        """
        url = 'gateway/{}/start-debugger'.format(quote(gateway))
        return self.post(url, files=files)

    def debug_connect(self, gateway, mcu, force, ignore_if_connected, attach):
        """
            connect debugger by mcu
        """
        url = 'gateway/{}/debug-connect'.format(quote(gateway))
        return self.post(url, json={'mcu': mcu, 'force': force, 'ignore_if_connected': ignore_if_connected, 'attach': attach})

    def debug_disconnect(self, gateway, mcu):
        """
            disconnect debugger by mcu
        """
        url = 'gateway/{}/debug-disconnect'.format(quote(gateway))
        return self.post(url, json={'mcu': mcu})

    def debug_erase(self, gateway, mcu, address, length):
        """
            erase debugger by mcu
        """
        url = 'gateway/{}/debug-erase'.format(quote(gateway))
        return self.post(url, json={'mcu': mcu, 'address': address, 'length': length})

    def debug_read(self, gateway, mcu, address, length):
        """
            erase debugger by mcu
        """
        url = 'gateway/{}/debug-read'.format(quote(gateway))
        return self.post(url, json={'mcu': mcu, 'address': address, 'length': length})

    def debug_write(self, gateway, mcu, size, address, data):
        """
            erase debugger by mcu
        """
        url = 'gateway/{}/debug-write'.format(quote(gateway))
        return self.post(url, json={'size': size, 'mcu': mcu, 'address': address, 'data': data})

    def debug_reset(self, gateway, mcu, halt):
        """
            erase debugger by mcu
        """
        url = 'gateway/{}/debug-reset'.format(quote(gateway))
        return self.post(url, json={'mcu': mcu, 'halt': halt})

    def net_action(self, gateway, data):
        """
            Net action
        """
        url = 'gateway/{}/net/action'.format(quote(gateway))
        return self.post(url, json=data)

    def debug_flash(self, gateway, files):
        """
            flash debugger by mcu
        """
        url = 'gateway/{}/debug-flash'.format(quote(gateway))
        return self.post(url, files=files)

    def stop_debugger(self, gateway):
        """
            Stop the debugger on the gateway
        """
        url = 'gateway/{}/stop-debugger'.format(quote(gateway))
        return self.post(url)

    def erase_dut(self, gateway, addresses):
        """
            Erase DUT connected to gateway
        """
        url = 'gateway/{}/erase-duck'.format(quote(gateway))
        return self.post(url, json=addresses, stream=True)

    def flash_dut(self, gateway, files):
        """
            Flash DUT connected to gateway
        """
        url = 'gateway/{}/flash-duck'.format(quote(gateway))
        return self.post(url, files=files, stream=True)

    def run_python(self, gateway, files):
        """
            Run python on a gateway
        """
        url = 'gateway/{}/run-python'.format(quote(gateway))
        return self.post(url, files=files, stream=True)

    def run_pip(self, gateway, args):
        """
            Run python on a gateway
        """
        url = 'gateway/{}/run-pip'.format(quote(gateway))
        return self.post(url, json={'args': args}, stream=True)

    def kill_python(self, gateway, lager_process_id, sig=signal.SIGTERM):
        """
            Run python on a gateway
        """
        url = 'gateway/{}/kill-python'.format(quote(gateway))
        return self.post(url, json={'signal': sig, 'lager_process_id': lager_process_id})

    def gateway_hello(self, gateway):
        """
            Say hello to gateway to see if it is connected
        """
        url = 'gateway/{}/hello'.format(quote(gateway))
        return self.get(url)

    def serial_numbers(self, gateway, model):
        """
            Get serial numbers of devices attached to gateway
        """
        url = 'gateway/{}/serial-numbers'.format(quote(gateway))
        return self.get(url, params={'model': model})

    def serial_ports(self, gateway):
        """
            Get serial port devices attached to gateway
        """
        url = 'gateway/{}/serial-ports'.format(quote(gateway))
        return self.get(url)

    def gateway_status(self, gateway, mcu):
        """
            Get debugger status on gateway
        """
        url = 'gateway/{}/status'.format(quote(gateway))
        return self.get(url, params={'mcu': mcu})

    def list_gateways(self):
        """
            Get all gateways for logged-in user
        """
        url = 'gateway/list'
        return self.get(url)

    def reset_dut(self, gateway, halt, mcu):
        """
            Reset the DUT attached to a gateway and optionally halt it
        """
        url = 'gateway/{}/reset-duck'.format(quote(gateway))
        return self.post(url, json={'halt': halt, 'mcu': mcu})

    def run_dut(self, gateway):
        """
            Run the DUT attached to a gateway
        """
        url = 'gateway/{}/run-duck'.format(quote(gateway))
        return self.post(url, stream=True)

    def uart_gateway(self, gateway, serial_options, test_runner):
        """
            Open a connection to gateway serial port
        """
        url = 'gateway/{}/uart-duck'.format(quote(gateway))

        if test_runner == 'none':
            test_runner = None
        json_data = {
            'serial_options': serial_options,
            'test_runner': test_runner,
        }
        return self.post(url, json=json_data)

    def remote_debug(self, gateway, use_cache, archive, args):
        """
            Start a remote debugging session
        """
        url = 'gateway/{}/remote-debug'.format(quote(gateway))
        files = [
            ('args', json.dumps(args)),
        ]
        if not use_cache:
            files.append(
                ('archive', archive),
            )
        else:
            files.append(
                ('archive', ''),
            )

        try:
            return self.post(url, files=files)
        except ElfHashMismatch:
            files = [
                ('args', json.dumps(args)),
                ('archive', archive),
            ]
            print('retry')
            return self.post(url, files=files)

    def rename_gateway(self, gateway, new_name):
        """
            Rename a gateway
        """
        url = 'gateway/{}/rename'.format(quote(gateway))
        return self.post(url, json={'name': new_name})

    def gpio_set(self, gateway, gpio, type_, pull):
        """
            Set a GPIO pin to input or output
        """
        url = 'gateway/{}/gpio/set'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'type': type_, 'pull': pull})

    def gpio_input(self, gateway, gpio):
        """
            Read from the GPIO pin
        """
        url = 'gateway/{}/gpio/input'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio})

    def gpio_output(self, gateway, gpio, level):
        """
            Write to the GPIO pin
        """
        url = 'gateway/{}/gpio/output'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'level': level})

    def gpio_power(self, gateway, bus, level):
        """
            Set a bus enable pin to high or low
        """
        url = 'gateway/{}/gpio/power'.format(quote(gateway))
        return self.post(url, json={'bus': bus, 'level': level})

    def gpio_servo(self, gateway, gpio, pulsewidth, stop):
        """
            Control a servo with GPIO
        """
        url = 'gateway/{}/gpio/servo'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'pulsewidth': pulsewidth, 'stop': stop})

    def gpio_trigger(self, gateway, gpio, pulse_length, level):
        """
            Send a trigger pulse on GPIO
        """
        url = 'gateway/{}/gpio/trigger'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'pulse_length': pulse_length, 'level': level})

    def gpio_hardware_pwm(self, gateway, frequency, dutycycle):
        """
            Start hardware PWM on gpio
        """
        url = 'gateway/{}/gpio/hardware-pwm'.format(quote(gateway))
        return self.post(url, json={'frequency': frequency, 'dutycycle': dutycycle})

    def gpio_hardware_clock(self, gateway, frequency):
        """
            Start hardware clock on gpio
        """
        url = 'gateway/{}/gpio/hardware-clock'.format(quote(gateway))
        return self.post(url, json={'frequency': frequency})

    def get_wifi_state(self, gateway):
        """
            Get the connection state of the specified gateway
        """
        url = 'gateway/{}/wifi/state'.format(quote(gateway))
        return self.get(url)

    def get_wifi_access_points(self, gateway, interface):
        """
            Get access points visible to the specified gateway
        """
        url = 'gateway/{}/wifi/access-points'.format(quote(gateway))
        return self.get(url, params={'interface': interface})

    def connect_wifi(self, gateway, ssid, password, interface):
        """
            Connect the gateway to a wifi network
        """
        url = 'gateway/{}/wifi/connect'.format(quote(gateway))
        return self.post(url, json={'ssid': ssid, 'password': password, 'interface': interface})

    def delete_wifi_connection(self, gateway, ssid):
        """
            Delete the wifi connection for the specified gateway
        """
        url = 'gateway/{}/wifi/delete-connection'.format(quote(gateway))
        return self.post(url, json={'ssid': ssid})

    def can_up(self, gateway, bitrate, interfaces):
        """
            Bring up the CAN bus
        """
        url = 'gateway/{}/canbus/up'.format(quote(gateway))
        return self.post(url, json={'bitrate': bitrate, 'interfaces': interfaces})

    def can_down(self, gateway, interfaces):
        """
            Bring down the CAN bus
        """
        url = 'gateway/{}/canbus/down'.format(quote(gateway))
        return self.post(url, json={'interfaces': interfaces})

    def can_list(self, gateway):
        """
            List can buses
        """
        url = 'gateway/{}/canbus/list'.format(quote(gateway))
        return self.get(url)

    def can_send(self, gateway, interface, frames):
        """
            Send one or more frames on CAN bus
        """
        url = 'gateway/{}/canbus/send'.format(quote(gateway))
        frames = [frame._asdict() for frame in frames]
        return self.post(url, json={'interface': interface, 'frames': frames})

    def can_dump(self, gateway, interface, can_options):
        """
            Dump frames from CAN bus
        """
        url = 'gateway/{}/canbus/dump'.format(quote(gateway))
        return self.post(url, json={'interface': interface, 'can_options': can_options})

    def read_adc(self, gateway, channel, average_count, output):
        """
            Read the ADC
        """
        data = {
            'channel': channel,
            'average_count': average_count,
            'output': output
        }
        url = 'gateway/{}/adc/read'.format(quote(gateway))
        return self.post(url, json=data)

    def reboot_gateway(self, gateway):
        """
            Reboot gateway
        """
        url = 'gateway/{}/reboot'.format(quote(gateway))
        return self.post(url)

    def shutdown_gateway(self, gateway):
        """
            shutdown gateway
        """
        url = 'gateway/{}/poweroff'.format(quote(gateway))
        return self.post(url)

    def ble_scan(self, gateway, timeout):
        """
            scan for BLE devices
        """
        url = 'gateway/{}/ble/scan'.format(quote(gateway))
        return self.get(url, params={'timeout': timeout})

    def download_file(self, gateway, filename):
        """
            download a file from gateway
        """
        url = 'gateway/{}/download-file'.format(quote(gateway))
        return self.get(url, params={'filename': filename}, stream=True)

    def region(self, gateway):
        """
            get the region for the gateway
        """
        url = 'gateway/{}/region'.format(quote(gateway))
        region = self.get(url).json()['region']
        if region == DEFAULT_REGION:
            return None
        return region

    def start_dev_factory(self, gateway):
        """
            start a dev factory
        """
        url = 'gateway/{}/start-dev-factory'.format(quote(gateway))
        return self.post(url)

    def all_muxes(self, gateway):
        """
            get the muxes for the DUT
        """
        url = 'gateway/{}/all-muxes'.format(quote(gateway))
        return self.get(url)

    def usb_command(self, gateway, data):
        """
            run a USB command
        """
        url = 'gateway/{}/usb'.format(quote(gateway))
        return self.post(url, json=data)

    def get_ssh_info(self, gateway):
        """
            Fetch SSH info for the dut
        """
        url = 'gateway/{}/ssh-info'.format(quote(gateway))
        return self.get(url)

    def create_instrument(self, gateway, data):
        """
            Create an instrument
        """
        url = 'gateway/{}/create-instrument'.format(quote(gateway))
        return self.post(url, json=data)

    def list_instruments(self, gateway):
        """
            List instruments
        """
        url = 'gateway/{}/list-instruments'.format(quote(gateway))
        return self.get(url)
    
    def nets(self, gateway):
        """
            Return every net defined on the specified gateway.
        """
        url = 'gateway/{}/nets'.format(quote(gateway))
        return self.get(url)


class DirectHTTPSession:
    """
    Direct HTTP session to gateway over any network (VPN, local, etc.).

    Network-agnostic: Works with Tailscale, WireGuard, corporate VPN, local network, or any IP.
    Authorization: Network-level access (can you reach the IP via HTTP?)

    This bypasses the backend proxy for faster execution.
    """

    def __init__(self, gateway_ip):
        """
        Initialize direct HTTP session to gateway.

        Args:
            gateway_ip: IP address of gateway (Tailscale, VPN, local, or public IP)
        """
        self.gateway_ip = gateway_ip
        self.base_url = f'http://{gateway_ip}:5000'
        self.session = requests.Session()

        # Add version header
        self.session.headers.update({
            'Lager-Version': __version__,
            'Lager-Invocation-Id': str(uuid4()),
        })

    def run_python(self, gateway, files):
        """
        Run python on gateway via direct HTTP.

        Args:
            gateway: Gateway IP (ignored, uses self.gateway_ip)
            files: List of (name, content) tuples for multipart upload

        Returns:
            requests.Response object with streaming content
        """
        url = f'{self.base_url}/python'

        # Retry logic for multipart upload connection issues
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                # Disable keep-alive to prevent connection reuse issues with multipart uploads
                headers = {'Connection': 'close'}

                # Reset file positions if they are BytesIO objects
                for name, value in files:
                    if hasattr(value, 'seek') and hasattr(value, 'read'):
                        # It's a file-like object, reset position
                        value.seek(0)
                    elif isinstance(value, tuple) and len(value) >= 2:
                        # It's a tuple (filename, file_obj, ...), check the file object
                        if hasattr(value[1], 'seek'):
                            value[1].seek(0)

                response = self.session.post(
                    url,
                    files=files,
                    headers=headers,
                    stream=True,
                    timeout=(7, 320)  # Connect timeout: 7s, Read timeout: 320s
                )
                return response
            except requests.exceptions.ConnectionError as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Wait a bit before retrying
                    import time
                    time.sleep(0.5)
                    continue
                # Last attempt failed - exit cleanly without traceback
                click.secho(f'Could not connect to gateway at {self.gateway_ip}', fg='red', err=True)
                click.secho('Ensure the gateway is online and reachable via your network', fg='yellow', err=True)
                click.secho('(Tailscale, VPN, or local network connection required)', fg='yellow', err=True)
                import sys
                sys.exit(1)
            except requests.exceptions.Timeout:
                click.secho(f'Connection to gateway at {self.gateway_ip} timed out', fg='red', err=True)
                import sys
                sys.exit(1)

        # Should not reach here, but just in case
        if last_error:
            click.secho(f'Could not connect to gateway at {self.gateway_ip}', fg='red', err=True)
            import sys
            sys.exit(1)

    def kill_python(self, gateway, lager_process_id, sig=signal.SIGTERM):
        """
        Kill python process on gateway.

        Args:
            gateway: Gateway IP (ignored)
            lager_process_id: Process ID to kill
            sig: Signal to send (default SIGTERM)
        """
        url = f'{self.base_url}/python/kill'
        response = self.session.post(url, json={
            'lager_process_id': lager_process_id,
            'signal': int(sig)
        })
        response.raise_for_status()
        return response

    def gateway_hello(self, gateway):
        """Say hello to gateway to test connectivity"""
        url = f'{self.base_url}/hello'
        return self.session.get(url)

    def list_instruments(self, gateway):
        """List instruments configured on gateway"""
        url = f'{self.base_url}/instruments'
        return self.session.get(url)

    def nets(self, gateway):
        """List nets configured on gateway"""
        url = f'{self.base_url}/nets'
        return self.session.get(url)

    def download_file(self, gateway, filename):
        """
        Download a file from gateway via direct HTTP.

        Args:
            gateway: Gateway IP (ignored, uses self.gateway_ip)
            filename: Path to file on gateway to download

        Returns:
            requests.Response object with streaming content
        """
        url = f'{self.base_url}/download-file'
        return self.session.get(url, params={'filename': filename}, stream=True)


class LagerContext:  # pylint: disable=too-few-public-methods
    """
        Lager Context manager
    """
    def __init__(self, ctx, defaults, debug, style, interpreter=None):
        ws_host = os.getenv('LAGER_WS_HOST', _DEFAULT_WEBSOCKET_HOST)
        response_hook = functools.partial(LagerSession.handle_errors, ctx)
        self.session = LagerSession(response_hook=response_hook)
        self.session.max_redirects = 2
        self.defaults = defaults
        self.style = style
        self.ws_host = ws_host
        self.debug = debug
        self.interpreter = interpreter

    def get_session_for_gateway(self, gateway, dut_name=None):
        """
        Get appropriate session for gateway.

        Returns DirectHTTPSession for direct network connections (default).
        Set LAGER_USE_BACKEND=1 to use legacy backend proxy mode.

        Args:
            gateway: IP address of gateway
            dut_name: Optional DUT name (unused in direct HTTP mode)

        Returns:
            DirectHTTPSession (default) or LagerSession (if LAGER_USE_BACKEND=1)
        """
        # Check if user wants to force backend mode (for debugging/fallback)
        use_backend = os.getenv('LAGER_USE_BACKEND', '0') == '1'

        if use_backend:
            if self.debug:
                click.echo(f"[DEBUG] Using backend session (LAGER_USE_BACKEND=1)", err=True)
            return self.session  # LagerSession (backend proxy)

        # Use direct HTTP by default (network-agnostic: works with any VPN/network)
        if self.debug:
            click.echo(f"[DEBUG] Using direct HTTP to {gateway}", err=True)

        return DirectHTTPSession(gateway)

    @property
    def default_gateway(self):
        """
            Get default gateway id from config
        """
        return self.defaults.get('gateway_id')

    @default_gateway.setter
    def default_gateway(self, gateway_id):
        self.defaults['gateway_id'] = str(gateway_id)

    def websocket_connection_params(self, socktype, **kwargs):
        """
            Yields a websocket connection to the given path
        """
        if socktype == 'job':
            path = f'/ws/job/{kwargs["job_id"]}'
        elif socktype == 'jl-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/2331'
        elif socktype == 'gdb-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/3333'
        elif socktype == 'openocd-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/4444'
        elif socktype == 'rtt':
            port = kwargs.get('rtt_port', 9090)
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/{port}'
        elif socktype == 'webcam-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/8081'
        elif socktype == 'pdb':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/5555'
        elif socktype == 'pigpio-tunnel':
             path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/8888'
        elif socktype == 'grafana-tunnel':
             path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/3000'
        else:
            raise ValueError(f'Invalid websocket type: {socktype}')

        if kwargs.get('region') and 'dev.lagerdata.app' not in self.ws_host:
            ws_host = f'wss://{kwargs["region"]}-elb.app.lagerdata.com'
        else:
            ws_host = self.ws_host
        uri = urllib.parse.urljoin(ws_host, path)

        headers = []
        ctx = get_ssl_context()

        return (uri, dict(extra_headers=headers, ssl_context=ctx))

def get_default_gateway(ctx):
    """
        Check for a default gateway in config.
        Also checks if the gateway name is a local DUT and resolves it to an IP address.
    """
    import ipaddress
    from .dut_storage import get_dut_ip, list_duts

    name = os.getenv('LAGER_GATEWAY')
    if name is None:
        name = ctx.obj.default_gateway

    if name is None:
        # No DUT specified - provide helpful error
        local_duts = list_duts()

        click.secho('No DUT specified and no default DUT configured.', fg='red', err=True)
        click.echo()

        if local_duts:
            click.echo('Available local DUTs:')
            for dut_name in sorted(local_duts.keys()):
                click.echo(f'  - {dut_name}')
            click.echo()
            click.echo('You can either:')
            click.echo('  1. Specify a box with: --box <name>')
            click.echo('  2. Set a default box with: lager defaults add --box <name>')
        else:
            click.echo('No local DUTs found in .lager file.')
            click.echo()
            click.echo('To add a DUT, run:')
            click.echo('  lager duts add --name <name> --ip <ip-address>')
            click.echo()
            click.echo('Then you can either:')
            click.echo('  1. Specify a box with: --box <name>')
            click.echo('  2. Set a default box with: lager defaults add --box <name>')

        ctx.exit(1)

    # Check if the gateway name is actually a local DUT that should be resolved to an IP
    local_ip = get_dut_ip(name)
    if local_ip:
        return local_ip

    # Check if it's a valid IP address
    try:
        ipaddress.ip_address(name)
        # It's a valid IP address, use it directly
        return name
    except ValueError:
        # Not a valid IP and not in local DUTs - Show helpful error
        click.secho(f"Error: DUT '{name}' not found.", fg='red', err=True)
        click.echo("", err=True)

        saved_duts = list_duts()
        if saved_duts:
            click.echo("Available DUTs:", err=True)
            for dut_name, dut_info in saved_duts.items():
                if isinstance(dut_info, dict):
                    dut_ip = dut_info.get('ip', 'unknown')
                else:
                    dut_ip = dut_info
                click.echo(f"  - {dut_name} ({dut_ip})", err=True)
        else:
            click.echo("No DUTs are currently saved.", err=True)

        click.echo("", err=True)
        click.echo("To add a new DUT, use:", err=True)
        click.echo(f"  lager duts add --name {name} --ip <IP_ADDRESS>", err=True)
        ctx.exit(1)

def get_ssl_context():
    """
        Get an SSL context, with custom CA cert if necessary
    """
    cafile_path = os.getenv('LAGER_CAFILE_PATH')
    if not cafile_path:
        # Use default system CA certs
        return None
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cafile=cafile_path)
    return ctx

def ensure_debugger_running(gateway, ctx, mcu=None):
    """
        Ensure debugger is running on a given gateway
    """
    session = ctx.obj.session
    gateway_status = session.gateway_status(gateway, mcu).json()
    if not gateway_status['running']:
        click.secho('Gateway debugger is not running. Please use `lager connect` to run it', fg='red', err=True)
        ctx.exit(1)
    return gateway_status

class CIEnvironment(Enum):
    """
        Enum representing supported CI systems
    """
    HOST = 'host'
    DRONE = 'drone'
    GITHUB = 'github'
    BITBUCKET = 'bitbucket'
    GITLAB = 'gitlab'
    GENERIC_CI = 'ci'
    JENKINS = 'jenkins'

_CONTAINER_CI = set((
    CIEnvironment.DRONE,
    CIEnvironment.GITHUB,
    CIEnvironment.BITBUCKET,
    CIEnvironment.GITLAB,
))

def is_container_ci(ci_env):
    """
        Supported container-based CI solutions
    """
    return ci_env in _CONTAINER_CI

def get_ci_environment():
    """
        Determine whether we are running in CI or not
    """
    if os.getenv('LAGER_CI_OVERRIDE'):
        return CIEnvironment.HOST

    if os.getenv('CI') == 'true':
        if os.getenv('DRONE') == 'true':
            return CIEnvironment.DRONE
        if os.getenv('GITHUB_RUN_ID'):
            return CIEnvironment.GITHUB
        if os.getenv('BITBUCKET_BUILD_NUMBER'):
            return CIEnvironment.BITBUCKET
        if 'gitlab' in os.getenv('CI_SERVER_NAME', '').lower():
            return CIEnvironment.GITLAB
        if 'jenkins' in os.getenv('BUILD_TAG', '').lower():
            return CIEnvironment.JENKINS
        return CIEnvironment.GENERIC_CI

    return CIEnvironment.HOST

def get_impl_path(filename):
    base = os.path.dirname(__file__)
    return os.path.join(base, 'impl', filename)


def get_default_net(ctx, net_type):
    """
    Get the default net name for a specific net type from config.

    Args:
        ctx: Click context
        net_type: Type of net (e.g., 'power_supply', 'battery', 'scope', etc.)

    Returns:
        Default net name if configured, None otherwise
    """
    from .config import read_config_file

    config_key = f'net_{net_type}'
    config = read_config_file()

    if config.has_option('LAGER', config_key):
        return config.get('LAGER', config_key)

    return None


