"""
nets_commands.py – "lager nets …" CLI group
-------------------------------------------
List all saved nets
"""

from __future__ import annotations

import io
import json
import re
from contextlib import redirect_stdout
from typing import Any, List, Optional
from collections import defaultdict

import click
from texttable import Texttable
import shutil

from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from .net_tui import launch_tui


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _parse_backend_json(raw: str) -> Any:
    """
    Parse JSON response from backend, handling duplicate output from double execution.

    Args:
        raw: Raw output from backend

    Returns:
        Parsed JSON data

    Raises:
        json.JSONDecodeError: If JSON cannot be parsed
    """
    try:
        return json.loads(raw or "[]")
    except json.JSONDecodeError:
        # Handle duplicate JSON output from backend double execution
        if raw and raw.count('[') >= 2:
            # Try to extract the first JSON array
            depth = 0
            first_array_end = -1
            for i, char in enumerate(raw):
                if char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
                    if depth == 0:
                        first_array_end = i + 1
                        break

            if first_array_end > 0:
                first_json = raw[:first_array_end]
                return json.loads(first_json)
            else:
                raise json.JSONDecodeError("Could not find complete JSON array", raw, 0)
        else:
            # Handle duplicate JSON objects (e.g., {"ok": true}{"ok": true})
            if raw and raw.count('{') >= 2:
                depth = 0
                first_obj_end = -1
                for i, char in enumerate(raw):
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            first_obj_end = i + 1
                            break

                if first_obj_end > 0:
                    first_json = raw[:first_obj_end]
                    return json.loads(first_json)

            raise  # Re-raise original exception

_MULTI_HUBS = {"LabJack_T7", "Acroname_8Port", "Acroname_4Port"}
_SINGLE_CHANNEL_INST = {
    "Keithley_2281S": ("batt", "supply"),
    "EA_PSB_10060_60": ("solar", "supply"),
    "EA_PSB_10080_60": ("solar", "supply"),
}
INSTRUMENT_NET_MAP: dict[str, list[str]] = {
    # supply
    "Rigol_DP811": ["supply"],
    "Rigol_DP821": ["supply"],
    "Rigol_DP831": ["supply"],
    "EA_PSB_10080_60": ["supply", "solar"],
    "EA_PSB_10060_60": ["supply", "solar"],
    "KEYSIGHT_E36233A": ["supply"],
    "KEYSIGHT_E36313A": ["supply"],

    # batt
    "Keithley_2281S": ["batt", "supply"],

    # scope
    "Rigol_MS05204": ["scope"],
    "Picoscope_2000": ["scope"],

    # adc / gpio / dac
    "LabJack_T7": ["gpio", "adc", "dac"],

    # debug
    "J-Link": ["debug"],
    "J-Link_Plus": ["debug"],
    "Flasher_ARM": ["debug"],

    # usb
    "Acroname_8Port": ["usb"],
    "Acroname_4Port": ["usb"],
    "YKUSH_Hub": ["usb"],

    # eload
    "Rigol_DL3021": ["eload"],

    # camera
    "Logitech_BRIO_HD": ["camera"],
    "Logitech_BRIO": ["camera"],

    # (robot) arm
    "Rotrix_Dexarm": ["arm"],

    # watt-meter
    "Yocto_Watt": ["watt-meter"],

    # uart
    "Prolific_USB_Serial": ["uart"],
    "SiLabs_CP210x": ["uart"],
    "FTDI_FT232R": ["uart"],
    "FTDI_FT4232H": ["uart"],
    "ESP32_JTAG_Serial": ["uart"],
}

def _run_net_py(ctx: click.Context, dut: str, *net_args: str) -> str:
    """
    Run `net.py …` via run_python_internal and capture stdout.
    """
    from ..python.commands import run_python_internal_get_output

    try:
        output = run_python_internal_get_output(
            ctx,
            get_impl_path("net.py"),
            dut,
            image="",
            env=(),
            passenv=(),
            kill=False,
            download=(),
            allow_overwrite=False,
            signum="SIGTERM",
            timeout=30,  # 30 second timeout to prevent hanging
            detach=False,
            port=(),
            org=None,
            args=net_args,
        )
        return output.decode('utf-8') if isinstance(output, bytes) else output
    except SystemExit:
        return ""


def _resolve_dut(ctx: click.Context, dut_opt: Optional[str] = None) -> str:
    """
    Resolve DUT precedence:
    1. explicit --dut given to this sub-command (check local DUTs first)
    2. --dut passed to the *parent* ("nets …") command (check local DUTs first)
    3. get_default_gateway(ctx) (automatically resolves local DUT names)
    """
    import ipaddress
    from ..dut_storage import get_dut_ip, list_duts

    target_dut = None
    if dut_opt:
        target_dut = dut_opt
    elif ctx.parent is not None and "dut" in ctx.parent.params and ctx.parent.params["dut"]:
        target_dut = ctx.parent.params["dut"]

    if target_dut:
        # Check if this is a local DUT name first
        local_ip = get_dut_ip(target_dut)
        if local_ip:
            return local_ip

        # Check if it looks like an IP address
        try:
            ipaddress.ip_address(target_dut)
            # It's a valid IP address, use it directly
            return target_dut
        except ValueError:
            # Not a valid IP and not in local DUTs
            # Show helpful error message
            click.secho(f"Error: DUT '{target_dut}' is not recorded in the system.", fg='red', err=True)
            click.echo("", err=True)

            saved_duts = list_duts()
            if saved_duts:
                click.echo("Available DUTs:", err=True)
                for name, ip in saved_duts.items():
                    if isinstance(ip, dict):
                        ip = ip.get('ip', 'unknown')
                    click.echo(f"  - {name} ({ip})", err=True)
            else:
                click.echo("No DUTs are currently saved.", err=True)

            click.echo("", err=True)
            click.echo("To add a new box, use:", err=True)
            click.echo(f"  lager boxes add --name {target_dut} --ip <IP_ADDRESS>", err=True)
            ctx.exit(1)

    # get_default_gateway already handles local DUT resolution
    return get_default_gateway(ctx)

def _natural_sort_key(text):
    """
    Convert a string into a list of mixed strings and integers for natural sorting.
    This makes "adc2" come before "adc10" instead of alphabetical order.

    Examples:
        "adc1" -> ["adc", 1]
        "adc10" -> ["adc", 10]
        "uart2" -> ["uart", 2]
    """
    def atoi(s):
        return int(s) if s.isdigit() else s
    return [atoi(c) for c in re.split(r'(\d+)', text)]

def _display_table(records):

    # ----- sort records: first by net type, then by name (with natural sorting) -------------------------
    sorted_records = sorted(records, key=lambda r: (r.get("role", ""), _natural_sort_key(r.get("name", ""))))

    # ----- gather table data -------------------------------------------------
    headers = ["Name", "Net Type", "Instrument", "Channel", "Address"]
    rows = []
    for rec in sorted_records:
        pin = rec.get("pin", "") or ""
        # Truncate UART serial numbers to 10 chars to reduce clutter
        if rec.get("role") == "uart" and len(pin) > 10:
            pin = pin[:10]
        rows.append([
            rec.get("name", ""),
            rec.get("role", ""),
            rec.get("instrument", "") or "",
            pin,
            rec.get("address", "") or "",
        ])

    if not rows:
        click.secho("No saved nets found.", fg="yellow")
        return

    # ----- compute column widths --------------------------------------------
    term_w = shutil.get_terminal_size((120, 24)).columns
    min_w = [8, 10, 14, 7]
    col_w = [
        max(min_w[i], max(len(str(r[i])) for r in rows))
        for i in range(4)
    ]
    used = sum(col_w) + 4 * 2
    addr_w = max(20, term_w - used - 2)
    col_w.append(addr_w)

    # ----- helper to format one row -----------------------------------------
    def fmt(row):
        return (
            f"{row[0]:<{col_w[0]}}  "
            f"{row[1]:<{col_w[1]}}  "
            f"{row[2]:<{col_w[2]}}  "
            f"{row[3]:<{col_w[3]}}  "
            f"{row[4]:<{col_w[4]}}"
        )

    # ----- output ------------------------------------------------------------
    total_width = sum(col_w) + 8  # 8 = 4 columns * 2 spaces each
    click.echo(fmt(headers))
    click.echo("=" * total_width)
    for row in rows:
        click.echo(fmt(row))

def _list_nets(ctx: click.Context, dut: str) -> None:
    """
    Fetch nets via net.py and print the table.
    """
    raw = _run_net_py(ctx, dut, "list")
    try:
        records: List[dict[str, Any]] = _parse_backend_json(raw)
    except json.JSONDecodeError:
        click.secho("Failed to parse response from backend.", fg="red", err=True)
        if not raw:
            click.secho("No output received from backend. Please ensure you are logged in with 'lager login'.", fg="yellow", err=True)
        else:
            click.secho(f"Raw output: {repr(raw)}", fg="yellow", err=True)
        ctx.exit(1)

    _display_table(records)

def _save_nets_batch(ctx: click.Context, dut: str, nets_data: List[dict]) -> None:
    """
    Save multiple nets using batch save functionality, with fallback to individual saves.
    """
    if not nets_data:
        return

    # Try batch save first
    try:
        raw = _run_net_py(ctx, dut, "save-batch", json.dumps(nets_data))

        if raw and raw.strip():
            response = _parse_backend_json(raw)
            # Check if response is a dict with expected format
            if isinstance(response, dict) and response.get("ok", False):
                count = response.get("count", len(nets_data))
                click.secho(f"Successfully saved {count} nets using batch save on DUT {dut}.", fg="green")
                return
        else:
            pass
    except (json.JSONDecodeError, Exception) as e:
        click.secho(f"Batch save failed, falling back to individual saves: {e}", fg="yellow", err=True)

    # Fallback to individual saves
    click.secho(f"Using individual saves for {len(nets_data)} nets...", fg="yellow", err=True)
    saved_count = 0

    for net_data in nets_data:
        try:
            raw = _run_net_py(ctx, dut, "save", json.dumps(net_data))
            saved_count += 1
        except Exception as e:
            click.secho(f"Failed to save net '{net_data.get('name', 'unknown')}': {e}", fg="red", err=True)

    click.secho(f"Successfully saved {saved_count} of {len(nets_data)} nets on DUT {dut}.", fg="green")

# --------------------------------------------------------------------------- #
# Top-level group                                                             #
# --------------------------------------------------------------------------- #
@click.group(
    name="nets",
    invoke_without_command=True,
    help="List all saved nets.",
)
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.pass_context
def nets(ctx: click.Context, box: str | None, dut: str | None) -> None:  # noqa: D401
    """
    If no sub-command is supplied, default to "list".
    """
    # Resolve box/dut (box takes precedence, dut is for backward compatibility)
    dut = box or dut

    if ctx.invoked_subcommand is None:
        _list_nets(ctx, _resolve_dut(ctx, dut))


# --------------------------------------------------------------------------- #
# Sub-commands                                                                #
# --------------------------------------------------------------------------- #

@nets.command("delete", help="Delete one saved net by name and type.")
@click.argument("name")
@click.argument("net_type")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_cmd(
    ctx: click.Context, name: str, net_type: str, box: str | None, dut: str | None, yes: bool
) -> None:
    # Use box or dut (box takes precedence)
    resolved = box or dut
    dut = _resolve_dut(ctx, resolved)
    raw = _run_net_py(ctx, dut, "list")
    try:
        recs = _parse_backend_json(raw)
    except json.JSONDecodeError:
        click.secho("Failed to parse response from backend.", fg="red", err=True)
        if not raw:
            click.secho("No output received from backend. Please ensure you are logged in with 'lager login'.", fg="yellow", err=True)
        else:
            click.secho(f"Raw output: {repr(raw)}", fg="yellow", err=True)
        ctx.exit(1)

    match = [r for r in recs if r.get("name") == name and r.get("role") == net_type]
    if not match:
        click.secho(f"Net '{name}' ({net_type}) not found on {dut}.", fg="yellow")
        ctx.exit(1)

    if not yes and not click.confirm(
        f"Delete net '{name}' ({net_type}) on DUT {dut}?"
    ):
        click.secho("Aborted.", fg="yellow")
        return

    _run_net_py(ctx, dut, "delete", name, net_type)
    click.secho(f"Deleted '{name}' ({net_type}) on DUT {dut}.", fg="green")


@nets.command("delete-all", help="Dangerous – delete every saved net.")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_all_cmd(ctx: click.Context, box: str | None, dut: str | None, yes: bool) -> None:
    # Use box or dut (box takes precedence)

    resolved = box or dut

    dut = _resolve_dut(ctx, resolved)

    if not yes and not click.confirm(
        f"Delete ALL saved nets on DUT {dut}? This cannot be undone."
    ):
        click.secho("Aborted.", fg="yellow")
        return

    _run_net_py(ctx, dut, "delete-all")
    click.secho(f"Deleted all nets on DUT {dut}.", fg="green")


@nets.command("tui", help="Launch the interactive Net-Manager TUI.")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.pass_context
def tui_cmd(ctx: click.Context, box: str | None, dut: str | None) -> None:
    # Use box or dut (box takes precedence)
    resolved = box or dut
    launch_tui(ctx, _resolve_dut(ctx, resolved))


# @nets.command("gui", help="Launch the interactive Net-Manager GUI.")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
# @click.pass_context
# def gui_cmd(ctx: click.Context, dut: str | None) -> None:
#     # Import GUI module only when the command is actually used
#     try:
#         from .net_gui import launch_net_gui
#         launch_net_gui(ctx, _resolve_dut(ctx, dut))
#     except ImportError as e:
#         click.secho(f"GUI module import failed: {e}", fg='red')
#         click.secho("   Try: pip install tkinter or check your Python installation", fg='yellow')
#         ctx.exit(1)


@nets.command("rename", help="Rename a saved net.")
@click.argument("name")
@click.argument("new_name")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.pass_context
def rename_cmd(
    ctx: click.Context,
    name: str,
    new_name: str,
    box: str | None,
    dut: str | None,
) -> None:
    """
    Rename a net. Prevent duplicate net names (regardless of type).
    """
    # Use box or dut (box takes precedence)

    resolved = box or dut

    dut = _resolve_dut(ctx, resolved)

    raw = _run_net_py(ctx, dut, "list")
    try:
        recs = _parse_backend_json(raw)
    except json.JSONDecodeError:
        click.secho("Failed to parse response from backend.", fg="red", err=True)
        if not raw:
            click.secho("No output received from backend. Please ensure you are logged in with 'lager login'.", fg="yellow", err=True)
        else:
            click.secho(f"Raw output: {repr(raw)}", fg="yellow", err=True)
        ctx.exit(1)

    src = next((r for r in recs if r.get("name") == name), None)
    if not src:
        click.secho(f"Net '{name}' not found on {dut}.", fg="yellow")
        ctx.exit(1)

    duplicate = next((r for r in recs if r.get("name") == new_name), None)
    if duplicate:
        click.secho(
            f"Cannot rename: a net named '{new_name}' already exists on DUT {dut}.",
            fg="red",
        )
        ctx.exit(1)

    _run_net_py(ctx, dut, "rename", name, new_name)
    click.secho(
        f"Renamed '{name}' → '{new_name}' on DUT {dut}.", fg="green"
    )

@nets.command("create")
@click.argument("name")
@click.argument("role")
@click.argument("channel")
@click.argument("address")
@click.option("--box")
@click.option("--dut")
@click.pass_context
def create_cmd(ctx, name, role, channel, address, box, dut):
    """
    Create a net using inferred instrument from VISA address.

    • The (role, instrument, channel, address) tuple must exist on DUT.
    • Only one physical hub is allowed for multi-hub instruments.
    • Single-channel instruments may only have one net at their address.
    • Net names must be globally unique (regardless of type).
    • No duplicate (role, instrument, channel, address).
    """
    from ..dut_storage import resolve_and_validate_dut

    # Resolve and validate the box/dut name
    box_name = box or dut
    gateway = resolve_and_validate_dut(ctx, box_name)

    def _run_and_json(path: str, args: tuple[str, ...] = ()) -> list:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                run_python_internal(
                    ctx, path, gateway,
                    image="", env={}, passenv=(), kill=False, download=(),
                    allow_overwrite=False, signum="SIGTERM", timeout=30,
                    detach=False, port=(), org=None, args=args,
                )
        except SystemExit:
            pass
        try:
            return json.loads(buf.getvalue() or "[]")
        except json.JSONDecodeError:
            return []

    def _get_instrument_from_address(address: str, allow_unknown: bool = False) -> str:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                run_python_internal(
                    ctx, get_impl_path("query_instruments.py"), gateway,
                    image="", env={}, passenv=(), kill=False, download=(),
                    allow_overwrite=False, signum="SIGTERM", timeout=30,
                    detach=False, port=(), org=None,
                    args=("get_instrument", address),
                )
        except SystemExit:
            pass

        try:
            result = json.loads(buf.getvalue())
        except json.JSONDecodeError:
            if not allow_unknown:
                click.secho("Invalid instrument info returned for address", fg="red")
                ctx.exit(1)
            return "Unknown_UART_Device"

        if isinstance(result, list):
            for inst in result:
                if inst.get("address") == address:
                    return inst.get("name", "Unknown")
            click.secho(f"No instrument found for address {address}", fg="red")
            if not allow_unknown:
                ctx.exit(1)
            return "Unknown_UART_Device"
        elif isinstance(result, dict) and "name" in result:
            return result["name"]

        if not allow_unknown:
            click.secho("Unexpected result format from query_instruments.py", fg="red")
            ctx.exit(1)
        return "Unknown_UART_Device"


    # ─────────── resolve instrument ─────────────
    # For UART nets, allow a direct device path (e.g., /dev/ttyUSB0) when a USB serial is unavailable.
    is_uart_device_path = (
        role == "uart" and isinstance(channel, str) and channel.startswith("/dev/")
    )

    instrument = _get_instrument_from_address(address, allow_unknown=is_uart_device_path)

    # ─────────── load devices and nets ──────────
    devs       = _run_and_json(get_impl_path("query_instruments.py"))
    saved_nets = _run_and_json(get_impl_path("net.py"), ("list",))

    # ─────────── multiple hubs restriction ──────
    if not is_uart_device_path:
        if instrument in _MULTI_HUBS:
            hub_count = sum(1 for d in devs if d.get("name") == instrument)
            if hub_count > 1:
                click.secho(
                    f"Multiple {instrument} devices detected – unplug extras before adding nets.",
                    fg="red",
                )
                ctx.exit(1)

        # ─────────── tuple must exist ───────────────
        dev_match = next((d for d in devs if d.get("address") == address), None)
        if not dev_match:
            click.secho(
                f"No instrument with address {address} is present on {gateway}.",
                fg="red",
            )
            ctx.exit(1)

        chan_map = dev_match.get("channels") or {}
        role_chans = chan_map.get(role)
    else:
        chan_map = {}
        role_chans = None

    if role == "debug":
        for net in saved_nets:
            if (
                net["role"] == "debug"
                and net["instrument"] == instrument
                and net["address"] == address
            ):
                click.secho(
                    f"A debug net already exists for instrument {instrument} at {address}.",
                    fg="red",
                )
                ctx.exit(1)
    else:
        # UART device-path mode skips channel validation because the tty path is supplied directly.
        if is_uart_device_path:
            role_chans = None
        # Normal validation for channel availability on the device
        if role_chans == "NA":
            click.secho(
                f"The role '{role}' is not available for the instrument at {address}.",
                fg="red",
            )
            ctx.exit(1)

        if role_chans:
            if isinstance(role_chans, str):
                role_chans = [s.strip() for s in role_chans.split(",")]
            elif not isinstance(role_chans, list):
                role_chans = [role_chans]

            if str(channel) not in [str(ch) for ch in role_chans]:
                click.secho(
                    f"The channel '{channel}' is not valid for role '{role}' on the instrument at {address}.",
                    fg="red",
                )
                ctx.exit(1)

    # ─────────── unique net name (regardless of type) ────────────────
    if any(n["name"] == name for n in saved_nets):
        click.secho(
            f"A net named '{name}' already exists. Net names must be globally unique.",
            fg="red",
        )
        ctx.exit(1)

    # ─────────── unique role/instrument/channel/address ──────────────
    if any(
        n["role"] == role
        and n["instrument"] == instrument
        and str(n["pin"]) == str(channel)
        and n["address"] == address
        for n in saved_nets
    ):
        click.secho(
            "A net with the same role / instrument / channel / address already exists.",
            fg="red",
        )
        ctx.exit(1)

    # ─────────── single-channel restriction ──────────────────────────
    if instrument in _SINGLE_CHANNEL_INST:
        if any(n["instrument"] == instrument and n["address"] == address for n in saved_nets):
            click.secho(
                f"Only one net may reference {instrument} at {address}.",
                fg="red",
            )
            ctx.exit(1)

    if role not in INSTRUMENT_NET_MAP.get(instrument, []) and not is_uart_device_path:
        click.secho(
                f"Instrument '{instrument}' does not support net type '{role}'",
                fg="red",
            )
        ctx.exit(1)

    # ─────────── persist new net ─────────────────────────────────────
    net_data = {
        "name":       name,
        "role":       role,
        "address":    address,
        "instrument": instrument,
        "pin":        channel,
    }
    if is_uart_device_path:
        net_data["device_path"] = channel
    try:
        _buf = io.StringIO()
        with redirect_stdout(_buf):
            run_python_internal(
                ctx,
                get_impl_path("net.py"),
                gateway,
                image="", env={}, passenv=(), kill=False, download=(),
                allow_overwrite=False, signum="SIGTERM", timeout=30,
                detach=False, port=(), org=None,
                args=(
                    "save",
                    json.dumps(net_data),
                ),
            )
    except SystemExit:
        pass

    click.secho(f"Saved new net '{name}' on {gateway}.", fg="green")


@nets.command("create-all", help="Create all possible nets that can be created on the DUT.")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def create_all_cmd(ctx: click.Context, box: str | None, dut: str | None, yes: bool) -> None:
    """
    Create all possible nets that can be created on a DUT.
    This command replicates the functionality of the 'Add Nets' page in the TUI.
    """
    # Use box or dut (box takes precedence)

    resolved = box or dut

    dut = _resolve_dut(ctx, resolved)

    def _run_and_json(script: str, *args: str) -> list:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                run_python_internal(
                    ctx, get_impl_path(script), dut,
                    image="", env={}, passenv=(), kill=False, download=(),
                    allow_overwrite=False, signum="SIGTERM", timeout=30,
                    detach=False, port=(), org=None, args=args,
                )
        except SystemExit:
            pass
        try:
            return _parse_backend_json(buf.getvalue() or "[]")
        except json.JSONDecodeError:
            return []

    def _first_word(role: str) -> str:
        """Return the first part of a hyphenated role name."""
        # Special case: power-supply nets use 'supply' prefix instead of 'power'
        if role == "power-supply":
            return "supply"
        return role.split("-")[0]

    # Get available instruments and existing nets
    inst_list = _run_and_json("query_instruments.py")
    saved_nets = _run_and_json("net.py", "list")

    if not inst_list:
        click.secho("No instruments found on the DUT.", fg="yellow")
        return

    # Generate all possible nets from instruments (without names yet)
    all_possible_nets: list[dict] = []

    for dev in inst_list:
        instr = dev.get("name", "Unknown")
        addr = dev.get("address", "NA")
        channel_map = dev.get("channels", {})

        for role, channels in (channel_map or {}).items():
            for ch in channels:
                # Special handling for UART devices:
                # For UART, the 'channels' list contains USB serial numbers
                # We store: instrument=device_name, chan=port, pin=usb_serial
                if role == "uart":
                    net_data = {
                        "instrument": instr,   # Device name (e.g., "Prolific_USB_Serial")
                        "chan": "0",          # Default port number
                        "pin": ch,            # USB serial number (e.g., "DGDIb136G04")
                        "type": role,
                        "net": None,  # Will assign name after filtering
                        "addr": addr,
                        "saved": False,
                    }
                else:
                    net_data = {
                        "instrument": instr,
                        "chan": ch,
                        "type": role,
                        "net": None,  # Will assign name after filtering
                        "addr": addr,
                        "saved": False,
                    }
                all_possible_nets.append(net_data)

    # Apply filtering logic similar to TUI's _get_addable_nets
    warnings = []

    # Check for multiple hubs of same type
    chan_seen: dict[str, set[str]] = defaultdict(set)
    duplicate_hubs: set[str] = set()
    for net in all_possible_nets:
        if net["instrument"] in _MULTI_HUBS:
            if net["chan"] in chan_seen[net["instrument"]]:
                duplicate_hubs.add(net["instrument"])
            chan_seen[net["instrument"]].add(net["chan"])

    # Filter out blocked instrument families
    filtered_nets = []
    dup_single: set[tuple[str, str]] = set()

    for net in all_possible_nets:
        # Skip if instrument family is blocked due to duplicates
        if net["instrument"] in duplicate_hubs:
            continue

        # Skip if single-channel instrument already has a net at this address
        if net["instrument"] in _SINGLE_CHANNEL_INST:
            if any(s.get("instrument") == net["instrument"] and s.get("address") == net["addr"] for s in saved_nets):
                dup_single.add((net["instrument"], net["addr"]))
                continue

        # Skip if duplicate debug net for same instrument/address (check BEFORE prompting)
        if net["type"] == "debug":
            if any(
                s.get("role") == "debug" and
                s.get("instrument") == net["instrument"] and
                s.get("address") == net["addr"]
                for s in saved_nets
            ):
                continue

        # Skip if exact duplicate of saved net exists
        # For UART nets, check against USB serial number (pin field)
        if net["type"] == "uart":
            if any(
                s.get("role") == "uart" and
                s.get("pin") == net["pin"]  # Match USB serial number
                for s in saved_nets
            ):
                continue
        else:
            if any(
                s.get("role") == net["type"] and
                s.get("instrument") == net["instrument"] and
                str(s.get("pin")) == str(net["chan"]) and
                s.get("address") == net["addr"]
                for s in saved_nets
            ):
                continue

        # Handle debug nets - prompt for device type if channel is DEVICE_TYPE
        # (only after we've confirmed this net will actually be created)
        if net["type"] == "debug" and net["chan"] == "DEVICE_TYPE":
            device_type = click.prompt(f"Enter device type for debug net on {net['instrument']} at {net['addr']}", type=str)
            net["chan"] = device_type

        filtered_nets.append(net)

    # Assign names to filtered nets (only now that we know which will be created)
    idx_re = re.compile(r"^([A-Za-z]+)(\d+)$")
    used_indices: dict[str, set[int]] = defaultdict(set)

    # Collect used indices from existing nets
    for saved_net in saved_nets:
        m = idx_re.match(saved_net.get("name", ""))
        if m and _first_word(saved_net.get("role", "")) == m.group(1):
            used_indices[saved_net.get("role", "")].add(int(m.group(2)))

    # Assign names to new nets
    for net in filtered_nets:
        role = net["type"]
        # Find lowest unused index for this role
        idx = 1
        while idx in used_indices[role]:
            idx += 1
        used_indices[role].add(idx)
        net["net"] = f"{_first_word(role)}{idx}"

    # Generate warnings
    for inst in sorted(duplicate_hubs):
        warnings.append(f"Multiple {inst} devices detected – unplug extras before adding nets.")
    for inst, addr in sorted(dup_single):
        warnings.append(f"{inst} at {addr} already has a net.")

    # Display warnings
    for warning in warnings:
        click.secho(f"Warning: {warning}", fg="yellow")

    if not filtered_nets:
        click.secho("No new nets can be created. All possible nets already exist or are blocked.", fg="yellow")
        return

    # Show what would be created
    click.secho(f"\nFound {len(filtered_nets)} nets that can be created:", fg="green")
    for net in filtered_nets:
        # For UART nets, show the device path instead of port number
        if net['type'] == 'uart':
            # Find the device path from inst_list
            device_path = None
            for dev in inst_list:
                uart_channels = dev.get("channels", {}).get("uart", [])
                if net.get('pin') in uart_channels:
                    device_path = dev.get("tty_path")
                    break
            path_display = f" ({device_path})" if device_path else ""
            click.echo(f"  - {net['net']} ({net['type']}) on {net['instrument']}{path_display}")
        else:
            click.echo(f"  - {net['net']} ({net['type']}) on {net['instrument']} channel {net['chan']}")

    # Confirm before proceeding
    if not yes:
        if not click.confirm(f"\nCreate all {len(filtered_nets)} nets on DUT {dut}?"):
            click.secho("Aborted.", fg="yellow")
            return

    # Prepare nets for batch save
    nets_to_save = []
    for net in filtered_nets:
        net_record = {
            "name": net["net"],
            "role": net["type"],
            "address": net["addr"],
            "instrument": net["instrument"],
            "pin": net.get("pin", net["chan"]),  # Use 'pin' if present (UART), else 'chan'
        }
        # For UART nets, also include the channel (port number)
        if net["type"] == "uart" and "chan" in net:
            net_record["channel"] = net["chan"]
        nets_to_save.append(net_record)

    # Use batch save for better performance
    _save_nets_batch(ctx, dut, nets_to_save)


@nets.command("create-batch", help="Create multiple nets from a JSON file for better performance.")
@click.argument("json_file", type=click.File("r"))
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP")
@click.pass_context
def create_batch_cmd(ctx: click.Context, json_file, box: str | None, dut: str | None) -> None:
    """
    Create multiple nets from a JSON file containing an array of net definitions.
    
    JSON format:
    [
        {
            "name": "net1",
            "role": "gpio", 
            "channel": "1",
            "address": "192.168.1.100"
        },
        {
            "name": "net2",
            "role": "adc",
            "channel": "2", 
            "address": "192.168.1.100"
        }
    ]
    """
    # Use box or dut (box takes precedence)

    resolved = box or dut

    dut = _resolve_dut(ctx, resolved)

    try:
        nets_data = json.load(json_file)
    except json.JSONDecodeError as e:
        click.secho(f"Invalid JSON in file: {e}", fg="red", err=True)
        ctx.exit(1)

    if not isinstance(nets_data, list):
        click.secho("JSON file must contain an array of net definitions", fg="red", err=True)
        ctx.exit(1)

    if not nets_data:
        click.secho("No nets found in JSON file", fg="yellow", err=True)
        return

    # Helper function to get instrument from address (reuse from create_cmd)
    def _get_instrument_from_address(address: str, fallback_instrument: str = "Unknown") -> str:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                run_python_internal(
                    ctx, get_impl_path("query_instruments.py"), dut,
                    image="", env={}, passenv=(), kill=False, download=(),
                    allow_overwrite=False, signum="SIGTERM", timeout=0,
                    detach=False, port=(), org=None,
                    args=("get_instrument", address),
                )
        except SystemExit:
            pass

        try:
            result = json.loads(buf.getvalue())
        except json.JSONDecodeError:
            return fallback_instrument

        if isinstance(result, list):
            for inst in result:
                if inst.get("address") == address:
                    return inst.get("name", "Unknown")
            return fallback_instrument
        elif isinstance(result, dict) and "name" in result:
            return result["name"]

        return fallback_instrument

    # Validate and normalize each net in the batch
    normalized_nets = []

    for i, net_data in enumerate(nets_data):
        if not isinstance(net_data, dict):
            click.secho(f"Net {i+1}: must be an object", fg="red", err=True)
            ctx.exit(1)

        required_fields = ["name", "role", "channel", "address"]
        for field in required_fields:
            if field not in net_data:
                click.secho(f"Net {i+1}: missing required field '{field}'", fg="red", err=True)
                ctx.exit(1)

        # Look up instrument if not provided
        instrument = net_data.get("instrument")
        if not instrument:
            instrument = _get_instrument_from_address(net_data["address"], "Unknown")

        normalized_net = {
            "name": net_data["name"],
            "role": net_data["role"],
            "address": net_data["address"],
            "pin": net_data["channel"],
            "instrument": instrument
        }
        normalized_nets.append(normalized_net)

    # Use batch save for better performance
    _save_nets_batch(ctx, dut, normalized_nets)
