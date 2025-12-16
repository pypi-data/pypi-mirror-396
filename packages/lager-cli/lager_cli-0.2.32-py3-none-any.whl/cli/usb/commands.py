from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import click
from texttable import Texttable

from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

USB_ROLE = "usb"


# --------------------------------------------------------------------------- #
# helper: run the impl script on the remote gateway
# --------------------------------------------------------------------------- #
def _resolve_gateway(ctx: click.Context, dut: str | None) -> str:
    """
    Resolve DUT name to IP address if it's a local DUT, otherwise return as-is.
    """
    from ..dut_storage import resolve_and_validate_dut

    return resolve_and_validate_dut(ctx, dut)


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


def _list_usb_nets(ctx, box):
    """Get list of USB nets from gateway."""
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == USB_ROLE]


def _display_usb_nets(ctx, box):
    """Display USB nets in a table."""
    nets = _list_usb_nets(ctx, box)
    if not nets:
        click.echo("No USB nets found on this gateway.")
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


def _invoke_remote(
    ctx: click.Context,
    net_name: str,
    dut: str | None,
    command: str,
) -> None:
    """
    Copy `impl/usb.py` to the requested gateway and run:

        python usb.py <command> <net_name>

    The impl in turn invokes the backend dispatcher inside the gateway
    container.
    """
    resolved_dut = _resolve_gateway(ctx, dut)

    run_python_internal(
        ctx,
        get_impl_path("usb.py"),
        box=resolved_dut,
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
        args=(command, net_name),
    )


# --------------------------------------------------------------------------- #
# single command (verb comes **after** the net name)
# --------------------------------------------------------------------------- #
@click.command(
    "usb",
    help="Control programmable USB hub ports",
)
@click.argument("net_name", metavar="NET_NAME", required=False)
@click.argument(
    "command",
    metavar="COMMAND",
    type=click.Choice(["enable", "disable", "toggle"], case_sensitive=False),
    required=False,
)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def usb(
    ctx: click.Context,
    net_name: str | None,
    command: str | None,
    box: str | None,
    dut: str | None,
) -> None:  # pragma: no cover
    """
    Examples
    --------
    >>> lager usb --box DUT                # List all USB nets
    >>> lager usb usb1 enable  --box DUT
    >>> lager usb usb1 toggle  --box DUT
    >>> lager usb usb1 disable --box DUT
    """
    # Use provided net_name, or fall back to default if not provided
    if net_name is None:
        net_name = get_default_net(ctx, 'usb')

    # If still no net_name, list available USB nets
    if net_name is None:
        resolved_dut = _resolve_gateway(ctx, box or dut)
        _display_usb_nets(ctx, resolved_dut)
        return

    # If we have a net but no command, show error
    if command is None:
        raise click.UsageError(
            "COMMAND required.\n\n"
            "Usage: lager usb <NET_NAME> <COMMAND>\n"
            "Example: lager usb usb1 enable --box mybox"
        )

    # Use box or dut (box takes precedence)
    resolved_dut = box or dut
    _invoke_remote(ctx, net_name, resolved_dut, command.lower())