"""
    lager.pip.commands

    Commands for managing pip packages in lager python container
"""
import sys
import os
import re
import click
from ..context import get_default_gateway
from ..python.commands import run_python_internal

def _normalize_package_name(pkg):
    """Normalize package name for comparison (remove version specifiers)"""
    # Extract package name before version specifier
    match = re.match(r'^([a-zA-Z0-9\-_\.]+)', pkg)
    if match:
        return match.group(1).lower().replace('_', '-')
    return pkg.lower()

def _read_remote_requirements(ctx, dut):
    """Read user requirements from remote gateway via HTTP"""
    import json
    from io import StringIO

    try:
        # Use run_python_internal to read the file via HTTP
        # Create a simple Python script to read the file
        script_content = """
import os
import json

requirements_file = '/home/www-data/gateway/python/docker/user_requirements.txt'

if os.path.exists(requirements_file):
    with open(requirements_file, 'r') as f:
        content = f.read()
    packages = []
    for line in content.splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if line and not line.startswith('#'):
            packages.append(line)
    print(json.dumps({'packages': packages}))
else:
    print(json.dumps({'packages': []}))
"""

        # Write script to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(script_content)
            temp_script = f.name

        try:
            # Capture output
            output_buffer = StringIO()

            # Run the script
            run_python_internal(
                ctx,
                temp_script,
                dut,
                env_vars=[],
                args=[],
                output_stream=output_buffer
            )

            # Parse the output
            output = output_buffer.getvalue()
            result = json.loads(output.strip())
            return result['packages']

        finally:
            # Clean up temp file
            os.unlink(temp_script)

    except Exception as e:
        click.secho(f'Error: Failed to read requirements from gateway: {e}', fg='red', err=True)
        sys.exit(1)

def _write_remote_requirements(ctx, dut, packages):
    """Write packages to remote gateway user requirements file via HTTP"""
    import json
    import tempfile
    from io import StringIO

    try:
        # Create the file content
        content = '# User-installed packages via lager pip\n'
        content += '# This file is managed by lager pip install/uninstall commands\n'
        content += '# Add your custom packages below (one per line with optional version specifier)\n'
        content += '#\n'
        content += '# Examples:\n'
        content += '#   pandas==2.0.0\n'
        content += '#   numpy\n'
        content += '#   scipy>=1.10.0\n'
        content += '\n'
        for pkg in sorted(packages):
            content += f'{pkg}\n'

        # Create a Python script to write the file
        script_content = f"""
import os
import json

requirements_file = '/home/www-data/gateway/python/docker/user_requirements.txt'
content = {json.dumps(content)}

# Ensure directory exists
os.makedirs(os.path.dirname(requirements_file), exist_ok=True)

# Write the file
with open(requirements_file, 'w') as f:
    f.write(content)

print(json.dumps({{'status': 'success'}}))
"""

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(script_content)
            temp_script = f.name

        try:
            # Capture output
            output_buffer = StringIO()

            # Run the script
            run_python_internal(
                ctx,
                temp_script,
                dut,
                env_vars=[],
                args=[],
                output_stream=output_buffer
            )

            # Verify success
            output = output_buffer.getvalue()
            result = json.loads(output.strip())
            if result.get('status') != 'success':
                raise Exception('Failed to write requirements file')

        finally:
            # Clean up temp file
            os.unlink(temp_script)

    except Exception as e:
        click.secho(f'Error: Failed to write requirements to gateway: {e}', fg='red', err=True)
        sys.exit(1)

def _validate_packages(packages):
    """Validate that packages exist on PyPI before attempting installation"""
    import urllib.request
    import json

    invalid_packages = []

    for pkg in packages:
        # Extract package name (remove version specifiers)
        pkg_name = _normalize_package_name(pkg)

        try:
            # Check if package exists on PyPI
            url = f'https://pypi.org/pypi/{pkg_name}/json'
            req = urllib.request.Request(url, headers={'User-Agent': 'lager-cli'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    invalid_packages.append(pkg)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                invalid_packages.append(pkg)
        except Exception:
            # Network error or timeout - skip validation for this package
            pass

    return invalid_packages

def _rebuild_python_container(ctx, dut):
    """Rebuild and restart the python container on the gateway via HTTP"""
    import json
    import tempfile
    from io import StringIO

    click.secho('\nRebuilding python container...', fg='blue')

    try:
        # Create a Python script to rebuild the container
        script_content = """
import subprocess
import json

try:
    # Stop existing containers
    print('Stopping existing containers...', flush=True)
    subprocess.run(
        ['docker', 'stop', 'python', 'controller'],
        capture_output=True,
        timeout=60
    )
    subprocess.run(
        ['docker', 'rm', 'python', 'controller'],
        capture_output=True,
        timeout=60
    )

    # Rebuild python container
    print('Rebuilding python container (no cache)...', flush=True)
    print('This may take 3-5 minutes...', flush=True)
    result = subprocess.run(
        ['docker', 'build', '--no-cache', '-f', '/home/www-data/gateway/python/docker/gatewaypy3.Dockerfile', '-t', 'python', '/home/www-data/gateway/python'],
        capture_output=False,
        timeout=600
    )
    if result.returncode != 0:
        print(json.dumps({'status': 'error', 'message': 'Docker build failed'}))
        exit(1)

    # Start containers
    print('Starting containers...', flush=True)
    result = subprocess.run(
        ['bash', '/home/www-data/gateway/start_all_containers.sh'],
        capture_output=True,
        timeout=300,
        text=True
    )
    if result.returncode != 0:
        # Try alternate location
        result = subprocess.run(
            ['bash', '/home/www-data/gateway/gateway/start_all_containers.sh'],
            capture_output=True,
            timeout=300,
            text=True
        )

    if result.returncode == 0:
        print(json.dumps({'status': 'success'}))
    else:
        print(json.dumps({'status': 'error', 'message': 'Failed to start containers'}))
        exit(1)

except subprocess.TimeoutExpired:
    print(json.dumps({'status': 'error', 'message': 'Operation timed out'}))
    exit(1)
except Exception as e:
    print(json.dumps({'status': 'error', 'message': str(e)}))
    exit(1)
"""

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(script_content)
            temp_script = f.name

        try:
            # Run the script and stream output to user
            run_python_internal(
                ctx,
                temp_script,
                dut,
                env_vars=[],
                args=[]
            )

            click.secho('\n✓ Container rebuilt successfully!', fg='green')
            return True

        finally:
            # Clean up temp file
            os.unlink(temp_script)

    except Exception as e:
        click.secho(f'\n✗ Failed to rebuild container: {e}', fg='red', err=True)
        return False

@click.group()
def pip():
    """Manage pip packages in the python container"""
    pass

@pip.command()
@click.pass_context
@click.option("--box", 'box', required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt and rebuild immediately')
@click.argument('packages', nargs=-1, required=True)
def install(ctx, box, dut, yes, packages):
    """Install packages permanently into the python container

    This command adds packages to the gateway's package list and rebuilds the container.
    Packages will persist across container restarts.

    Examples:
        lager pip install pandas
        lager pip install numpy==1.24.0
        lager pip install scipy matplotlib
    """
    from ..dut_storage import resolve_and_validate_dut

    # Determine target DUT (box takes precedence over dut)
    box_name = box or dut

    # Resolve and validate the box/dut name
    target = resolve_and_validate_dut(ctx, box_name)

    # Read current requirements from gateway
    current_packages = _read_remote_requirements(ctx, target)
    current_names = {_normalize_package_name(pkg) for pkg in current_packages}

    # Add new packages (avoid duplicates)
    new_packages = []
    for pkg in packages:
        pkg_name = _normalize_package_name(pkg)
        if pkg_name not in current_names:
            new_packages.append(pkg)
            current_packages.append(pkg)
            current_names.add(pkg_name)
            click.secho(f'Adding {pkg} to package list', fg='green')
        else:
            click.secho(f'Package {pkg} already in package list', fg='yellow')

    if not new_packages:
        click.secho('No new packages to install', fg='yellow')
        return

    # Validate packages exist on PyPI before modifying files
    click.secho('\nValidating packages on PyPI...', fg='blue')
    invalid_packages = _validate_packages(new_packages)

    if invalid_packages:
        click.secho('\n✗ Error: The following packages do not exist on PyPI:', fg='red', err=True)
        for pkg in invalid_packages:
            click.secho(f'  - {pkg}', fg='red', err=True)
        click.secho('\nNo changes were made. Please check package names and try again.', fg='yellow', err=True)
        sys.exit(1)

    click.secho('✓ All packages validated', fg='green')

    # Write updated requirements to gateway
    _write_remote_requirements(ctx, target, current_packages)

    click.secho('\nPackages added successfully', fg='green')

    # Prompt user to rebuild container (skip prompt if --yes flag)
    if yes or click.confirm('\nRebuild and restart the python container now?', default=False):
        if _rebuild_python_container(ctx, target):
            click.secho('Packages are now available.', fg='green')
        else:
            click.secho(f'To apply changes, run:', fg='yellow')
            click.secho(f'  lager pip apply --box {target}', fg='yellow')
    else:
        click.secho('\nTo apply changes later, run:', fg='blue')
        click.secho(f'  lager pip apply --box {target}', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def list(ctx, box, dut):
    """List user-installed packages

    Shows packages that have been installed via 'lager pip install'.
    These packages persist across container restarts.
    """
    from ..dut_storage import resolve_and_validate_dut

    # Determine target DUT (box takes precedence over dut)
    box_name = box or dut

    # Resolve and validate the box/dut name
    target = resolve_and_validate_dut(ctx, box_name)

    # Read packages from gateway
    packages = _read_remote_requirements(ctx, target)

    if not packages:
        click.secho('No user-installed packages found', fg='yellow')
        click.secho('\nTo install packages permanently:', fg='blue')
        click.secho('  lager pip install <package-name>', fg='blue')
        return

    click.secho('User-installed packages:', fg='green')
    for pkg in packages:
        click.echo(f'  {pkg}')

    click.secho(f'\nTotal: {len(packages)} package(s)', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt and rebuild immediately')
@click.argument('packages', nargs=-1, required=True)
def uninstall(ctx, box, dut, yes, packages):
    """Uninstall packages from the python container

    Removes packages that were installed via 'lager pip install'.
    Changes will take effect after container rebuild.

    Examples:
        lager pip uninstall pandas
        lager pip uninstall numpy scipy
    """
    from ..dut_storage import resolve_and_validate_dut

    # Determine target DUT (box takes precedence over dut)
    box_name = box or dut

    # Resolve and validate the box/dut name
    target = resolve_and_validate_dut(ctx, box_name)

    # Read current requirements from gateway
    current_packages = _read_remote_requirements(ctx, target)

    if not current_packages:
        click.secho('No user-installed packages found', fg='yellow')
        return

    # Normalize package names for removal
    packages_to_remove = {_normalize_package_name(pkg) for pkg in packages}

    # Filter out packages to remove
    removed = []
    remaining = []
    for pkg in current_packages:
        pkg_name = _normalize_package_name(pkg)
        if pkg_name in packages_to_remove:
            removed.append(pkg)
            click.secho(f'Removing {pkg} from package list', fg='green')
        else:
            remaining.append(pkg)

    if not removed:
        click.secho('No matching packages found in package list', fg='yellow')
        return

    # Write updated requirements to gateway
    _write_remote_requirements(ctx, target, remaining)

    click.secho(f'\nRemoved {len(removed)} package(s) from package list', fg='green')

    # Prompt user to rebuild container (skip prompt if --yes flag)
    if yes or click.confirm('\nRebuild and restart the python container now?', default=False):
        if _rebuild_python_container(ctx, target):
            click.secho('Packages have been removed.', fg='green')
        else:
            click.secho(f'To apply changes, run:', fg='yellow')
            click.secho(f'  lager pip apply --box {target}', fg='yellow')
    else:
        click.secho('\nTo apply changes later, run:', fg='blue')
        click.secho(f'  lager pip apply --box {target}', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
def apply(ctx, box, dut, yes):
    """Apply package changes by rebuilding the python container

    Use this command to rebuild the container after adding/removing packages
    with 'lager pip install' or 'lager pip uninstall' when you chose not to
    rebuild immediately.

    Examples:
        lager pip apply --box TEST-2
        lager pip apply --box TEST-2 --yes
    """
    from ..dut_storage import resolve_and_validate_dut

    # Determine target DUT (box takes precedence over dut)
    box_name = box or dut

    # Resolve and validate the box/dut name
    target = resolve_and_validate_dut(ctx, box_name)

    # Read current packages to show what will be applied
    packages = _read_remote_requirements(ctx, target)

    if packages:
        click.secho(f'Current package list ({len(packages)} package(s)):', fg='blue')
        for pkg in packages:
            click.echo(f'  {pkg}')
    else:
        click.secho('No packages in package list', fg='yellow')

    # Confirm rebuild unless --yes flag is used
    if not yes:
        if not click.confirm('\nRebuild and restart the python container now?', default=True):
            click.secho('Rebuild cancelled', fg='yellow')
            return

    # Rebuild container
    if _rebuild_python_container(ctx, target):
        if packages:
            click.secho('Packages are now available.', fg='green')
        else:
            click.secho('Container rebuilt with no user packages.', fg='green')
    else:
        click.secho('Container rebuild failed', fg='red', err=True)
        sys.exit(1)

