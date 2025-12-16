import os
import io
import json
from pathlib import Path
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_default_net, get_impl_path
from ..python.commands import run_python_internal

ADC_ROLE = "adc"


def _impl_adc_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "impl" / "adc.py")


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


def _list_adc_nets(ctx, box):
    """Get list of ADC nets from gateway."""
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == ADC_ROLE]


def _display_adc_nets(ctx, box):
    """Display ADC nets in a table."""
    nets = _list_adc_nets(ctx, box)
    if not nets:
        click.echo("No ADC nets found on this gateway.")
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


@click.command(name="adc", help="Read voltage from ADC net")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def adc(ctx, box, dut, netname):
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'adc')

    # If still no netname, list available ADC nets
    if netname is None:
        gateway = _resolve_gateway(ctx, box, dut)
        _display_adc_nets(ctx, gateway)
        return

    gateway = _resolve_gateway(ctx, box, dut)
    gateway_image = os.environ.get("LAGER_GATEWAY_IMAGE", "python")

    payload = json.dumps({"netname": netname})

    run_python_internal(
        ctx=ctx,
        runnable=_impl_adc_path(),
        box=gateway,
        image=gateway_image,
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum="SIGTERM",
        timeout=None,
        detach=False,
        port=(),
        org=None,
        args=[payload],
    )