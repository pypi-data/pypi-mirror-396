"""
    Supply commands (local nets; Rigol DP800 friendly)

    Usage:
      lager supply                    -> lists only supply nets
      lager supply <NETNAME> voltage  -> set/read voltage on that net
      lager supply <NETNAME> current  -> set/read current on that net
      lager supply <NETNAME> enable
      lager supply <NETNAME> disable
      lager supply <NETNAME> state
      lager supply <NETNAME> clear-ocp
      lager supply <NETNAME> clear-ovp
      lager supply <NETNAME> set
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
import asyncio

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal


def parse_value_with_negatives(ctx, param, value):
    """Parse value, handling the case where negative values are passed with -- separator."""
    if value is None:
        return None
    
    # Handle case where value looks like '--0.050' (negative value misinterpreted as flag)
    if isinstance(value, str) and value.startswith('--') and len(value) > 2:
        try:
            # Remove the extra '--' prefix and parse as negative
            return -float(value[2:])
        except ValueError:
            pass
    
    # Regular parsing
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            raise click.BadParameter(f"'{value}' is not a valid float.")
    
    return value

SUPPLY_ROLE = "power-supply"


# ---------- helpers ----------

def _require_netname(ctx) -> str:
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager supply <NETNAME> <COMMAND>\n"
            "Example: lager supply supply1 voltage --ovp 5.5 --ocp 0.8"
        )
    return netname


def _resolve_gateway(ctx, box, dut):
    from ..dut_storage import resolve_and_validate_dut

    # Use box or dut (box takes precedence)
    box_name = box or dut
    return resolve_and_validate_dut(ctx, box_name)


def _validate_positive_parameters(**params):
    """Validate that all provided parameters are positive values"""
    for param_name, value in params.items():
        if value is not None and value < 0:
            param_type = "V" if "voltage" in param_name or "ovp" in param_name else "A"
            raise click.BadParameter(f"{param_name.replace('_', ' ').title()} must be positive, got {value}{param_type}")


def _validate_protection_limits(voltage=None, current=None, ovp=None, ocp=None):
    """Validate that protection limits are not below setpoints"""
    if ovp is not None and voltage is not None and ovp < voltage:
        raise click.BadParameter(
            f"OVP limit ({ovp}V) cannot be less than voltage setpoint ({voltage}V). "
            f"Use a higher OVP value or lower the voltage first."
        )
    if ocp is not None and current is not None and ocp < current:
        raise click.BadParameter(
            f"OCP limit ({ocp}A) cannot be less than current setpoint ({current}A). "
            f"Use a higher OCP value or lower the current first."
        )


def _run_net_py(ctx: click.Context, dut: str, *args: str) -> list[dict]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path("net.py"),
                dut,
                image="",
                env={},
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum="SIGTERM",
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=args or ("list",),
            )
    except SystemExit:
        pass
    raw = buf.getvalue() or "[]"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def _list_supply_nets(ctx, box):
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == SUPPLY_ROLE]


def validate_net(ctx, box, netname, net_role):
    """Validate that a net exists and has the specified role using locally saved nets"""
    nets = _run_net_py(ctx, box, "list")
    for net in nets:
        if net.get("name") == netname and net.get("role") == net_role:
            return True
    return False


def display_nets(ctx, box, netname: str | None):
    nets = _list_supply_nets(ctx, box)
    if not nets:
        click.echo("No power supply nets found on this gateway.")
        return

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(["t", "t", "t", "t", "t"])
    table.set_cols_align(["l", "l", "l", "l", "l"])
    table.header(["Name", "Net Type", "Instrument", "Channel", "Address"])

    for rec in nets:
        if netname is None or netname == rec.get("name"):
            table.add_row([
                rec.get("name", ""),
                rec.get("role", ""),
                rec.get("instrument", ""),
                rec.get("pin", ""),
                rec.get("address", "")
            ])

    click.echo(table.draw())


def _run_backend(ctx, dut, action: str, **params):
    """
    Run backend command and handle errors gracefully.

    First tries to use the WebSocket HTTP endpoint if a TUI is running for this net,
    which allows sharing the USB connection. Falls back to direct access if no TUI is active.
    """
    import requests

    netname = getattr(ctx.obj, "netname", None)

    # Try WebSocket HTTP endpoint first (for concurrent TUI + CLI access)
    if netname:
        try:
            # Get gateway IP from dut
            from ..dut_storage import resolve_and_validate_dut
            gateway_ip = resolve_and_validate_dut(ctx, dut)

            # Try the WebSocket-shared endpoint
            url = f"http://{gateway_ip}:9000/supply/command"
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
                    click.echo(f"✓ {message}")
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
        "action": action,
        "params": params,
    }

    # Capture stderr to detect Resource busy errors
    import sys
    import io
    from contextlib import redirect_stderr

    stderr_capture = io.StringIO()

    try:
        with redirect_stderr(stderr_capture):
            run_python_internal(
                ctx,
                get_impl_path("supply.py"),
                dut,
                image="",
                env=(f"LAGER_COMMAND_DATA={json.dumps(data)}",),
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum="SIGTERM",
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=(),
            )
    except SystemExit as e:
        # Get captured stderr
        stderr_output = stderr_capture.getvalue()

        # Check if this is a "Resource busy" error
        if e.code != 0 and "Resource busy" in stderr_output:
            click.echo(stderr_output, err=True)  # Print the original error
            click.echo("\n" + "="*70, err=True)
            click.echo("WARNING: Power supply is currently in use by the TUI", err=True)
            click.echo("="*70, err=True)
            click.echo(f"\nThe power supply '{netname}' cannot be accessed because it's being used", err=True)
            click.echo("by an active 'lager supply tui' session.\n", err=True)
            click.echo("To fix this:", err=True)
            click.echo(f"  1. Close the TUI: Press 'q' or 'Ctrl+C' in the TUI window", err=True)
            click.echo(f"  2. Then retry this command", err=True)
            click.echo("\nOr use the TUI's command prompt to control the supply interactively.", err=True)
            raise SystemExit(1)
        elif e.code != 0:
            # Other error - print captured stderr and re-raise
            click.echo(stderr_output, err=True)
            raise

    # Provide feedback for operations that don't naturally produce output
    if action in ["set_mode", "clear_ovp", "clear_ocp", "enable", "disable"]:
        operation_names = {
            "set_mode": "Set power supply mode",
            "clear_ovp": "Cleared OVP protection",
            "clear_ocp": "Cleared OCP protection",
            "enable": "Enabled supply output",
            "disable": "Disabled supply output"
        }
        click.echo(f"✓ {operation_names.get(action, 'Operation completed')}")


# ---------- CLI ----------

@click.group(invoke_without_command=True)
@click.argument("NETNAME", required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def supply(ctx, box, dut, netname):
    """
        Control power supply voltage and current
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'power_supply')

    if netname is not None:
        ctx.obj.netname = netname

    if ctx.invoked_subcommand is None:
        gw = _resolve_gateway(ctx, box, dut)
        display_nets(ctx, gw, None)


@supply.command()
@click.argument("VALUE", required=False, callback=parse_value_with_negatives)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--ocp", required=False, type=click.FLOAT, help="Over-current protection limit in amps (A)")
@click.option("--ovp", required=False, type=click.FLOAT, help="Over-voltage protection limit in volts (V)")
@click.option("--yes", is_flag=True, default=False, help="Confirm the action without prompting")
def voltage(ctx, box, dut, value, ocp, ovp, yes):
    """Set (or read) voltage in volts (V)"""
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    # Validate positive values and protection limits at CLI level
    _validate_positive_parameters(voltage=value, ocp=ocp, ovp=ovp)
    _validate_protection_limits(voltage=value, ovp=ovp)

    if value is not None and not (yes or click.confirm(f"Set voltage to {value} V?", default=False)):
        click.echo("Aborting")
        return

    _run_backend(
        ctx, resolved_gateway,
        action="voltage",
        netname=netname,
        value=value,
        ocp=ocp,
        ovp=ovp,
    )


@supply.command()
@click.argument("VALUE", required=False, callback=parse_value_with_negatives)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--ocp", required=False, type=click.FLOAT, help="Over-current protection limit in amps (A)")
@click.option("--ovp", required=False, type=click.FLOAT, help="Over-voltage protection limit in volts (V)")
@click.option("--yes", is_flag=True, default=False, help="Confirm the action without prompting")
def current(ctx, box, dut, value, ocp, ovp, yes):
    """Set (or read) current in amps (A)"""
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    # Validate positive values and protection limits at CLI level
    _validate_positive_parameters(current=value, ocp=ocp, ovp=ovp)
    _validate_protection_limits(current=value, ocp=ocp)

    if value is not None and not (yes or click.confirm(f"Set current to {value} A?", default=False)):
        click.echo("Aborting")
        return

    _run_backend(
        ctx, resolved_gateway,
        action="current",
        netname=netname,
        value=value,
        ocp=ocp,
        ovp=ovp,
    )


@supply.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--yes", is_flag=True, help="Confirm the action without prompting")
def disable(ctx, box, dut, yes):
    """Disable supply output"""
    if not yes and not click.confirm("Disable Net?", default=False):
        click.echo("Aborting")
        return
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, resolved_gateway, action="disable", netname=netname)


@supply.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--yes", is_flag=True, help="Confirm the action without prompting")
def enable(ctx, box, dut, yes):
    """Enable supply output"""
    if not yes and not click.confirm("Enable Net?", default=False):
        click.echo("Aborting")
        return
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, resolved_gateway, action="enable", netname=netname)


@supply.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def state(ctx, box, dut):
    """Read power state"""
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, resolved_gateway, action="state", netname=netname)


@supply.command(name="set")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def set_mode(ctx, box, dut):
    """
        Set power supply mode
    """
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, resolved_gateway, action="set_mode", netname=netname)


@supply.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def clear_ovp(ctx, box, dut):
    """Clear over-voltage protection trip condition"""
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, resolved_gateway, action="clear_ovp", netname=netname)


@supply.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def clear_ocp(ctx, box, dut):
    """Clear over-current protection trip condition"""
    resolved_gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)
    _run_backend(ctx, resolved_gateway, action="clear_ocp", netname=netname)


@supply.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def tui(ctx, box, dut):
    """Launch interactive supply control TUI"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, SUPPLY_ROLE):
        click.echo(f"{netname} is not a supply net")
        return

    try:
        from .supply_tui import SupplyTUI
        app = SupplyTUI(ctx, netname, gateway, gateway)
        asyncio.run(app.run_async())
    except Exception:
        raise