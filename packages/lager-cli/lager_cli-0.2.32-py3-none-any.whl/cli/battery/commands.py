"""
    Battery commands
"""
from __future__ import annotations

import io
import json
import asyncio
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

BATTERY_ROLE = "battery"


# ---------- helpers ----------

def _require_netname(ctx) -> str:
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager battery <NETNAME> <COMMAND>\n"
            "Example: lager battery battery1 soc 50"
        )
    return netname


def _resolve_gateway(ctx, box, dut):
    from ..dut_storage import resolve_and_validate_dut

    # Use box or dut (box takes precedence)
    box_name = box or dut
    return resolve_and_validate_dut(ctx, box_name)


def _run_net_py(ctx: click.Context, gateway: str, *args: str) -> list[dict]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path('net.py'),
                gateway,
                image='',
                env={},
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum='SIGTERM',
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=args or ('list',),
            )
    except SystemExit:
        pass
    raw = buf.getvalue() or '[]'
    try:
        return json.loads(raw)
    except Exception:
        return []


def _list_battery_nets(ctx, box: str) -> None:
    recs = _run_net_py(ctx, box, 'list')
    nets = [r for r in recs if r.get("role") == BATTERY_ROLE]
    if not nets:
        click.echo("No battery nets found on this gateway.")
        return

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 't', 't', 't'])
    table.set_cols_align(['l', 'l', 'l', 'l', 'l'])
    table.header(['Name', 'Net Type', 'Instrument', 'Channel', 'Address'])

    for net in nets:
        table.add_row([
            net.get('name', ''),
            net.get('role', ''),
            net.get('instrument', ''),
            net.get('pin', ''),
            net.get('address', '')
        ])

    click.echo(table.draw())


def validate_net(ctx, box, netname, net_role):
    """Validate that a net exists and has the specified role using locally saved nets"""
    nets = _run_net_py(ctx, box, 'list')
    for net in nets:
        if net.get("name") == netname and net.get("role") == net_role:
            return True
    return False


def _run_backend(ctx, box, action: str, **params):
    """
    Run backend command and handle errors gracefully.

    First tries to use the WebSocket HTTP endpoint if a TUI is running for this net,
    which allows sharing the USB connection. Falls back to direct access if no TUI is active.
    """
    import requests

    netname = params.get('netname')

    # Try WebSocket HTTP endpoint first (for concurrent TUI + CLI access)
    if netname:
        try:
            # Get gateway IP from box
            from ..dut_storage import resolve_and_validate_dut
            gateway_ip = resolve_and_validate_dut(ctx, box)

            # Try the WebSocket-shared endpoint
            url = f"http://{gateway_ip}:9000/battery/command"
            payload = {
                "netname": netname,
                "action": action,
                "params": params
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Command succeeded via WebSocket endpoint
                    message = result.get('message', 'Command executed')
                    click.echo(f"\033[92m{message}\033[0m")
                    return
                else:
                    # WebSocket endpoint returned error
                    click.echo(f"Error: {result.get('error', 'Unknown error')}", err=True)
                    raise SystemExit(1)

            elif response.status_code == 404:
                # No active WebSocket session, fall through to direct access
                pass

            else:
                # Other HTTP error, try direct access as fallback
                pass

        except (requests.ConnectionError, requests.Timeout):
            # Gateway not reachable via HTTP, fall through to direct access
            pass
        except Exception:
            # Other error, fall through to direct access
            pass

    # Fall back to direct USB access (original behavior)
    data = {
        'action': action,
        'params': params,
    }
    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
        box,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum='SIGTERM',
        timeout=0,
        detach=False,
        port=(),
        org=None,
        args=(),
    ) 

@click.group(invoke_without_command=True)
@click.argument('NETNAME', required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def battery(ctx, box, dut, netname):
    """
        Control battery simulator settings and output
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'battery')

    if netname is not None:
        ctx.obj.netname = netname

    # Only resolve gateway if no subcommand (listing nets)
    # When there's a subcommand, let it handle gateway resolution with its own --dut option
    if ctx.invoked_subcommand is None:
        gateway = _resolve_gateway(ctx, box, dut)
        _list_battery_nets(ctx, gateway)   

@battery.command()
@click.argument('MODE_TYPE', required=False, type=click.Choice(('static', 'dynamic')))
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def mode(ctx, box, dut, mode_type):
    """
        Set (or read) battery simulation mode type
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_mode', netname=netname, mode_type=mode_type)

@battery.command(name='set')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def set_mode(ctx, box, dut):
    """
        Initialize battery simulator mode
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_to_battery_mode', netname=netname)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def soc(ctx, box, dut, value):
    """
        Set (or read) battery state of charge in percent (%)
    """   
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_soc', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def voc(ctx, box, dut, value):
    """
        Set (or read) battery open circuit voltage in volts (V)
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_voc', netname=netname, value=value)

@battery.command(name='batt-full')
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def batt_full(ctx, box, dut, value):
    """
        Set (or read) battery fully charged voltage in volts (V)
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_volt_full', netname=netname, value=value)

@battery.command(name='batt-empty')
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def batt_empty(ctx, box, dut, value):
    """
        Set (or read) battery fully discharged voltage in volts (V)
    """      
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_volt_empty', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def capacity(ctx, box, dut, value):
    """
        Set (or read) battery capacity limit in amp-hours (Ah)
    """      
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_capacity', netname=netname, value=value)

@battery.command(name='current-limit')
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def current_limit(ctx, box, dut, value):
    """
        Set (or read) maximum charge/discharge current in amps (A)
    """       
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_current_limit', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def ovp(ctx, box, dut, value):
    """
        Set (or read) over voltage protection limit in volts (V)
    """   
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_ovp', netname=netname, value=value)

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def ocp(ctx, box, dut, value):
    """
        Set (or read) over current protection limit in amps (A)
    """     
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_ocp', netname=netname, value=value)

@battery.command()
@click.argument('PARTNUMBER', required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def model(ctx, box, dut, partnumber):
    """
        Set (or read) battery model (18650, nimh, lead-acid, etc.)
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'set_model', netname=netname, partnumber=partnumber)

@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def state(ctx, box, dut):
    """
        Get battery state (comprehensive status)
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'state', netname=netname) 

@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def enable(ctx, box, dut, yes):
    """
        Enable battery simulator output
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if yes or click.confirm(f"Enable Net?", default=False):
        pass
    else:
        click.echo("Aborting")
        return

    _run_backend(ctx, gateway, 'enable_battery', netname=netname) 

@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Confirm the action without prompting.')
def disable(ctx, box, dut, yes):
    """
        Disable battery simulator output
    """    
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if yes or click.confirm(f"Disable Net?", default=True):
        pass
    else:
        click.echo("Aborting")
        return

    _run_backend(ctx, gateway, 'disable_battery', netname=netname)

# --------- CLEAR COMMANDS ---------

@battery.command(name='clear')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def clear_both(ctx, box, dut):
    """
        Clear protection trip conditions (OVP/OCP)
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'clear', netname=netname)

# NEW: clear-ovp (targets OVP only if backend supports it; otherwise acts like clear)
@battery.command(name='clear-ovp')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def clear_ovp(ctx, box, dut):
    """
        Clear OVP trip condition
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'clear_ovp', netname=netname)

# NEW: clear-ocp (targets OCP only if backend supports it; otherwise acts like clear)
@battery.command(name='clear-ocp')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def clear_ocp(ctx, box, dut):
    """
        Clear OCP trip condition
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, gateway, 'clear_ocp', netname=netname)


@battery.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def tui(ctx, box, dut):
    """Launch interactive battery control TUI"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, BATTERY_ROLE):
        click.echo(f"{netname} is not a battery net")
        return

    try:
        from .battery_tui import BatteryTUI
        app = BatteryTUI(ctx, netname, gateway, gateway)
        asyncio.run(app.run_async())
    except Exception:
        raise
