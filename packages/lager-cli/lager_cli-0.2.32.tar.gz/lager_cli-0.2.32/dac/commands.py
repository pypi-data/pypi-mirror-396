import os
import io
import json
from pathlib import Path
from contextlib import redirect_stdout

import click
from texttable import Texttable
from ..context import get_default_gateway, get_default_net, get_impl_path
from ..python.commands import run_python_internal

DAC_ROLE = "dac"


def _impl_dac_path() -> str:
    """Construct path to the implementation script for DAC."""
    return str(Path(__file__).resolve().parent.parent / "impl" / "dac.py")


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


def _list_dac_nets(ctx, box):
    """Get list of DAC nets from gateway."""
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == DAC_ROLE]


def _display_dac_nets(ctx, box):
    """Display DAC nets in a table."""
    nets = _list_dac_nets(ctx, box)
    if not nets:
        click.echo("No DAC nets found on this gateway.")
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


@click.command(name="dac", help="Set or read DAC output voltage")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.argument("netname", required=False)
@click.argument("voltage", required=False)
def dac(ctx, box, dut, netname, voltage):
    """
    Set the digital-to-analog converter for a net on the DUT (value in volts).
    If no voltage is provided, this command reads the current DAC value.
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'dac')

    # If still no netname, list available DAC nets
    if netname is None:
        gateway = _resolve_gateway(ctx, box, dut)
        _display_dac_nets(ctx, gateway)
        return

    # Validate voltage if provided
    if voltage is not None and voltage.strip() == "":
        click.secho("Error: Voltage argument cannot be empty", fg='red', err=True)
        click.secho("Usage: lager dac <netname> [voltage]", fg='yellow', err=True)
        ctx.exit(1)

    gateway = _resolve_gateway(ctx, box, dut)
    gateway_image = os.environ.get("LAGER_GATEWAY_IMAGE", "python")
    payload = {"netname": netname}
    if voltage is not None:
        payload["voltage"] = voltage
    payload_json = json.dumps(payload)
    run_python_internal(
        ctx=ctx,
        runnable=_impl_dac_path(),
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
        args=[payload_json],
    )