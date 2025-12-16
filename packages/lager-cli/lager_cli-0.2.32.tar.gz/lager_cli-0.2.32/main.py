"""
    lager.cli

    Command line interface entry point
"""
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import trio
    import lager_trio_websocket

import os
import urllib.parse
import sys

import traceback
import click

from . import __version__
from .config import read_config_file
from .context import LagerContext

from .adc.commands import adc
from .ble.commands import ble
from .debug.commands import _debug
from .defaults.commands import defaults
from .devenv.commands import devenv
from .exec.commands import exec_
from .uart.commands import uart
from .python.commands import python
from .wifi.commands import _wifi
from .webcam.commands import webcam
from .pip.commands import pip
# Net-related commands (restructured)
from .scope.commands import scope
from .logic.commands import logic
from .supply.commands import supply
from .solar.commands import solar
from .battery.commands import battery
from .eload.commands import eload
from .net.commands import nets
from .usb.commands import usb
from .hello.commands import hello
from .arm.commands import arm
from .thermocouple.commands import thermocouple
from .watt.commands import watt
from .dac.commands import dac
from .gpi.commands import gpi
from .gpo.commands import gpo
from .status.commands import status
from .boxes.commands import boxes
from .instruments.commands import instruments
from .ssh.commands import ssh
from .update.commands import update
from .logs.commands import logs
from .binaries.commands import binaries

def _decode_environment():
    for key in os.environ:
        if key.startswith('LAGER_'):
            os.environ[key] = urllib.parse.unquote(os.environ[key])

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', 'see_version', is_flag=True, help='See package version')
@click.option('--debug', 'debug', is_flag=True, help='Show debug output', default=False)
@click.option('--colorize', 'colorize', is_flag=True, help='Enable colored terminal output', default=False)
@click.option('--interpreter', '-i', required=False, default=None, help='Select a specific interpreter / user interface', hidden=True)
def cli(ctx=None, see_version=None, debug=False, colorize=False, interpreter=None):
    """
        Lager CLI
    """
    if os.getenv('LAGER_DECODE_ENV'):
        _decode_environment()

    if see_version:
        click.echo(__version__)
        click.get_current_context().exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    else:
        setup_context(ctx, debug, colorize, interpreter)

cli.add_command(adc)
cli.add_command(ble)
cli.add_command(_debug)
cli.add_command(defaults)
cli.add_command(devenv)
cli.add_command(exec_)
cli.add_command(uart)
cli.add_command(python)
cli.add_command(_wifi)
cli.add_command(webcam)
cli.add_command(pip)
cli.add_command(scope)
cli.add_command(logic)
cli.add_command(supply)
cli.add_command(battery)
cli.add_command(eload)
cli.add_command(nets)
cli.add_command(solar)
cli.add_command(usb)
cli.add_command(hello)
cli.add_command(arm)
cli.add_command(thermocouple)
cli.add_command(watt)
cli.add_command(dac)
cli.add_command(gpi)
cli.add_command(gpo)
cli.add_command(status)
cli.add_command(boxes)
cli.add_command(instruments)
cli.add_command(ssh)
cli.add_command(update)
cli.add_command(logs)
cli.add_command(binaries)

def setup_context(ctx, debug, colorize, interpreter):
    """
        Setup the CLI context
    """
    config = read_config_file()
    ctx.obj = LagerContext(
        ctx=ctx,
        defaults=config['LAGER'],
        debug=debug,
        style=click.style if colorize else lambda string, **kwargs: string,
        interpreter=interpreter,
    )
