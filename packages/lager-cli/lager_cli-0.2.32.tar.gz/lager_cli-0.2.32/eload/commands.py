"""Electronic Load CLI commands."""

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

ELOAD_ROLE = "eload"


def _resolve_gateway(ctx, box, dut):
    """Resolve DUT name to IP address if it's a local DUT."""
    from ..dut_storage import resolve_and_validate_dut

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


def _list_eload_nets(ctx, box):
    """Get list of electronic load nets from gateway."""
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == ELOAD_ROLE]


def _display_eload_nets(ctx, box):
    """Display electronic load nets in a table."""
    nets = _list_eload_nets(ctx, box)
    if not nets:
        click.echo("No electronic load nets found on this gateway.")
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


def _run_eload_script(ctx, box: str, args: list):
    """Run eload implementation script with proper arguments."""
    run_python_internal(
        ctx,
        get_impl_path('eload.py'),
        box,
        image='',
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum='SIGTERM',
        timeout=0,
        detach=False,
        port=(),
        org=None,
        args=tuple(args),
    )


@click.group(invoke_without_command=True)
@click.argument('netname', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def eload(ctx, netname, box, dut):
    """Control electronic load settings and modes"""
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'eload')

    if netname is not None:
        ctx.obj.netname = netname

    # If no subcommand and no netname, list nets
    if ctx.invoked_subcommand is None:
        gateway = _resolve_gateway(ctx, box, dut)
        _display_eload_nets(ctx, gateway)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cc(ctx, value, box, dut):
    """Set (or read) constant current mode in amps (A)"""
    resolved_dut = _resolve_gateway(ctx, box, dut)
    netname = ctx.obj.netname
    args = ["cc", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cv(ctx, value, box, dut):
    """Set (or read) constant voltage mode in volts (V)"""
    resolved_dut = _resolve_gateway(ctx, box, dut)
    netname = ctx.obj.netname
    args = ["cv", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cr(ctx, value, box, dut):
    """Set (or read) constant resistance mode in ohms (Ω)"""
    resolved_dut = _resolve_gateway(ctx, box, dut)
    netname = ctx.obj.netname
    args = ["cr", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def cp(ctx, value, box, dut):
    """Set (or read) constant power mode in watts (W)"""
    resolved_dut = _resolve_gateway(ctx, box, dut)
    netname = ctx.obj.netname
    args = ["cp", netname]
    if value is not None:
        args.append(str(value))
    _run_eload_script(ctx, resolved_dut, args)


@eload.command()
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def state(ctx, box, dut):
    """Display electronic load state"""
    resolved_dut = _resolve_gateway(ctx, box, dut)
    netname = ctx.obj.netname
    args = ["state", netname]
    _run_eload_script(ctx, resolved_dut, args)
