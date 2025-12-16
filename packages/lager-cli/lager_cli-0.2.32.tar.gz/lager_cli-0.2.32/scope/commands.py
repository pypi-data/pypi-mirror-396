"""
    Scope commands (analog nets using local nets)
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

SCOPE_ROLE = "scope"


# ---------- helpers ----------

def _require_netname(ctx) -> str:
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager scope <NETNAME> <COMMAND>\n"
            "Example: lager scope scope1 disable"
        )
    return netname


def _resolve_gateway(ctx, box, dut):
    from ..dut_storage import resolve_and_validate_dut

    # Use box or dut (box takes precedence)
    box_name = box or dut
    return resolve_and_validate_dut(ctx, box_name)


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


def _list_scope_nets(ctx, box):
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == SCOPE_ROLE]


def validate_net(ctx, box, netname, net_role):
    """Validate that a net exists and has the specified role using locally saved nets"""
    nets = _run_net_py(ctx, box, "list")
    for net in nets:
        if net.get("name") == netname and net.get("role") == net_role:
            return True
    return False


def display_nets(ctx, box, netname: str | None):
    nets = _list_scope_nets(ctx, box)
    if not nets:
        click.echo("No scope nets found on this gateway.")
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
    """Run backend command for scope operations"""
    data = {
        "action": action,
        "mcu": params.pop("mcu", None),
        "params": params,
    }
    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


# ---------- CLI ----------

@click.group(invoke_without_command=True)
@click.argument("NETNAME", required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def scope(ctx, box, dut, netname):
    """Control oscilloscope settings"""
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'scope')

    if netname is not None:
        ctx.obj.netname = netname

    if ctx.invoked_subcommand is None:
        gw = _resolve_gateway(ctx, box, dut)
        display_nets(ctx, gw, None)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def disable(ctx, box, dut, mcu):
    """Disable scope channel"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "disable_net", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def enable(ctx, box, dut, mcu):
    """Enable scope channel"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "enable_net", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--single", is_flag=True, help="Capture single waveform then stop")
def start(ctx, box, dut, mcu, single):
    """Start waveform capture (continuous or single)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    action = "start_single" if single else "start_capture"
    _run_backend(ctx, gateway, action, netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def stop(ctx, box, dut, mcu):
    """Stop waveform capture"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "stop_capture", netname=netname, mcu=mcu)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def force(ctx, box, dut, mcu):
    """Force trigger manually (bypass trigger condition)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "force_trigger", netname=netname, mcu=mcu)


@scope.command()
@click.argument("volts_per_div", type=float)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def scale(ctx, volts_per_div, box, dut, mcu):
    """Set vertical scale (volts per division)

    \b
    Examples:
      lager scope scope1 scale 1.0 --box my-box    # 1V/div
      lager scope scope1 scale 0.5 --box my-box    # 500mV/div
      lager scope scope1 scale 0.1 --box my-box    # 100mV/div
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "set_scale", netname=netname, mcu=mcu,
                 volts_per_div=volts_per_div)


CHANNEL_COUPLING_CHOICES = click.Choice(("dc", "ac", "gnd"))


@scope.command()
@click.argument("mode", type=CHANNEL_COUPLING_CHOICES)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def coupling(ctx, mode, box, dut, mcu):
    """Set channel coupling mode (dc, ac, or gnd)

    \b
    Examples:
      lager scope scope1 coupling dc --box my-box   # DC coupling (default)
      lager scope scope1 coupling ac --box my-box   # AC coupling (blocks DC)
      lager scope scope1 coupling gnd --box my-box  # Ground reference
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "set_coupling", netname=netname, mcu=mcu, mode=mode)


PROBE_CHOICES = click.Choice(("1", "10", "100", "1000"))


@scope.command()
@click.argument("ratio", type=PROBE_CHOICES)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def probe(ctx, ratio, box, dut, mcu):
    """Set probe attenuation ratio (1x, 10x, 100x, 1000x)

    Example: lager scope scope1 probe 10 --box my-box
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "set_probe", netname=netname, mcu=mcu, ratio=int(ratio))


@scope.command()
@click.argument("seconds_per_div", type=float)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True)
@click.option("--mcu", required=False)
def timebase(ctx, seconds_per_div, box, dut, mcu):
    """Set horizontal timebase (seconds per division)

    \b
    Examples:
      lager scope scope1 timebase 0.001 --box my-box    # 1ms/div
      lager scope scope1 timebase 0.0001 --box my-box   # 100us/div
      lager scope scope1 timebase 0.000001 --box my-box # 1us/div
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "set_timebase", netname=netname, mcu=mcu,
                 seconds_per_div=seconds_per_div)


@scope.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def autoscale(ctx, box, dut, mcu):
    """Automatically adjust vertical scale and timebase (Rigol only)

    Note: This operation can take 10-15 seconds to complete.

    Example: lager scope scope1 autoscale --box my-box
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    click.echo("Running autoscale (this may take 10-15 seconds)...")
    _run_backend(ctx, gateway, "autoscale", netname=netname, mcu=mcu)


@scope.group()
def measure():
    """Measure waveform characteristics (Rigol only - PicoScope uses streaming)"""
    pass


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def period(ctx, mcu, box, dut, display, cursor):
    """Measure waveform period"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_period",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def freq(ctx, mcu, box, dut, display, cursor):
    """Measure waveform frequency"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_freq",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def vpp(ctx, mcu, box, dut, display, cursor):
    """Measure peak-to-peak voltage"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_vpp",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def vmax(ctx, mcu, box, dut, display, cursor):
    """Measure maximum voltage"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_vmax",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def vmin(ctx, mcu, box, dut, display, cursor):
    """Measure minimum voltage"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_vmin",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def vrms(ctx, mcu, box, dut, display, cursor):
    """Measure RMS voltage"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_vrms",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def vavg(ctx, mcu, box, dut, display, cursor):
    """Measure average voltage"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_vavg",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command("pulse-width-pos")
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def pulse_width_pos(ctx, mcu, box, dut, display, cursor):
    """Measure positive pulse width"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_pulse_width_pos",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command("pulse-width-neg")
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def pulse_width_neg(ctx, mcu, box, dut, display, cursor):
    """Measure negative pulse width"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_pulse_width_neg",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command("duty-cycle-pos")
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def duty_cycle_pos(ctx, mcu, box, dut, display, cursor):
    """Measure positive duty cycle"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_dc_pos",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@measure.command("duty-cycle-neg")
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--display", is_flag=True, help="Display measurement on screen")
@click.option("--cursor", is_flag=True, help="Enable measurement cursor")
def duty_cycle_neg(ctx, mcu, box, dut, display, cursor):
    """Measure negative duty cycle"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "measure_dc_neg",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "display": display,
            "cursor": cursor
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@scope.group()
def trigger():
    """Configure trigger settings"""
    pass


MODE_CHOICES = click.Choice(("normal", "auto", "single"))
COUPLING_CHOICES = click.Choice(("dc", "ac", "low_freq_rej", "high_freq_rej"))


@trigger.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mode", default="normal", type=MODE_CHOICES, help="Trigger mode", show_default=True)
@click.option("--coupling", default="dc", type=COUPLING_CHOICES, help="Coupling mode", show_default=True)
@click.option("--source", required=False, help="Trigger source", metavar="NET")
@click.option("--slope", type=click.Choice(("rising", "falling", "both")), help="Trigger slope")
@click.option("--level", type=click.FLOAT, help="Trigger level")
def edge(ctx, mcu, box, dut, mode, coupling, source, slope, level):
    """Set edge trigger (works with both PicoScope and Rigol)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "trigger_edge",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "mode": mode,
            "coupling": coupling,
            "source": source,
            "slope": slope,
            "level": level,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@trigger.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mode", default="normal", type=MODE_CHOICES, help="Trigger mode", show_default=True)
@click.option("--coupling", default="dc", type=COUPLING_CHOICES, help="Coupling mode", show_default=True)
@click.option("--source", required=False, help="Trigger source", metavar="NET")
@click.option("--level", type=click.FLOAT, help="Trigger level")
@click.option("--baud", type=click.INT, default=9600, help="Baud rate", show_default=True)
@click.option("--parity", type=click.Choice(("none", "even", "odd")), default="none", help="Parity", show_default=True)
@click.option("--stop-bits", type=click.Choice(("1", "1.5", "2")), default="1", help="Stop bits", show_default=True)
@click.option("--data-width", type=click.INT, default=8, help="Data width (bits)", show_default=True)
@click.option("--trigger-on", type=click.Choice(("start", "stop", "data", "error")), default="start", help="Trigger condition", show_default=True)
@click.option("--data", type=click.STRING, required=False, help="Data pattern to match (hex)")
def uart(ctx, mcu, box, dut, mode, coupling, source, level, baud, parity, stop_bits, data_width, trigger_on, data):
    """Set UART trigger (Rigol only)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "trigger_uart", netname=netname, mcu=mcu, mode=mode,
                 coupling=coupling, source=source, level=level, trigger_on=trigger_on,
                 parity=parity, stop_bits=stop_bits, baud=baud, data_width=data_width, data=data)


@trigger.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mode", default="normal", type=MODE_CHOICES, help="Trigger mode", show_default=True)
@click.option("--coupling", default="dc", type=COUPLING_CHOICES, help="Coupling mode", show_default=True)
@click.option("--source-scl", required=False, help="SCL source net", metavar="NET")
@click.option("--source-sda", required=False, help="SDA source net", metavar="NET")
@click.option("--level-scl", type=click.FLOAT, help="SCL trigger level")
@click.option("--level-sda", type=click.FLOAT, help="SDA trigger level")
@click.option("--trigger-on", type=click.Choice(("start", "restart", "stop", "ack_miss", "address", "data", "addr_data")), default="start", help="Trigger condition", show_default=True)
@click.option("--address", type=click.STRING, required=False, help="I2C address (hex)")
@click.option("--addr-width", type=click.Choice(("7", "8", "10")), default="7", help="Address width (bits)", show_default=True)
@click.option("--data", type=click.STRING, required=False, help="Data pattern to match (hex)")
@click.option("--data-width", type=click.INT, default=8, help="Data width (bits)", show_default=True)
@click.option("--direction", type=click.Choice(("read", "write", "read_write")), default="read_write", help="Transfer direction", show_default=True)
def i2c(ctx, mcu, box, dut, mode, coupling, source_scl, source_sda, level_scl, level_sda,
        trigger_on, address, addr_width, data, data_width, direction):
    """Set I2C trigger (Rigol only)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "trigger_i2c", netname=netname, mcu=mcu, mode=mode,
                 coupling=coupling, source_scl=source_scl, level_scl=level_scl,
                 source_sda=source_sda, level_sda=level_sda, trigger_on=trigger_on,
                 address=address, addr_width=addr_width, data=data, data_width=data_width,
                 direction=direction)


@trigger.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mode", default="normal", type=MODE_CHOICES, help="Trigger mode", show_default=True)
@click.option("--coupling", default="dc", type=COUPLING_CHOICES, help="Coupling mode", show_default=True)
@click.option("--source-mosi-miso", required=False, help="MOSI/MISO source net", metavar="NET")
@click.option("--source-sck", required=False, help="SCK source net", metavar="NET")
@click.option("--source-cs", required=False, help="CS source net", metavar="NET")
@click.option("--level-mosi-miso", type=click.FLOAT, help="MOSI/MISO trigger level")
@click.option("--level-sck", type=click.FLOAT, help="SCK trigger level")
@click.option("--level-cs", type=click.FLOAT, help="CS trigger level")
@click.option("--trigger-on", type=click.Choice(("timeout", "cs")), default="cs", help="Trigger condition", show_default=True)
@click.option("--data", type=click.STRING, required=False, help="Data pattern to match (hex)")
@click.option("--data-width", type=click.INT, default=8, help="Data width (bits)", show_default=True)
@click.option("--clk-slope", type=click.Choice(("rising", "falling")), default="rising", help="Clock edge", show_default=True)
@click.option("--cs-idle", type=click.Choice(("high", "low")), default="high", help="CS idle state", show_default=True)
@click.option("--timeout", type=click.FLOAT, required=False, help="Timeout value (seconds)")
def spi(ctx, mcu, box, dut, mode, coupling, source_mosi_miso, source_sck, source_cs,
        level_mosi_miso, level_sck, level_cs, trigger_on, data, data_width, clk_slope, cs_idle, timeout):
    """Set SPI trigger (Rigol only)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "trigger_spi", netname=netname, mcu=mcu, mode=mode,
                 coupling=coupling, source_mosi_miso=source_mosi_miso, source_sck=source_sck,
                 source_cs=source_cs, level_mosi_miso=level_mosi_miso, level_sck=level_sck,
                 level_cs=level_cs, data=data, data_width=data_width, clk_slope=clk_slope,
                 trigger_on=trigger_on, cs_idle=cs_idle, timeout=timeout)


@trigger.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mode", default="normal", type=MODE_CHOICES, help="Trigger mode", show_default=True)
@click.option("--coupling", default="dc", type=COUPLING_CHOICES, help="Coupling mode", show_default=True)
@click.option("--source", required=False, help="Trigger source", metavar="NET")
@click.option("--level", type=click.FLOAT, help="Trigger level")
@click.option("--trigger-on", type=click.Choice(("positive", "negative", "positive_greater", "negative_greater", "positive_less", "negative_less")), default="positive", help="Trigger condition", show_default=True)
@click.option("--upper", type=click.FLOAT, required=False, help="Upper pulse width limit (seconds)")
@click.option("--lower", type=click.FLOAT, required=False, help="Lower pulse width limit (seconds)")
def pulse(ctx, mcu, box, dut, mode, coupling, source, level, trigger_on, upper, lower):
    """Set pulse width trigger (Rigol only)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "trigger_pulse", netname=netname, mcu=mcu, mode=mode,
                 coupling=coupling, source=source, level=level, trigger_on=trigger_on,
                 upper=upper, lower=lower)


@scope.group()
def cursor():
    """Control scope cursor (Rigol only)"""
    pass


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--x", required=False, type=click.FLOAT, help="Cursor A x coordinate")
@click.option("--y", required=False, type=click.FLOAT, help="Cursor A y coordinate")
def set_a(ctx, box, dut, mcu, x, y):
    """Set cursor A position"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "set_a",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "x": x,
            "y": y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--x", required=False, type=click.FLOAT, help="Cursor B x coordinate")
@click.option("--y", required=False, type=click.FLOAT, help="Cursor B y coordinate")
def set_b(ctx, box, dut, mcu, x, y):
    """Set cursor B position"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "set_b",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "x": x,
            "y": y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--x", required=False, type=click.FLOAT, help="Relative x movement (delta)")
@click.option("--y", required=False, type=click.FLOAT, help="Relative y movement (delta)")
def move_a(ctx, box, dut, mcu, x, y):
    """Move cursor A by relative offset"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "move_a",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "del_x": x,
            "del_y": y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
@click.option("--x", required=False, type=click.FLOAT, help="Relative x movement (delta)")
@click.option("--y", required=False, type=click.FLOAT, help="Relative y movement (delta)")
def move_b(ctx, box, dut, mcu, x, y):
    """Move cursor B by relative offset"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "move_b",
        "mcu": mcu,
        "params": {
            "netname": netname,
            "del_x": x,
            "del_y": y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--mcu", required=False)
def hide(ctx, box, dut, mcu):
    """Hide cursor"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "hide_cursor",
        "mcu": mcu,
        "params": {
            "netname": netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope.py"),
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


# ---------- STREAMING COMMANDS (PicoScope) ----------

@scope.group()
def stream():
    """Stream oscilloscope data (PicoScope)"""
    pass


CAPTURE_MODE_CHOICES = click.Choice(("auto", "normal", "single"))
COUPLING_STREAM_CHOICES = click.Choice(("dc", "ac"))
TRIGGER_SLOPE_CHOICES = click.Choice(("rising", "falling", "either"))
CHANNEL_CHOICES = click.Choice(("A", "B", "1", "2"))


@stream.command("start")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--channel", "-c", type=CHANNEL_CHOICES, default="A", help="Channel to enable (A, B, 1, or 2)")
@click.option("--volts-per-div", "-v", type=float, default=1.0, help="Vertical scale in volts per division (default: 1.0V/div)")
@click.option("--time-per-div", "-t", type=float, default=0.001, help="Horizontal scale in seconds per division (default: 1ms/div)")
@click.option("--trigger-level", type=float, default=0.0, help="Trigger threshold voltage (default: 0V)")
@click.option("--trigger-slope", type=TRIGGER_SLOPE_CHOICES, default="rising", help="Trigger edge direction (rising, falling, or either)")
@click.option("--capture-mode", type=CAPTURE_MODE_CHOICES, default="auto", help="Triggering mode (auto, normal, or single)")
@click.option("--coupling", type=COUPLING_STREAM_CHOICES, default="dc", help="Input coupling type (dc or ac)")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.option("--json", "json_output", is_flag=True, help="JSON output format")
@click.option("--verbose", is_flag=True, help="Verbose debugging output")
def stream_start(ctx, box, dut, channel, volts_per_div, time_per_div, trigger_level, trigger_slope, capture_mode, coupling, quiet, json_output, verbose):
    """Start oscilloscope streaming with web visualization.

    Configures and starts streaming mode for PicoScope oscilloscopes. Opens a web interface
    for real-time waveform visualization at port 8080.

    \b
    Examples:
      # Start streaming with default settings (1V/div, 1ms/div)
      lager scope scope1 stream start --box TEST-2

      # Custom voltage and timebase for viewing 5V signals
      lager scope scope1 stream start --volts-per-div 2.0 --time-per-div 0.01 --box TEST-2

      # Configure trigger for logic signals (0-3.3V)
      lager scope scope1 stream start -v 1.0 -t 0.001 --trigger-level 1.5 --trigger-slope rising --box TEST-2

      # Fast sampling for high-frequency signals
      lager scope scope1 stream start --time-per-div 0.0001 --box TEST-2

      # JSON output for automation
      lager scope scope1 stream start --json --box TEST-2
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    # Check if this is a Picoscope net
    nets = _run_net_py(ctx, gateway, "list")
    net_info = None
    for net in nets:
        if net.get("name") == netname and net.get("role") == SCOPE_ROLE:
            net_info = net
            break

    if not net_info:
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    instrument = net_info.get("instrument", "")
    if "Picoscope" not in instrument and "picoscope" not in instrument.lower():
        click.secho(f"{netname} is not a PicoScope (instrument: {instrument})", fg="yellow", err=True)
        click.secho("Streaming is only supported for PicoScope devices", fg="yellow", err=True)
        return

    data = {
        "action": "stream_start",
        "params": {
            "netname": netname,
            "channel": channel,
            "volts_per_div": volts_per_div,
            "time_per_div": time_per_div,
            "trigger_level": trigger_level,
            "trigger_slope": trigger_slope,
            "capture_mode": capture_mode,
            "coupling": coupling,
            "gateway_ip": gateway,  # Pass gateway IP for browser URL
            "quiet": quiet,
            "json_output": json_output,
            "verbose": verbose,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope_stream.py"),
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


@stream.command("stop")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def stream_stop(ctx, box, dut):
    """Stop oscilloscope streaming acquisition"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "stream_stop",
        "params": {
            "netname": netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path("scope_stream.py"),
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


@stream.command("status")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
def stream_status(ctx, box, dut):
    """Check oscilloscope streaming daemon status"""
    gateway = _resolve_gateway(ctx, box, dut)

    data = {
        "action": "stream_status",
        "params": {}
    }

    run_python_internal(
        ctx,
        get_impl_path("scope_stream.py"),
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


@stream.command("web")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--port", type=int, default=8080, help="HTTP server port for oscilloscope UI")
def stream_web(ctx, box, dut, port):
    """Open web browser for oscilloscope visualization"""
    import webbrowser

    gateway = _resolve_gateway(ctx, box, dut)

    # Construct the URL for the web visualization
    # Port 8080 serves the HTML UI which connects to WebTransport on 8083
    url = f"http://{gateway}:{port}/web_oscilloscope.html"

    click.secho(f"Opening oscilloscope visualization at {url}", fg="green")
    click.secho("Note: Make sure streaming is started with 'lager scope <net> stream start'", fg="yellow")

    try:
        webbrowser.open(url)
    except Exception as e:
        click.secho(f"Could not open browser: {e}", fg="red", err=True)
        click.secho(f"Please open {url} manually in your browser", fg="yellow")


@stream.command("capture")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--output", "-o", type=click.Path(), default="scope_data.csv", help="CSV output file path (default: scope_data.csv)")
@click.option("--duration", "-d", type=float, default=1.0, help="Capture duration in seconds (default: 1.0)")
@click.option("--samples", "-n", type=int, default=None, help="Maximum number of samples to capture (optional)")
@click.option("--quiet", "-q", is_flag=True, help="Minimal output")
@click.option("--json", "json_output", is_flag=True, help="JSON output format")
@click.option("--verbose", is_flag=True, help="Verbose debugging output")
def stream_capture(ctx, box, dut, output, duration, samples, quiet, json_output, verbose):
    """Capture oscilloscope waveform data to CSV file.

    Records triggered waveform data from a streaming PicoScope to a CSV file. The file
    contains timestamps, voltages, and channel information for each sample. Streaming
    must be started before capturing.

    \b
    Examples:
      # Capture 1 second of data to default file (scope_data.csv)
      lager scope scope1 stream capture --box TEST-2

      # Capture 10 seconds to custom file
      lager scope scope1 stream capture -o my_data.csv -d 10.0 --box TEST-2

      # Capture exactly 1000 samples
      lager scope scope1 stream capture -n 1000 --box TEST-2

      # Long capture with verbose progress
      lager scope scope1 stream capture -d 60 --verbose --box TEST-2

      # Automation-friendly JSON output
      lager scope scope1 stream capture --json --box TEST-2
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    data = {
        "action": "stream_capture",
        "params": {
            "netname": netname,
            "output": output,
            "duration": duration,
            "samples": samples,
            "quiet": quiet,
            "json_output": json_output,
            "verbose": verbose,
        }
    }

    # Note: File is saved on gateway at the specified output path
    # For direct connections, download isn't supported - file stays on gateway
    run_python_internal(
        ctx,
        get_impl_path("scope_stream.py"),
        gateway,
        image="",
        env=(f"LAGER_COMMAND_DATA={json.dumps(data)}",),
        passenv=(),
        kill=False,
        download=(),  # Disabled - DirectHTTPSession doesn't support download
        allow_overwrite=True,
        signum="SIGTERM",
        timeout=int(duration * 2 + 30) if duration else 60,
        detach=False,
        port=(),
        org=None,
        args=(),
    )

    click.secho(f"\nNote: Data file saved on gateway at: {output}", fg="yellow")
    click.secho(f"To retrieve: scp lagerdata@{gateway}:/tmp/{output} .", fg="yellow")


@stream.command("config")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.option("--channel", "-c", type=CHANNEL_CHOICES, help="Channel to configure")
@click.option("--volts-per-div", "-v", type=float, help="Volts per division")
@click.option("--time-per-div", "-t", type=float, help="Time per division (seconds)")
@click.option("--trigger-level", type=float, help="Trigger level (volts)")
@click.option("--trigger-source", type=CHANNEL_CHOICES, help="Trigger source channel")
@click.option("--trigger-slope", type=TRIGGER_SLOPE_CHOICES, help="Trigger slope")
@click.option("--capture-mode", type=CAPTURE_MODE_CHOICES, help="Capture mode")
@click.option("--coupling", type=COUPLING_STREAM_CHOICES, help="Input coupling")
@click.option("--enable/--disable", default=None, help="Enable or disable channel")
def stream_config(ctx, box, dut, channel, volts_per_div, time_per_div, trigger_level, trigger_source, trigger_slope, capture_mode, coupling, enable):
    """Configure oscilloscope streaming settings (PicoScope)"""
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, gateway, netname, SCOPE_ROLE):
        click.secho(f"{netname} is not a scope net", fg="red", err=True)
        return

    # Build config dict with only provided options
    config_params = {"netname": netname}
    if channel is not None:
        config_params["channel"] = channel
    if volts_per_div is not None:
        config_params["volts_per_div"] = volts_per_div
    if time_per_div is not None:
        config_params["time_per_div"] = time_per_div
    if trigger_level is not None:
        config_params["trigger_level"] = trigger_level
    if trigger_source is not None:
        config_params["trigger_source"] = trigger_source
    if trigger_slope is not None:
        config_params["trigger_slope"] = trigger_slope
    if capture_mode is not None:
        config_params["capture_mode"] = capture_mode
    if coupling is not None:
        config_params["coupling"] = coupling
    if enable is not None:
        config_params["enable"] = enable

    data = {
        "action": "stream_config",
        "params": config_params,
    }

    run_python_internal(
        ctx,
        get_impl_path("scope_stream.py"),
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