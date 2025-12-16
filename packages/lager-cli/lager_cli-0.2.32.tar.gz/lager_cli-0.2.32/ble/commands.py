"""
    lager.ble.commands

    Commands for BLE - Updated for direct SSH execution
"""
import re
import click
import json
from texttable import Texttable
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from ..dut_storage import resolve_and_validate_dut

@click.group(name='ble')
def ble():
    """
        Scan and connect to Bluetooth Low Energy devices
    """
    pass

ADDRESS_NAME_RE = re.compile(r'\A([0-9A-F]{2}-){5}[0-9A-F]{2}\Z')

def check_name(device):
    return 0 if ADDRESS_NAME_RE.search(device['name']) else 1

def normalize_device(device):
    (address, data) = device
    item = {'address': address}
    manufacturer_data = data.get('manufacturer_data', {})
    for (k, v) in manufacturer_data.items():
        manufacturer_data[k] = bytes(v) if isinstance(v, list) else v
    item.update(data)
    return item

@ble.command('scan')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.option('--timeout', required=False, help='Total time gateway will spend scanning for devices', default=5.0, type=click.FLOAT, show_default=True)
@click.option('--name-contains', required=False, help='Filter devices to those whose name contains this string')
@click.option('--name-exact', required=False, help='Filter devices to those whose name matches this string')
@click.option('--verbose', required=False, is_flag=True, default=False, help='Verbose output (includes UUIDs)')
def scan(ctx, box,
 dut, timeout, name_contains, name_exact, verbose):
    """
        Scan for BLE devices
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    scan_args = {
        'action': 'scan',
        'timeout': timeout,
        'name_contains': name_contains,
        'name_exact': name_exact,
        'verbose': verbose
    }

    run_python_internal(
        ctx, get_impl_path('ble.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(scan_args),)
    )

@ble.command('info')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.argument('address', required=True)
def info(ctx, box, dut, address):
    """
        Get BLE device information
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    info_args = {
        'action': 'info',
        'address': address
    }

    run_python_internal(
        ctx, get_impl_path('ble.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(info_args),)
    )

@ble.command('connect')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.argument('address', required=True)
def connect(ctx, box,
 dut, address):
    """
        Connect to a BLE device
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    connect_args = {
        'action': 'connect',
        'address': address
    }

    run_python_internal(
        ctx, get_impl_path('ble.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(connect_args),)
    )

@ble.command('disconnect')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
@click.argument('address', required=True)
def disconnect(ctx, box, dut, address):
    """
        Disconnect from a BLE device
    """
    # Use box or dut (box takes precedence)
    box_name = box or dut

    # Resolve and validate the box/dut name
    dut = resolve_and_validate_dut(ctx, box_name)

    disconnect_args = {
        'action': 'disconnect',
        'address': address
    }

    run_python_internal(
        ctx, get_impl_path('ble.py'), dut,
        image='', env={}, passenv=(), kill=False, download=(),
        allow_overwrite=False, signum='SIGTERM', timeout=0,
        detach=False, port=(), org=None,
        args=(json.dumps(disconnect_args),)
    )