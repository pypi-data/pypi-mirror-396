"""
    lager.ssh.commands

    SSH into DUTs
"""
import click
import subprocess
import sys
from ..dut_storage import resolve_and_validate_dut
from ..context import get_default_gateway


@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def ssh(ctx, box, dut):
    """
        SSH into a DUT
    """
    # Use box or dut (box takes precedence)
    dut = box or dut

    from ..dut_storage import get_dut_user

    # Use default gateway if no DUT specified
    if not dut:
        dut = get_default_gateway(ctx)

    # Resolve and validate the DUT (handles both names and IPs)
    resolved_dut = resolve_and_validate_dut(ctx, dut)

    # Get username from DUT storage (defaults to 'lagerdata' if not found)
    username = get_dut_user(dut) or 'lagerdata'

    # Build SSH command
    ssh_host = f'{username}@{resolved_dut}'

    try:
        # Use subprocess to execute SSH interactively
        # We use os.execvp to replace the current process with SSH
        # This allows full interactivity (shell, etc.)
        import os
        os.execvp('ssh', ['ssh', ssh_host])
    except FileNotFoundError:
        click.secho('Error: SSH client not found. Please ensure SSH is installed.', fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f'Error connecting to {ssh_host}: {str(e)}', fg='red', err=True)
        ctx.exit(1)
