"""
    Logic commands (using local nets)
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

LOGIC_ROLE = "logic"


# ---------- helpers ----------

def _require_netname(ctx) -> str:
    netname = getattr(ctx.obj, "netname", None)
    if not netname:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager logic <NETNAME> <COMMAND>\n"
            "Example: lager logic logic1 disable"
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


def _list_logic_nets(ctx, box):
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == LOGIC_ROLE]


def validate_net(ctx, box, netname, net_role):
    """Validate that a net exists and has the specified role using locally saved nets"""
    nets = _run_net_py(ctx, box, "list")
    for net in nets:
        if net.get("name") == netname and net.get("role") == net_role:
            return True
    return False


def display_nets(ctx, box, netname: str | None):
    nets = _list_logic_nets(ctx, box)
    if not nets:
        click.echo("No logic nets found on this gateway.")
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

# ---------- CLI ----------

@click.group(invoke_without_command=True)
@click.argument("NETNAME", required=False)
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
def logic(ctx, box, dut, netname):
    """
        Control logic analyzer channels and triggers
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'logic')

    if netname is not None:
        ctx.obj.netname = netname

    if ctx.invoked_subcommand is None:
        gw = _resolve_gateway(ctx, box, dut)
        display_nets(ctx, gw, None)    


def _run_backend(ctx, dut, action: str, **params):
    """Run backend command for logic operations"""
    data = {
        "action": action,
        "mcu": params.pop("mcu", None),
        "params": params,
    }
    run_python_internal(
        ctx,
        get_impl_path("enable_disable.py"),
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


@logic.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
@click.option("--mcu", required=False)
def disable(ctx, box, dut, mcu):
    """
        Disable Net
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "disable_net", netname=netname, mcu=mcu)    

@logic.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
@click.option("--mcu", required=False)
def enable(ctx, box, dut, mcu):
    """
        Enable Net
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "enable_net", netname=netname, mcu=mcu) 

@logic.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
@click.option("--mcu", required=False)
def start(ctx, box, dut, mcu):
    """
        Start waveform capture
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "start_capture", netname=netname, mcu=mcu) 

@logic.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
@click.option("--mcu", required=False)
def start_single(ctx, box, dut, mcu):
    """
        Start a single waveform capture
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "start_single", netname=netname, mcu=mcu)

@logic.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
@click.option("--mcu", required=False)
def stop(ctx, box, dut, mcu):
    """
        Stop waveform capture
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_backend(ctx, gateway, "stop_capture", netname=netname, mcu=mcu)


@logic.group()
def measure():
    """
        Measure characteristics of logic nets
    """    
    pass

def _run_measurement_backend(ctx, dut, action: str, **params):
    """Run backend command for measurement operations"""
    data = {
        "action": action,
        "mcu": params.pop("mcu", None),
        "params": params,
    }
    run_python_internal(
        ctx,
        get_impl_path("measurement.py"),
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


def _run_trigger_backend(ctx, dut, action: str, **params):
    """Run backend command for trigger operations"""
    data = {
        "action": action,
        "mcu": params.pop("mcu", None),
        "params": params,
    }
    run_python_internal(
        ctx,
        get_impl_path("trigger.py"),
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


def _run_cursor_backend(ctx, dut, action: str, **params):
    """Run backend command for cursor operations"""
    data = {
        "action": action,
        "mcu": params.pop("mcu", None),
        "params": params,
    }
    run_python_internal(
        ctx,
        get_impl_path("cursor.py"),
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


@measure.command()
@click.pass_context
@click.option("--mcu", required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="ID of DUT")
@click.option("--display", default=False, type=click.BOOL, help="Display measurement on screen")
@click.option("--cursor", default=False, type=click.BOOL, help="Enable measurement cursor")
def period(ctx, mcu, box, dut, display, cursor):
    """
    Measure period of captured net waveform
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_measurement_backend(ctx, dut, "measure_period", netname=netname, display=display, cursor=cursor, mcu=mcu)

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def freq(ctx, mcu, box, dut, display, cursor):
    """
    Measure frequency of captured net waveform
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_measurement_backend(ctx, dut, "measure_freq", netname=netname, display=display, cursor=cursor, mcu=mcu)

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def dc_pos(ctx, mcu, box, dut, display, cursor):
    """
    Measure positive duty cycle
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_measurement_backend(ctx, dut, "measure_dc_pos", netname=netname, display=display, cursor=cursor, mcu=mcu)

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def dc_neg(ctx, mcu, box, dut, display, cursor):
    """
    Measure negative duty cycle
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_measurement_backend(ctx, dut, "measure_dc_neg", netname=netname, display=display, cursor=cursor, mcu=mcu)

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def pw_pos(ctx, mcu, box, dut, display, cursor):
    """
    Measure positive pulse width
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_measurement_backend(ctx, dut, "measure_pw_pos", netname=netname, display=display, cursor=cursor, mcu=mcu)

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def pw_neg(ctx, mcu, box, dut, display, cursor):
    """
    Measure negative pulse width
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_measurement_backend(ctx, dut, "measure_pw_neg", netname=netname, display=display, cursor=cursor, mcu=mcu)


@logic.group()
def trigger():
    """
        Set up trigger properties for logic nets
    """    
    pass


MODE_CHOICES = click.Choice(('normal', 'auto', 'single'))
COUPLING_CHOICES = click.Choice(('dc', 'ac', 'low_freq_rej', 'high_freq_rej'))

@trigger.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source', required=False, help='Trigger source', metavar='NET')
@click.option('--slope', type=click.Choice(('rising', 'falling', 'both')), help='Trigger slope')
@click.option('--level', type=click.FLOAT, help='Trigger level')
def edge(ctx, mcu, box, dut, mode, coupling, source, slope, level):
    """
    Set edge trigger
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_trigger_backend(ctx, dut, "trigger_edge", netname=netname, mode=mode, coupling=coupling, source=source, slope=slope, level=level, mcu=mcu)


@trigger.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source', required=False, help='Trigger source', metavar='NET')
@click.option('--level', type=click.FLOAT, help='Trigger level')
@click.option('--trigger-on', type=click.Choice(('gt', 'lt', 'gtlt')), help='Trigger on')
@click.option('--upper', type=click.FLOAT, help='upper width')
@click.option('--lower', type=click.FLOAT, help='lower width')
def pulse(ctx, mcu, box, dut, mode, coupling, source, level, trigger_on, upper, lower):
    """
    Set pulse trigger
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_trigger_backend(ctx, dut, "trigger_pulse", netname=netname, mode=mode, coupling=coupling, source=source, level=level, trigger_on=trigger_on, upper=upper, lower=lower, mcu=mcu)    

@trigger.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode, e.g. Normal, Automatic, or Single Shot', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source-scl', required=False, help='Trigger source', metavar='NET')
@click.option('--source-sda', required=False, help='Trigger source', metavar='NET')
@click.option('--level-scl', type=click.FLOAT, help='Trigger scl level')
@click.option('--level-sda', type=click.FLOAT, help='Trigger sda level')
@click.option('--trigger-on', type=click.Choice(('start', 'restart', 'stop', 'nack', 'address', 'data', 'addr_data')), help='Trigger on')
@click.option('--address', type=click.INT, help='Address value to trigger on in ADDRESS mode')
@click.option('--addr-width', type=click.Choice(('7', '8', '9', '10')), help='Address width in bits')
@click.option('--data', type=click.INT, help='Data value to trigger on in DATA mode')
@click.option('--data-width', type=click.Choice(('1', '2', '3', '4', '5')), help='Data width in bytes')
@click.option('--direction', type=click.Choice(('write', 'read', 'rw')), help='Direction to trigger on')
def i2c(ctx, box, dut, mcu, mode, coupling, source_scl, level_scl, source_sda, level_sda, trigger_on, address, addr_width, data, data_width, direction):
    """
    Set I2C trigger
    """
    if addr_width is not None:
        addr_width = int(addr_width)
    if data_width is not None:
        data_width = int(data_width)

    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_trigger_backend(ctx, dut, "trigger_i2c", netname=netname, mode=mode, coupling=coupling, source_scl=source_scl, source_sda=source_sda, level_scl=level_scl, level_sda=level_sda, trigger_on=trigger_on, address=address, addr_width=addr_width, data=data, data_width=data_width, direction=direction, mcu=mcu)    

@trigger.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode, e.g. Normal, Automatic, or Single Shot', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source', required=False, help='Trigger source', metavar='NET')
@click.option('--level', type=click.FLOAT, help='Trigger level')
@click.option('--trigger-on', type=click.Choice(('start', 'error', 'cerror', 'data')), help='Trigger on')
@click.option('--parity', type=click.Choice(('even', 'odd', 'none')), help='Data trigger parity')
@click.option('--stop-bits', type=click.Choice(('1', '1.5', '2')), help='Data trigger stop bits')
@click.option('--baud', type=click.INT, help='Data trigger baud')
@click.option('--data-width', type=click.INT, help='Data trigger data width in bits')
@click.option('--data', type=click.INT, help='Data trigger data')
def uart(ctx, box, dut, mcu, mode, coupling, source, level, trigger_on, parity, stop_bits, baud, data_width, data):
    """
    Set UART trigger
    """
    if stop_bits is not None:
        stop_bits = float(stop_bits)

    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_trigger_backend(ctx, dut, "trigger_uart", netname=netname, mode=mode, coupling=coupling, source=source, level=level, trigger_on=trigger_on, parity=parity, stop_bits=stop_bits, baud=baud, data_width=data_width, data=data, mcu=mcu)

@trigger.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode, e.g. Normal, Automatic, or Single Shot', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source-mosi-miso', required=False, help='Trigger master/slave data source', metavar='NET')
@click.option('--source-sck', required=False, help='Trigger clock source', metavar='NET')
@click.option('--source-cs', required=False, help='Trigger chip select source', metavar='NET')
@click.option('--level-mosi-miso', type=click.FLOAT, help='Trigger mosi/miso level')
@click.option('--level-sck', type=click.FLOAT, help='Trigger sck level')
@click.option('--level-cs', type=click.FLOAT, help='Trigger cs level')
@click.option('--data', type=click.INT, help='Trigger data value')
@click.option('--data-width', type=click.INT, help='Data width in bits')
@click.option('--clk-slope', type=click.Choice(('positive', 'negative')), help='Slope of clock edge to sample data')
@click.option('--trigger-on', type=click.Choice(('timeout', 'cs')), help='Trigger on')
@click.option('--cs-idle', type=click.Choice(('high', 'low')), help='CS Idle type')
@click.option('--timeout', type=click.FLOAT, help='Timeout length')
def spi(ctx, box, dut, mcu, mode, coupling, source_mosi_miso, source_sck, source_cs, level_mosi_miso, level_sck, level_cs, data, data_width, clk_slope, trigger_on, cs_idle, timeout):
    """
    Set SPI trigger
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_trigger_backend(ctx, dut, "trigger_spi", netname=netname, mode=mode, coupling=coupling, source_mosi_miso=source_mosi_miso, source_sck=source_sck, source_cs=source_cs, level_mosi_miso=level_mosi_miso, level_sck=level_sck, level_cs=level_cs, data=data, data_width=data_width, clk_slope=clk_slope, trigger_on=trigger_on, cs_idle=cs_idle, timeout=timeout, mcu=mcu) 

@logic.group()
def cursor():
    """
        Move scope cursor on a given net
    """    
    pass

@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--x', required=False, type=click.FLOAT, help='cursor a x coordinate')
@click.option('--y', required=False, type=click.FLOAT, help='cursor a y coordinate')
def set_a(ctx, box, dut, mcu, x, y):
    """
        Set cursor a's x position
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_cursor_backend(ctx, dut, "set_a", netname=netname, x=x, y=y, mcu=mcu)

@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--x', required=False, type=click.FLOAT, help='cursor b x coordinate')
@click.option('--y', required=False, type=click.FLOAT, help='cursor b y coordinate')
def set_b(ctx, box, dut, mcu, x, y):
    """
        Set cursor b's x position
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_cursor_backend(ctx, dut, "set_b", netname=netname, x=x, y=y, mcu=mcu)

@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--del-x', required=False, type=click.FLOAT, help='shift a\'s x coordinate')
@click.option('--del-y', required=False, type=click.FLOAT, help='shift a\'s y coordinate')
def move_a(ctx, box, dut, mcu, del_x, del_y):
    """
        Shift cursor a's  position
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_cursor_backend(ctx, dut, "move_a", netname=netname, del_x=del_x, del_y=del_y, mcu=mcu)

@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--del-x', required=False, type=click.FLOAT, help='shift b\'s x coordinate')
@click.option('--del-y', required=False, type=click.FLOAT, help='shift b\'s y coordinate')
def move_b(ctx, box, dut, mcu, del_x, del_y):
    """
        Shift cursor b's position
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_cursor_backend(ctx, dut, "move_b", netname=netname, del_x=del_x, del_y=del_y, mcu=mcu)

@cursor.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--mcu', required=False)
def hide(ctx, box, dut, mcu):
    """
        Hide cursor
    """
    gateway = _resolve_gateway(ctx, box, dut)
    netname = _require_netname(ctx)

    if not validate_net(ctx, box, netname, LOGIC_ROLE):
        click.secho(f"{netname} is not a logic net", fg="red", err=True)
        return

    _run_cursor_backend(ctx, dut, "hide_cursor", netname=netname, mcu=mcu)