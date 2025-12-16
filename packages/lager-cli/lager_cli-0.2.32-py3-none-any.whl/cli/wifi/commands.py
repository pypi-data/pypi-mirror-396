"""
    lager.wifi.commands

    Commands for controlling WiFi - Updated for direct SSH execution
"""

import click
import json
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from ..dut_storage import resolve_and_validate_dut

@click.group(name='wifi', hidden=True)
def _wifi():
    """
        Lager wifi commands
    """
    pass

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
def status(ctx, box, dut):
    """
        Get the current WiFi Status of the gateway
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    status_args = {
        'action': 'status'
    }

    run_python_internal(
        ctx, get_impl_path('wifi.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(status_args),)
    )

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--interface', required=False, help='Wireless interface to use', default='wlan0')
def access_points(ctx, box,
 dut, interface='wlan0'):
    """
        Get WiFi access points visible to the gateway
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    scan_args = {
        'action': 'scan',
        'interface': interface
    }

    run_python_internal(
        ctx, get_impl_path('wifi.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(scan_args),)
    )

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--ssid', required=True, help='SSID of the network to connect to')
@click.option('--interface', help='Wireless interface to use', default='wlan0', show_default=True)
@click.option('--password', required=False, help='Password of the network to connect to', default='')
def connect(ctx, box, dut, ssid, interface, password=''):
    """
        Connect the gateway to a new network
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    connect_args = {
        'action': 'connect',
        'ssid': ssid,
        'password': password,
        'interface': interface
    }

    run_python_internal(
        ctx, get_impl_path('wifi.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(connect_args),)
    )

@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help='ID of DUT')
@click.option('--yes', is_flag=True, help='Confirm the action without prompting')
@click.argument('SSID', required=True)
def delete_connection(ctx, box, dut, yes, ssid):
    """
        Delete the specified network from the gateway
    """
    if not yes and not click.confirm('An ethernet connection will be required to bring the gateway back online. Proceed?', default=False):
        click.echo("Aborting")
        return

    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    delete_args = {
        'action': 'delete',
        'ssid': ssid,
        'connection_name': ssid
    }

    run_python_internal(
        ctx, get_impl_path('wifi.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(delete_args),)
    )