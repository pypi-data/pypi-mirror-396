from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal
from ..dut_storage import resolve_and_validate_dut

SOLAR_ROLE = "solar"

###############################################################################
# Internal helpers                                                            #
###############################################################################

def _resolve_gateway(ctx, box, dut):
    """Resolve DUT name to IP address if it's a local DUT."""
    # Use box or dut (box takes precedence)
    box_name = box or dut
    return resolve_and_validate_dut(ctx, box_name)


def _run_net_py(ctx: click.Context, dut: str, *args: str) -> list[dict]:
    """Run net.py to get list of nets."""
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


def _list_solar_nets(ctx, box):
    """Get list of solar nets from gateway."""
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == SOLAR_ROLE]


def _display_solar_nets(ctx, box):
    """Display solar nets in a table."""
    nets = _list_solar_nets(ctx, box)
    if not nets:
        click.echo("No solar nets found on this gateway.")
        return

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(["t", "t", "t", "t", "t"])
    table.set_cols_align(["l", "l", "l", "l", "l"])
    table.header(["Name", "Net Type", "Instrument", "Channel", "Address"])

    for rec in nets:
        table.add_row([
            rec.get("name", ""),
            rec.get("role", ""),
            rec.get("instrument", ""),
            rec.get("pin", ""),
            rec.get("address", "")
        ])

    click.echo(table.draw())


def _run_backend(ctx: click.Context, gateway: str | None, action: str, **params) -> None:
    """Send action (+ params) for the current solar net to the gateway backend."""
    # Retrieve the net name from context (set by the group callback)
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError("NETNAME required for solar command.")
    # Determine target gateway (if any)
    if gateway is None:
        gateway = ctx.obj.gateway

    # Resolve and validate the gateway name
    gateway = resolve_and_validate_dut(ctx, gateway)

    # Prepare command data for solar backend
    data = {
        "action": action,
        "params": {"netname": netname, **params},
    }
    try:
        run_python_internal(
            ctx,
            get_impl_path("solar.py"),
            gateway,
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
        # If backend exited with error, propagate the non-zero exit code
        if e.code != 0:
            raise

###############################################################################
# Main command group                                                         #
###############################################################################

@click.group(invoke_without_command=True, help="Control solar simulator settings and output")
@click.argument("netname", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def solar(ctx, netname, box, dut):
    """
    Top-level solar command: stores net & optional gateway.
    """
    # Resolve box/dut (box takes precedence, dut is for backward compatibility)
    gateway = box or dut

    if ctx.obj is None:
        # Create a simple attribute container for storing context data
        class _Obj:
            pass
        ctx.obj = _Obj()

    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'solar')

    # Store provided net name and gateway (if any) in context
    setattr(ctx.obj, "netname", netname)
    setattr(ctx.obj, "gateway", gateway)

    # If no subcommand and no netname, list nets
    if ctx.invoked_subcommand is None:
        resolved_gateway = _resolve_gateway(ctx, box, dut)
        _display_solar_nets(ctx, resolved_gateway)

###############################################################################
# Sub-commands                                                               #
###############################################################################

@solar.command("set", help="Initialize and start solar simulation mode")
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def set_mode(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """Initialize and start the solar simulation mode."""
    gateway = box or dut
    _run_backend(ctx, gateway, "set_to_solar_mode")

@solar.command("stop", help="Stop solar simulation mode")
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def stop_mode(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """Stop the solar simulation mode."""
    gateway = box or dut
    _run_backend(ctx, gateway, "stop_solar_mode")

@solar.command("irradiance", help="Set (or read) irradiance in watts per square meter (W/m²)")
@click.argument("value", required=False, type=click.FloatRange(min=0.0, max=1500.0))
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def irradiance(ctx: click.Context, value: float | None, box: str | None, dut: str | None) -> None:
    """Get or set the irradiance in W m⁻²."""
    gateway = box or dut
    if value is None:
        _run_backend(ctx, gateway, "irradiance")
    else:
        _run_backend(ctx, gateway, "irradiance", value=value)

@solar.command("mpp-current", help="Read maximum power point current in amps (A)")
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def mpp_current(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """Return the MPP current (A)."""
    gateway = box or dut
    _run_backend(ctx, gateway, "mpp_current")

@solar.command("mpp-voltage", help="Read maximum power point voltage in volts (V)")
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def mpp_voltage(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """Return the MPP voltage (V)."""
    gateway = box or dut
    _run_backend(ctx, gateway, "mpp_voltage")

@solar.command("resistance", help="Set (or read) dynamic panel resistance in ohms (Ω)")
@click.argument("value", required=False, type=click.FloatRange(min=0.1, max=100.0))
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def resistance(ctx: click.Context, value: float | None, box: str | None, dut: str | None) -> None:
    """Get or set the dynamic panel resistance (Ω)."""
    gateway = box or dut
    if value is None:
        _run_backend(ctx, gateway, "resistance")
    else:
        _run_backend(ctx, gateway, "resistance", value=value)

@solar.command("temperature", help="Read cell temperature in degrees Celsius (°C)")
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def temperature(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """Return the cell temperature (°C)."""
    gateway = box or dut
    _run_backend(ctx, gateway, "temperature")

@solar.command("voc", help="Read open-circuit voltage in volts (V)")
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def voc(ctx: click.Context, box: str | None, dut: str | None) -> None:
    """Return the open‑circuit voltage (Voc)."""
    gateway = box or dut
    _run_backend(ctx, gateway, "voc")