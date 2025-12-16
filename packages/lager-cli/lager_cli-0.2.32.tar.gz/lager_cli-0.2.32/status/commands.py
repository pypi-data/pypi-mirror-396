"""
status_commands.py – "lager status …" CLI group
-------------------------------------------
Status monitoring TUI and GUI commands.
"""

from __future__ import annotations

import time
from typing import Dict, Any, Optional

import click
import requests
import shutil
from texttable import Texttable

from .status_tui import launch_status_tui
from ..dut_storage import list_duts, get_dut_ip
from ..net_storage import load_nets
# GUI import moved to function to avoid tkinter import on every CLI command


def _check_dut_connectivity(dut_ip: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Check if a DUT is online and responsive.

    Args:
        dut_ip: IP address of the DUT
        timeout: Request timeout in seconds

    Returns:
        Dict with status, response_time, and error info
    """
    import subprocess
    import ipaddress

    # First check if this is an IP address
    try:
        ipaddress.ip_address(dut_ip)
        is_ip = True
    except ValueError:
        is_ip = False

    if is_ip:
        # For direct IP connections (like Tailscale), use ping like the hello command
        try:
            start_time = time.time()
            result = subprocess.run([
                'ping', '-c', '3', '-W', '2000', dut_ip
            ], capture_output=True, text=True, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            if result.returncode == 0:
                return {
                    "status": "Online",
                    "response_time": response_time,
                    "error": None
                }
            else:
                return {
                    "status": "Offline",
                    "response_time": response_time,
                    "error": "Ping failed"
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "Offline",
                "response_time": timeout * 1000,
                "error": "Ping timeout"
            }
        except Exception as e:
            return {
                "status": "Error",
                "response_time": 0,
                "error": str(e)
            }
    else:
        # For gateway IDs, try the HTTP API
        try:
            start_time = time.time()
            # Try a simple HTTP request to the gateway health endpoint
            response = requests.get(f"http://{dut_ip}:8000/health", timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            if response.status_code == 200:
                return {
                    "status": "Online",
                    "response_time": response_time,
                    "error": None
                }
            else:
                return {
                    "status": "Error",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}"
                }
        except requests.exceptions.Timeout:
            return {
                "status": "Offline",
                "response_time": timeout * 1000,
                "error": "Timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "Offline",
                "response_time": 0,
                "error": "Connection refused"
            }
        except Exception as e:
            return {
                "status": "Error",
                "response_time": 0,
                "error": str(e)
            }


def _get_dut_nets(ctx: click.Context, dut_name: str) -> Dict[str, Any]:
    """
    Get nets information for a specific DUT from local storage.

    Args:
        ctx: Click context (unused, kept for compatibility)
        dut_name: Name of the DUT

    Returns:
        Dict with nets list and count
    """
    try:
        nets = load_nets(dut_name)
        return {
            "nets": nets,
            "count": len(nets),
            "error": None
        }
    except Exception as e:
        return {"nets": [], "count": 0, "error": str(e)}


def _format_status_table(dut_data: Dict[str, Dict[str, Any]]) -> None:
    """
    Display a formatted table of DUT status information.

    Args:
        dut_data: Dictionary mapping DUT names to their status info
    """
    if not dut_data:
        click.echo("No DUTs found in .lager file. Add one with: lager duts add --name <NAME> --ip <IP>")
        return

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 't', 't', 't', 't'])
    table.set_cols_align(["l", "l", "r", "l", "r", "t"])

    # Calculate column widths
    term_width = shutil.get_terminal_size((120, 24)).columns
    col_widths = [12, 10, 15, 15, 6, max(20, term_width - 70)]
    table.set_cols_width(col_widths)

    table.add_row(['DUT Name', 'Status', 'Response (ms)', 'IP Address', 'Nets', 'Last Error'])

    for dut_name, data in sorted(dut_data.items()):
        conn_info = data['connectivity']
        nets_info = data['nets']

        # Format response time
        response_str = f"{conn_info['response_time']:.1f}" if conn_info['response_time'] > 0 else "-"

        # Format error (truncate if too long)
        error_str = conn_info['error'] or ""
        if len(error_str) > col_widths[5]:
            error_str = error_str[:col_widths[5]-3] + "..."

        table.add_row([
            dut_name,
            conn_info['status'],
            response_str,
            data['ip'],
            str(nets_info['count']),
            error_str
        ])

    # Color-code status in output
    table_output = table.draw()
    # Display with colors based on status
    for line in table_output.split('\n'):
        if 'Online' in line:
            click.secho(line, fg='green')
        elif 'Offline' in line or 'Error' in line:
            click.secho(line, fg='red')
        else:
            click.echo(line)


def _display_dut_details(dut_name: str, dut_ip: str, dut_data: Dict[str, Any]) -> None:
    """
    Display detailed information for a specific DUT.

    Args:
        dut_name: Name of the DUT
        dut_ip: IP address of the DUT
        dut_data: Status and nets data for the DUT
    """
    conn_info = dut_data['connectivity']
    nets_info = dut_data['nets']

    click.echo(f"\nDUT Status: {dut_name}")
    click.echo("=" * (len(dut_name) + 12))

    # Connectivity information
    click.echo(f"IP Address: {dut_ip}")
    status_color = 'green' if conn_info['status'] == 'Online' else 'red'
    click.secho(f"Status: {conn_info['status']}", fg=status_color)

    if conn_info['response_time'] > 0:
        click.echo(f"Response Time: {conn_info['response_time']:.1f} ms")

    if conn_info['error']:
        click.secho(f"Error: {conn_info['error']}", fg='red')

    # Nets information
    click.echo(f"\nActive Nets: {nets_info['count']}")

    if nets_info['error']:
        click.secho(f"Nets Error: {nets_info['error']}", fg='red')
    elif nets_info['nets']:
        click.echo()
        _display_nets_table(nets_info['nets'])
    elif nets_info['count'] == 0:
        click.echo("No nets configured on this DUT.")


def _display_nets_table(nets: list) -> None:
    """
    Display a formatted table of nets (reusing logic from nets command).

    Args:
        nets: List of net dictionaries
    """
    if not nets:
        return

    # Calculate terminal width for responsive layout
    term_w = shutil.get_terminal_size((120, 24)).columns

    # Prepare data
    headers = ["Name", "Type", "Instrument", "Channel", "Address"]
    rows = [
        [
            net.get("name", ""),
            net.get("role", ""),
            net.get("instrument", "") or "",
            net.get("pin", "") or "",
            net.get("address", "") or "",
        ]
        for net in nets
    ]

    # Calculate column widths
    min_widths = [8, 10, 14, 7, 20]
    col_widths = [
        max(min_widths[i], max(len(str(r[i])) for r in rows + [headers]))
        for i in range(len(min_widths))
    ]

    # Adjust address column to fit terminal
    used_width = sum(col_widths[:-1]) + 4 * 2  # padding
    remaining_width = max(20, term_w - used_width - 2)
    col_widths[-1] = remaining_width

    # Format and display
    def format_row(row):
        return (
            f"{row[0]:<{col_widths[0]}}  "
            f"{row[1]:<{col_widths[1]}}  "
            f"{row[2]:<{col_widths[2]}}  "
            f"{row[3]:<{col_widths[3]}}  "
            f"{row[4]:<{col_widths[4]}}"
        )

    click.secho(format_row(headers), fg='green')
    click.echo("-" * sum(col_widths) + "-" * 8)  # separator
    for row in rows:
        click.secho(format_row(row), fg='green')


@click.group(
    name="status",
    invoke_without_command=True,
    help="Show box status and connectivity",
)
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.pass_context
def status(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """
    Show box status and connectivity information
    """
    # Resolve box/dut (box takes precedence, dut is for backward compatibility)
    resolved = box or dut

    if ctx.invoked_subcommand is None:
        if resolved:
            _show_dut_status(ctx, resolved)
        else:
            _show_all_duts_status(ctx)


def _show_all_duts_status(ctx: click.Context) -> None:
    """Show status overview for all configured DUTs."""
    duts = list_duts()

    if not duts:
        click.echo("No DUTs found in .lager file. Add one with: lager duts add --name <NAME> --ip <IP>")
        return

    click.echo("Checking DUT connectivity...")

    dut_data = {}
    for dut_name, dut_info in duts.items():
        # Handle both string (IP only) and dict formats
        if isinstance(dut_info, dict):
            dut_ip = dut_info.get('ip', dut_info.get('address', 'unknown'))
        else:
            dut_ip = dut_info

        if dut_ip == 'unknown':
            continue

        # Check connectivity
        connectivity = _check_dut_connectivity(dut_ip)

        # Get nets info from local storage (regardless of connectivity)
        nets_info = _get_dut_nets(ctx, dut_name)

        dut_data[dut_name] = {
            'ip': dut_ip,
            'connectivity': connectivity,
            'nets': nets_info
        }

    click.echo()  # Empty line before table
    _format_status_table(dut_data)


def _show_dut_status(ctx: click.Context, dut_name: str) -> None:
    """Show detailed status for a specific DUT."""
    # First try to resolve as a local DUT name
    dut_ip = get_dut_ip(dut_name)
    original_dut_name = dut_name

    if not dut_ip:
        # Check if it might be an IP address directly
        try:
            import ipaddress
            ipaddress.ip_address(dut_name)
            dut_ip = dut_name
            dut_name = f"Direct IP ({dut_name})"
        except ValueError:
            click.secho(f"DUT '{dut_name}' not found in .lager file.", fg='red', err=True)
            click.echo("Available DUTs:")
            duts = list_duts()
            for name in sorted(duts.keys()):
                click.echo(f"  - {name}")
            ctx.exit(1)

    click.echo(f"Checking status for {dut_name}...")

    # Check connectivity
    connectivity = _check_dut_connectivity(dut_ip)

    # Get nets information from local storage using original DUT name
    nets_info = _get_dut_nets(ctx, original_dut_name)

    # Display detailed information
    dut_data = {
        'connectivity': connectivity,
        'nets': nets_info
    }

    _display_dut_details(dut_name, dut_ip, dut_data)


@status.command("tui", help="Launch status monitoring TUI")
@click.option("--refresh-interval", type=float, default=10.0,
              help="Refresh interval in seconds (s)")
@click.pass_context
def tui_cmd(ctx: click.Context, refresh_interval: float) -> None:
    """Launch the interactive status monitoring TUI."""
    launch_status_tui(ctx, None, refresh_interval)