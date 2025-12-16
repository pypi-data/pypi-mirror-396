"""
lager.webcam.commands

Webcam streaming commands for viewing live camera feeds from gateway devices.
"""

import io
import click
import json
from contextlib import redirect_stdout
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path, get_default_net
from ..python.commands import run_python_internal
from ..dut_storage import get_dut_ip

WEBCAM_ROLE = "camera"


def _get_dut_ip_address(ctx: click.Context, dut: str = None) -> str:
    """
    Get the DUT IP address from various sources.

    Priority:
    1. Explicit --dut option (check local DUTs first)
    2. Default gateway from context

    Returns:
        IP address string
    """
    from ..dut_storage import resolve_and_validate_dut

    return resolve_and_validate_dut(ctx, dut)


def _resolve_gateway(ctx, box, dut):
    """Resolve DUT name to IP address if it's a local DUT."""
    from ..dut_storage import resolve_and_validate_dut
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


def _list_webcam_nets(ctx, box):
    """Get list of webcam nets from gateway."""
    recs = _run_net_py(ctx, box, "list")
    return [r for r in recs if r.get("role") == WEBCAM_ROLE]


def _display_webcam_nets(ctx, box):
    """Display webcam nets in a table."""
    nets = _list_webcam_nets(ctx, box)
    if not nets:
        click.echo("No webcam nets found on this gateway.")
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


def _run_webcam_command(ctx: click.Context, dut_ip: str, action: str, net_name: str = None) -> dict:
    """
    Execute webcam command on gateway.

    Args:
        ctx: Click context
        dut_ip: DUT IP address
        action: Action to perform (start, stop, url)
        net_name: Name of the webcam net

    Returns:
        dict: Response from gateway

    Raises:
        SystemExit: On command failure
    """
    import io
    from contextlib import redirect_stdout

    command_data = {
        "action": action,
        "net_name": net_name,
        "dut_ip": dut_ip
    }

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            run_python_internal(
                ctx,
                get_impl_path("webcam.py"),
                dut_ip,
                image="",
                env=(f"LAGER_COMMAND_DATA={json.dumps(command_data)}",),
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum="SIGTERM",
                timeout=30,
                detach=False,
                port=(),
                org=None,
                args=(),
            )
    except SystemExit:
        pass

    output = buf.getvalue().strip()

    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        click.secho(f"Failed to parse response from gateway", fg="red", err=True)
        click.secho(f"Raw output: {output}", fg="yellow", err=True)
        ctx.exit(1)

    if "error" in result:
        click.secho(f"Error: {result['error']}", fg="red", err=True)
        ctx.exit(1)

    return result


class WebcamGroup(click.Group):
    """Custom Group that handles optional NETNAME before subcommand"""

    def parse_args(self, ctx, args):
        """Override parse_args to handle NETNAME before subcommand"""
        # List of commands that don't require NETNAME
        command_names = ['url', 'start-all', 'stop-all']

        # Check if first argument is a command name (without NETNAME)
        if args and args[0] in command_names:
            # No NETNAME provided, just parse normally
            return super().parse_args(ctx, args)

        # Check if we have at least 2 args and second one is a command
        if len(args) >= 2 and args[1] in list(self.commands.keys()):
            # First arg is NETNAME, second is command
            netname = args[0]
            ctx.obj.netname = netname
            # Remove NETNAME from args and continue parsing
            return super().parse_args(ctx, args[1:])

        # Check if first argument is a command but no NETNAME provided
        if args and args[0] in list(self.commands.keys()):
            # Try to get default netname
            netname = get_default_net(ctx, 'webcam')
            if netname:
                ctx.obj.netname = netname
            # Continue parsing normally
            return super().parse_args(ctx, args)

        # Default parsing
        return super().parse_args(ctx, args)


@click.group(name="webcam", cls=WebcamGroup, invoke_without_command=True)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option("--dut", required=False, hidden=True, help="Lagerbox name or IP (deprecated, use --box)")
@click.pass_context
def webcam(ctx, box, dut):
    """
    Manage webcam streams

    Usage:
      lager webcam --box <BOX>                     # List webcam nets on gateway
      lager webcam <NETNAME> start --box <BOX>     # Start specific webcam
      lager webcam <NETNAME> stop --box <BOX>      # Stop specific webcam
      lager webcam start-all --box <BOX>           # Start all webcams
      lager webcam stop-all --box <BOX>            # Stop all webcams
      lager webcam url --box <BOX>                 # Show all webcam URLs
    """
    # If no subcommand was provided
    if ctx.invoked_subcommand is None:
        if box or dut:
            # List webcam nets for the specified gateway
            gateway = _resolve_gateway(ctx, box, dut)
            _display_webcam_nets(ctx, gateway)
        else:
            # Show help if no --box and no subcommand
            click.echo(ctx.get_help())


@click.command(name="start")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP (deprecated, use --box)")
@click.pass_context
def webcam_start(ctx, box, dut):
    """
    Start webcam stream
    """
    # Use box or dut (box takes precedence)
    box = box or dut

    # Get netname from parent context
    net_name = getattr(ctx.obj, "netname", None)
    if not net_name:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager webcam <NETNAME> start --box <BOX>\n"
            "Example: lager webcam webcam1 start --box JUL-3"
        )

    # Use parent context for get_default_gateway to access the correct params
    dut_ip = _get_dut_ip_address(ctx.parent, box)

    click.echo(f"Starting webcam stream for net '{net_name}' on {dut_ip}...")

    result = _run_webcam_command(ctx, dut_ip, "start", net_name)

    if result.get("already_running"):
        click.secho(f"Stream already running for '{net_name}'", fg="yellow")
    else:
        click.secho(f"Stream started successfully", fg="green")

    click.echo()
    click.secho(f"Webcam URL: {result['url']}", fg="cyan", bold=True)
    click.echo()
    click.echo("Open this URL in your browser to view the live feed.")
    click.echo(f"To stop the stream: lager webcam stop {net_name} --box {dut_ip}")


@click.command(name="url")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP (deprecated, use --box)")
@click.pass_context
def webcam_url(ctx, box, dut):
    """
    Print URLs of all active webcam streams
    """
    # Use box or dut (box takes precedence)
    box = box or dut

    # Use parent context for get_default_gateway to access the correct params
    dut_ip = _get_dut_ip_address(ctx.parent, box)

    result = _run_webcam_command(ctx, dut_ip, "url-all", None)

    if not result.get("results"):
        click.secho("No active webcam streams found", fg="yellow")
        return

    click.echo(f"Active webcam streams on {dut_ip}:")
    click.echo()

    for r in result["results"]:
        click.secho(f"{r['net']}:", fg="green", bold=True)
        click.secho(f"  URL: {r['url']}", fg="cyan")
        click.echo(f"  Port: {r['port']}")
        click.echo(f"  Device: {r['video_device']}")
        click.echo()


@click.command(name="stop")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP (deprecated, use --box)")
@click.pass_context
def webcam_stop(ctx, box, dut):
    """
    Stop webcam stream
    """
    # Use box or dut (box takes precedence)
    box = box or dut

    # Get netname from parent context
    net_name = getattr(ctx.obj, "netname", None)
    if not net_name:
        raise click.UsageError(
            "NETNAME required.\n\n"
            "Usage: lager webcam <NETNAME> stop --box <BOX>\n"
            "Example: lager webcam webcam1 stop --box JUL-3"
        )

    # Use parent context for get_default_gateway to access the correct params
    dut_ip = _get_dut_ip_address(ctx.parent, box)

    click.echo(f"Stopping webcam stream for net '{net_name}'...")

    result = _run_webcam_command(ctx, dut_ip, "stop", net_name)

    if result.get("ok"):
        click.secho("Stream stopped successfully", fg="green")
    else:
        click.secho(result.get("message", "Stream not running"), fg="yellow")


@click.command(name="start-all")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP (deprecated, use --box)")
@click.pass_context
def webcam_start_all(ctx, box, dut):
    """
    Start all webcam streams
    """
    # Use box or dut (box takes precedence)
    box = box or dut

    # Use parent context for get_default_gateway to access the correct params
    dut_ip = _get_dut_ip_address(ctx.parent, box)

    click.echo(f"Starting all webcam streams on {dut_ip}...")

    result = _run_webcam_command(ctx, dut_ip, "start-all", None)

    if not result.get("results"):
        click.secho(result.get("message", "No webcam nets found"), fg="yellow")
        return

    click.echo()
    success_count = len([r for r in result["results"] if r["success"]])
    click.secho(f"Started {success_count}/{len(result['results'])} webcam streams", fg="green")
    click.echo()

    # Print results for each webcam
    for r in result["results"]:
        net_name = r["net"]
        if r["success"]:
            status = "already running" if r.get("already_running") else "started"
            click.secho(f"✓ {net_name}: {status}", fg="green")
            click.secho(f"  URL: {r['url']}", fg="cyan")
        else:
            click.secho(f"✗ {net_name}: {r.get('error', 'failed')}", fg="red")

    click.echo()
    click.echo("Open the URLs in your browser to view the live feeds.")
    click.echo(f"To stop all streams: lager webcam stop-all --box {dut_ip}")


@click.command(name="stop-all")
@click.option("--box", help="Lagerbox name or IP")
@click.option("--dut", hidden=True, help="Lagerbox name or IP (deprecated, use --box)")
@click.pass_context
def webcam_stop_all(ctx, box, dut):
    """
    Stop all webcam streams
    """
    # Use box or dut (box takes precedence)
    box = box or dut

    # Use parent context for get_default_gateway to access the correct params
    dut_ip = _get_dut_ip_address(ctx.parent, box)

    click.echo(f"Stopping all webcam streams on {dut_ip}...")

    result = _run_webcam_command(ctx, dut_ip, "stop-all", None)

    if not result.get("results"):
        click.secho(result.get("message", "No webcam nets found"), fg="yellow")
        return

    click.echo()
    stopped_count = len([r for r in result["results"] if r.get("was_running")])
    click.secho(f"Stopped {stopped_count} webcam streams", fg="green")

    # Print results for each webcam
    for r in result["results"]:
        net_name = r["net"]
        if r.get("was_running"):
            click.secho(f"✓ {net_name}: stopped", fg="green")
        elif r["success"]:
            click.secho(f"  {net_name}: was not running", fg="yellow")
        else:
            click.secho(f"✗ {net_name}: {r.get('error', 'failed')}", fg="red")


# Add subcommands to the group
webcam.add_command(webcam_start)
webcam.add_command(webcam_url)
webcam.add_command(webcam_stop)
webcam.add_command(webcam_start_all)
webcam.add_command(webcam_stop_all)
