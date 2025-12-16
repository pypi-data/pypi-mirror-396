import click
import subprocess
from ..dut_storage import list_duts


@click.group()
def logs():
    """Manage gateway logs"""
    pass


@logs.command('clean')
@click.option('--box', required=True, help='Gateway to clean logs on')
@click.option('--older-than', default=1, type=int, help='Remove logs older than N days (default: 1)')
@click.option('--yes', is_flag=True, help='Skip confirmation')
def clean(box, older_than, yes):
    """Clean old log files from gateway

    Removes log files older than specified days to free up space and prevent
    upload errors caused by large log files.

    Examples:
        lager logs clean --box TEST-3 --yes
        lager logs clean --box TEST-4 --older-than 7
    """
    # Resolve box to IP
    saved_duts = list_duts()
    if box not in saved_duts:
        click.secho(f"Error: Box '{box}' not found", fg='red', err=True)
        click.echo("Available boxes:")
        for name in sorted(saved_duts.keys()):
            click.echo(f"  - {name}")
        return

    dut_info = saved_duts[box]
    if isinstance(dut_info, dict):
        ip = dut_info.get('ip', 'unknown')
    else:
        ip = dut_info

    if not yes:
        click.confirm(f"Clean logs older than {older_than} day(s) on {box} ({ip})?", abort=True)

    # Build command to remove old logs
    # Note: -mtime +N means "modified more than N days ago"
    cmd = f'find ~/gateway/logs -name "*.log" -type f -mtime +{older_than} -delete 2>/dev/null || true'

    click.echo(f'Cleaning logs on {box}...', nl=False)
    result = subprocess.run(
        ['ssh', f'lagerdata@{ip}', cmd],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        click.secho(' OK', fg='green')

        # Show how much space was freed
        size_cmd = 'du -sh ~/gateway/logs/ 2>/dev/null || echo "0"'
        result = subprocess.run(
            ['ssh', f'lagerdata@{ip}', size_cmd],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            size = result.stdout.strip().split()[0] if result.stdout.strip() else "0"
            click.echo(f'Current logs size: {size}')
    else:
        click.secho(' FAILED', fg='red')
        if result.stderr:
            click.echo(result.stderr, err=True)


@logs.command('size')
@click.option('--box', help='Gateway to check (if not specified, checks all)')
@click.option('--verbose', '-v', is_flag=True, help='Show individual log files')
def size(box, verbose):
    """Check log file sizes on gateway(s)

    Shows total size of logs directory and optionally individual log files.
    Useful for diagnosing which gateways need log cleanup.

    Examples:
        lager logs size                    # Check all gateways
        lager logs size --box TEST-3       # Check specific gateway
        lager logs size --box TEST-4 -v    # Show individual files
    """
    saved_duts = list_duts()

    # Filter to specific box if requested
    if box:
        if box not in saved_duts:
            click.secho(f"Error: Box '{box}' not found", fg='red', err=True)
            return
        boxes_to_check = {box: saved_duts[box]}
    else:
        boxes_to_check = saved_duts

    # Check each box
    for name, dut_info in sorted(boxes_to_check.items()):
        if isinstance(dut_info, dict):
            ip = dut_info.get('ip', 'unknown')
        else:
            ip = dut_info

        click.echo(f'\n{name} ({ip}):')

        # Get total size
        size_cmd = 'du -sh ~/gateway/logs/ 2>/dev/null || echo "0\t(not found)"'
        result = subprocess.run(
            ['ssh', f'lagerdata@{ip}', size_cmd],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            size_output = result.stdout.strip()
            if size_output:
                size, path = size_output.split('\t', 1)
                click.echo(f'  Total logs: {size}')

                # Parse size and warn if too large
                size_str = size.strip()
                if size_str.endswith('M'):
                    size_mb = float(size_str[:-1])
                    if size_mb > 500:
                        click.secho(f'  ⚠ Warning: Logs are large, consider cleaning', fg='yellow')
                elif size_str.endswith('G'):
                    click.secho(f'  ⚠ ERROR: Logs are very large! Clean immediately:', fg='red')
                    click.echo(f'    lager logs clean --box {name} --yes')
            else:
                click.echo('  Total logs: 0')

            # Show individual files if verbose
            if verbose:
                files_cmd = 'find ~/gateway/logs -name "*.log" -type f -exec ls -lh {} \\; 2>/dev/null | awk \'{print "    " $9 ": " $5}\''
                result = subprocess.run(
                    ['ssh', f'lagerdata@{ip}', files_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    click.echo('  Individual files:')
                    click.echo(result.stdout.strip())
        else:
            click.secho(f'  Connection failed', fg='red')


@logs.command('docker')
@click.option('--box', required=True, help='Gateway to check')
@click.option('--container', help='Specific container name (default: all containers)')
def docker_logs(box, container):
    """Check Docker container log sizes

    Shows size of Docker container logs which can grow large over time.
    These are separate from application logs and are managed by Docker.

    Examples:
        lager logs docker --box TEST-3
        lager logs docker --box TEST-4 --container lager
    """
    # Resolve box to IP
    saved_duts = list_duts()
    if box not in saved_duts:
        click.secho(f"Error: Box '{box}' not found", fg='red', err=True)
        return

    dut_info = saved_duts[box]
    if isinstance(dut_info, dict):
        ip = dut_info.get('ip', 'unknown')
    else:
        ip = dut_info

    click.echo(f'Docker logs on {box} ({ip}):\n')

    # Get container logs info
    if container:
        cmd = f'docker inspect {container} --format="{{{{.LogPath}}}}" 2>/dev/null | xargs -I{{}} sudo ls -lh "{{}}" 2>/dev/null | awk \'{{print $5 " " $9}}\''
    else:
        cmd = 'for c in $(docker ps --format "{{.Names}}"); do echo "Container: $c"; docker inspect $c --format="{{.LogPath}}" 2>/dev/null | xargs -I{} sudo ls -lh "{}" 2>/dev/null | awk \'{print "  Size: " $5 " Path: " $9}\'; done'

    result = subprocess.run(
        ['ssh', f'lagerdata@{ip}', cmd],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        if result.stdout.strip():
            click.echo(result.stdout.strip())
            click.echo('\nNote: Docker logs are automatically rotated with max-size=10m, max-file=3')
            click.echo('Total maximum per container: ~30MB')
        else:
            click.echo('No containers found or no logs')
    else:
        click.secho('Failed to check Docker logs', fg='red')
        if result.stderr:
            click.echo(result.stderr, err=True)
