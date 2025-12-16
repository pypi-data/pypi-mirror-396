"""
lager.uart.commands

Commands for DUT UART interaction
"""
from __future__ import annotations

import sys
import io
import json
from contextlib import redirect_stdout

import click
import requests
from texttable import Texttable

from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal

UART_ROLE = "uart"


# ---------- helpers ----------

def _resolve_gateway(ctx, box, dut):
    """
    Resolve gateway/dut parameter to IP address.
    Returns tuple of (ip_address, dut_name) where dut_name is used for username lookup.
    """
    from ..dut_storage import resolve_and_validate_dut, get_dut_name_by_ip

    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    resolved_ip = resolve_and_validate_dut(ctx, box_name)

    # Try to find DUT name for username lookup
    # If box_name was provided and is not an IP, it's the DUT name
    if box_name and not box_name.replace('.', '').isdigit():
        dut_name = box_name
    else:
        # It was an IP, try reverse lookup
        dut_name = get_dut_name_by_ip(resolved_ip)

    return (resolved_ip, dut_name)


def _run_net_py(ctx: click.Context, dut: str, *args: str) -> list[dict]:
    """
    Fetch nets list from the gateway.
    Uses the HTTP endpoint on port 9000 (Python container).
    """
    try:
        gateway_url = f'http://{dut}:9000/uart/nets/list'
        response = requests.get(gateway_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('nets', [])
        else:
            click.echo(f"Error: Gateway returned status {response.status_code}", err=True)
            return []
    except (requests.RequestException, json.JSONDecodeError) as e:
        click.echo(f"Error: Could not fetch nets from gateway at {dut}:9000: {e}", err=True)
        return []


def _list_uart_nets(ctx, box):
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == UART_ROLE]


def _get_uart_net(ctx, box, netname):
    """Get a specific UART net by name"""
    nets = _list_uart_nets(ctx, box)
    for net in nets:
        if net.get("name") == netname:
            return net
    return None


def _run_query_instruments(ctx: click.Context, dut: str) -> list[dict]:
    """Query instruments on the gateway to get device information."""
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
    raw = buf.getvalue() or "[]"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def _find_device_path(usb_serial: str, inst_list: list[dict]) -> str | None:
    """Find the /dev/tty* path for a given USB serial number."""
    if usb_serial and isinstance(usb_serial, str) and usb_serial.startswith("/dev/"):
        # Net was created using a direct device path instead of a USB serial number.
        return usb_serial

    for inst in inst_list:
        # Check if this is a UART device
        channels = inst.get("channels", {})
        uart_channels = channels.get("uart", [])

        # If this device's UART channels include our serial number
        if usb_serial in uart_channels:
            # Return the tty_path if available
            return inst.get("tty_path")

    return None


def display_nets(ctx, box, netname: str | None):
    """Display UART nets with their configuration parameters."""
    uart_nets = _list_uart_nets(ctx, box)

    # Check if there are any UART nets to display
    if not uart_nets:
        click.echo("No UART nets found on this gateway.")
        return

    # Query instruments to get current device paths
    inst_list = _run_query_instruments(ctx, box)

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(["t", "t", "t", "t", "t", "t", "t"])
    table.set_cols_align(["l", "l", "l", "l", "l", "l", "l"])
    table.header(["Name", "Bridge Type", "Device Path", "Port", "Baudrate", "Format", "Flow Control"])

    for rec in uart_nets:
        if netname is None or netname == rec.get("name"):
            name = rec.get("name", "")
            bridge_type = rec.get("instrument", "Unknown")
            usb_serial = rec.get("pin", "")
            port = rec.get("channel", "0")
            params = rec.get("params", {})

            # Look up current device path from instruments
            device_path = _find_device_path(usb_serial, inst_list)
            display_path = device_path if device_path else f"{usb_serial} (disconnected)"

            # Extract parameters with defaults
            baudrate = params.get("baudrate", "115200")
            bytesize = params.get("bytesize", "8")
            parity = params.get("parity", "none")
            stopbits = params.get("stopbits", "1")

            # Build format string (e.g., "8N1")
            parity_char = {"none": "N", "even": "E", "odd": "O", "mark": "M", "space": "S"}.get(parity, "N")
            format_str = f"{bytesize}{parity_char}{stopbits}"

            # Build flow control string
            flow_parts = []
            if params.get("xonxoff"):
                flow_parts.append("XON/XOFF")
            if params.get("rtscts"):
                flow_parts.append("RTS/CTS")
            if params.get("dsrdtr"):
                flow_parts.append("DSR/DTR")
            flow_control = ", ".join(flow_parts) if flow_parts else "None"

            table.add_row([name, bridge_type, display_path, port, str(baudrate), format_str, flow_control])

    result = table.draw()
    click.echo(result)


def _run_backend(ctx, dut, action: str, **params):
    """Run backend command and handle errors gracefully"""
    data = {
        "action": action,
        "params": params,
    }
    try:
        run_python_internal(
            ctx,
            get_impl_path("uart.py"),
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
        # Backend errors are already printed by the backend
        # Just re-raise to preserve exit code
        if e.code != 0:
            raise


def _connect_uart_http(ctx, gateway, netname, overrides, interactive):
    """
    Connect to UART via WebSocket (both read-only and interactive modes).

    Both modes now use WebSocket for reliability - no more HTTP streaming crashes!

    Args:
        ctx: Click context
        gateway: Gateway IP address
        netname: Name of the UART net to connect to
        overrides: Dictionary of serial port parameter overrides
        interactive: Whether to use interactive mode (bidirectional with keyboard input)
    """
    import time

    # Both interactive and read-only modes now use WebSocket
    if interactive:
        from .websocket_client import connect_uart_interactive
        gateway_url = f'http://{gateway}:9000'
        connect_func = connect_uart_interactive
    else:
        from .websocket_client import connect_uart_readonly
        gateway_url = f'http://{gateway}:9000'
        connect_func = connect_uart_readonly

    # Retry logic for WebSocket connection
    max_retries = 2
    for attempt in range(max_retries):
        try:
            exit_code = connect_func(gateway_url, netname, overrides)
            ctx.exit(exit_code)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                if "Connection refused" in str(e) or "Failed to establish" in str(e):
                    click.echo(f"Connection failed, retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})", err=True)
                    time.sleep(2)
                    continue
            raise


# ---------- CLI ----------

@click.command()
@click.argument("NETNAME", required=False)
@click.argument("ACTION", required=False)
@click.pass_context
# Target options
@click.option('--dut', required=False, help="Lagerbox name or IP")
# Serial parameter overrides
@click.option('--baudrate', type=int, help='Baudrate in baud (e.g., 9600, 115200)')
@click.option('--bytesize', type=click.Choice(['5', '6', '7', '8']), help='Number of data bits')
@click.option('--parity', type=click.Choice(['none', 'even', 'odd', 'mark', 'space']), help='Parity checking mode')
@click.option('--stopbits', type=click.Choice(['1', '1.5', '2']), help='Number of stop bits')
# Flow control options
@click.option('--xonxoff/--no-xonxoff', default=None, help='Software flow control (XON/XOFF)')
@click.option('--rtscts/--no-rtscts', default=None, help='Hardware flow control (RTS/CTS)')
@click.option('--dsrdtr/--no-dsrdtr', default=None, help='Hardware flow control (DSR/DTR)')
# Session options
@click.option('-i', '--interactive', is_flag=True, help='Enable input mode for typing to serial port', show_default=True)
@click.option('--opost/--no-opost', default=False, help=r'Convert \n to \r\n on output', show_default=True)
@click.option('--line-ending', type=click.Choice(['lf', 'crlf', 'cr']), default='lf', help='Line ending format (lf=\\n, crlf=\\r\\n, cr=\\r)', show_default=True)
@click.option("--box", required=False, help="Lagerbox name or IP")
def uart(ctx, netname, action, dut, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr,
         interactive, opost, line_ending, box):
    """
    Connect to UART serial port.

    \b
    Usage examples:
      lager uart                       # list UART nets
      lager uart NET                   # connect read-only
      lager uart NET -i                # connect interactively
      lager uart NET serial-port       # show the tty path for NET

    \b
    Creating UART nets:
      Standard (using Device Serial NUMBER):
        lager nets create NET uart <device-serial> <address> --box <gateway>
      Direct /dev path (using Device Serial PORT):
        lager nets create NET uart /dev/ttyUSB0 <label> --box <gateway>
        (warning: tty names can change across reboots; prefer serial-number mode when possible)
    """
    # Resolve box/dut to gateway IP
    target_gateway, dut_name = _resolve_gateway(ctx, box, dut)

    # If no netname provided, try to use default
    if not netname:
        netname = get_default_net(ctx, 'uart')

    # Handle sub-action to report the current serial port in use
    if action:
        if action != "serial-port":
            raise click.UsageError(f"Unknown UART action '{action}'. Supported: serial-port")

        if not netname:
            click.secho("No UART net specified and no default configured.", fg="yellow", err=True)
            click.echo("Provide a net name or set a default with 'lager defaults set --uart-net <name>'.", err=True)
            ctx.exit(1)

        net_config = _get_uart_net(ctx, target_gateway, netname)
        if not net_config:
            click.secho(f"Error: UART net '{netname}' not found", fg='red', err=True)
            ctx.exit(1)

        inst_list = _run_query_instruments(ctx, target_gateway)
        usb_serial = net_config.get("pin", "")
        device_path = _find_device_path(usb_serial, inst_list)

        if device_path:
            click.echo(device_path)
        else:
            click.secho(f"Serial port for net '{netname}' ({usb_serial}) is not connected.", fg="yellow", err=True)
            ctx.exit(1)
        return

    # If still no netname, list all UART nets
    if not netname:
        display_nets(ctx, target_gateway, None)
        return

    # Validate flow control options
    if xonxoff and rtscts:
        raise click.UsageError('Cannot use --xonxoff and --rtscts simultaneously')

    # Load net configuration
    net_config = _get_uart_net(ctx, target_gateway, netname)
    if not net_config:
        click.secho(f"Error: UART net '{netname}' not found", fg='red', err=True)
        click.echo(f"\nRun 'lager uart' to see available UART nets on {target_gateway}", err=True)
        click.echo(f"\nTo create a new UART net:", err=True)
        click.echo(f"  1. Find available UART devices: lager instruments --box {target_gateway}", err=True)
        click.echo(f"  2a. Standard: lager nets create {netname} uart <device-serial> <address>", err=True)
        click.echo(f"  2b. No serial on adapter: lager nets create {netname} uart /dev/ttyUSB0 <label>", err=True)
        ctx.exit(1)

    # Validate TTY for interactive mode
    if interactive:
        if not sys.stdin.isatty():
            click.secho('Error: stdin is not a TTY (cannot use --interactive)', fg='red', err=True)
            ctx.exit(1)
        if not sys.stdout.isatty():
            click.secho('Error: stdout is not a TTY (cannot use --interactive)', fg='red', err=True)
            ctx.exit(1)

    # Build parameter overrides
    overrides = {}
    if baudrate is not None:
        overrides['baudrate'] = baudrate
    if bytesize is not None:
        overrides['bytesize'] = int(bytesize)
    if parity is not None:
        overrides['parity'] = parity
    if stopbits is not None:
        overrides['stopbits'] = stopbits
    if xonxoff is not None:
        overrides['xonxoff'] = xonxoff
    if rtscts is not None:
        overrides['rtscts'] = rtscts
    if dsrdtr is not None:
        overrides['dsrdtr'] = dsrdtr

    # Always include opost setting
    overrides['opost'] = opost

    # Always include line_ending setting
    overrides['line_ending'] = line_ending

    # Show connection info
    net_params = net_config.get("params", {})
    final_baudrate = overrides.get('baudrate', net_params.get("baudrate", 115200))
    bridge_type = net_config.get("instrument", "unknown")
    usb_serial = net_config.get("pin", "unknown")
    usb_serial_short = usb_serial[:10] if len(usb_serial) > 10 else usb_serial
    port = net_config.get("channel", "0")
    mode_str = "interactive" if interactive else "read-only"

    click.echo(
        f"Connecting to {netname}: {bridge_type} (serial {usb_serial_short})",
        err=True,
    )

    # Connect to UART via HTTP using run_python_internal()
    # This uses the same streaming pattern as all other lager commands
    _connect_uart_http(
        ctx, target_gateway, netname, overrides, interactive
    )
