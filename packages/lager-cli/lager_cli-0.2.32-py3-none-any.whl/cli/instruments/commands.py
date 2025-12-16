"""
    lager.instruments.commands

    Instruments commands
"""
import click
import json
from texttable import Texttable
from ..context import get_impl_path
from ..python.commands import run_python_internal
from ..context import get_default_gateway
from ..dut_storage import resolve_and_validate_dut
from collections import defaultdict

import io
from contextlib import redirect_stdout

_MULTI_HUBS = {"LabJack_T7", "Acroname_8Port", "Acroname_4Port"}

@click.command()
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.pass_context
def instruments(ctx, box: str | None, dut: str | None = None) -> None:
    """List attached instruments"""
    # Resolve and validate the box/dut name
    box_name = box or dut
    dut = resolve_and_validate_dut(ctx, box_name)

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path("query_instruments.py"),
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
                args=(),
            )
    except SystemExit:
        pass

    try:
        instruments_data = json.loads(buf.getvalue() or "[]")
    except json.JSONDecodeError:
        click.secho(
            "Could not parse instrument data returned by query_instruments.py",
            fg="red",
            err=True,
        )
        ctx.exit(1)

    if not instruments_data:
        click.echo("No instruments detected.")
        return

    inst_counts: dict[str, int] = defaultdict(int)
    for dev in instruments_data:
        inst_counts[dev.get("name")] += 1

    duplicated: set[str] = {
        name for name, cnt in inst_counts.items()
        if name in _MULTI_HUBS and cnt > 1
    }

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["l", "l", "l"])
    table.set_cols_dtype(["t", "t", "t"])
    table.set_cols_width([22, 60, 45])

    table.add_row(["Name", "Channels", "VISA Address"])

    for dev in instruments_data:
        if dev.get("name") in duplicated:
            continue

        chan_map = dev.get("channels", {})
        if chan_map:
            lines = []
            for role, chs in chan_map.items():
                if chs:
                    # Truncate UART serial numbers to 10 chars to reduce clutter
                    if role == "uart":
                        chs_display = [ch[:10] if len(ch) > 10 else ch for ch in chs]
                    else:
                        chs_display = chs
                    lines.append(f"{role}: {', '.join(chs_display)}")
                else:
                    lines.append(f"{role}: —")
            channels_str = "\n".join(lines)
        else:
            channels_str = "—"

        table.add_row(
            [
                dev.get("name", "—"),
                channels_str,
                dev.get("address", "—"),
            ]
        )

    rendered = table.draw().splitlines()
    if len(rendered) > 1:
        rendered.insert(1, "")
    click.secho("\n".join(rendered), fg="green")

    for name in sorted(duplicated):
        click.secho(
            f"Multiple {name} devices detected – unplug extras before adding nets.",
            fg="yellow",
        )