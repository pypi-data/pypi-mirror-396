"""
    DUT storage utilities for managing local DUT configurations
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional


def get_lager_file_path() -> Path:
    """Get the path to the .lager file in home directory."""
    # Check for environment variable override
    if lager_config := os.getenv('LAGER_CONFIG_FILE_DIR'):
        return Path(lager_config) / '.lager'

    # Always use global config in home directory
    return Path.home() / '.lager'


def load_duts() -> Dict[str, any]:
    """Load DUTs from the .lager file.

    Returns a dict where values can be either:
    - str: IP address (legacy format)
    - dict: {"ip": str, "user": str} (new format)
    """
    lager_file = get_lager_file_path()
    if not lager_file.exists():
        return {}

    try:
        with open(lager_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Check for new DUTS key, fallback to legacy 'duts'
            return data.get('DUTS') or data.get('duts', {})
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_duts(duts: Dict[str, str]) -> None:
    """Save DUTs to the .lager file, preserving all existing data."""
    lager_file = get_lager_file_path()

    # Load existing data or create new structure
    data = {}
    if lager_file.exists():
        try:
            with open(lager_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    data = {}
                elif content[0] in ('{', '['):
                    # JSON format - migrate legacy keys to new format
                    data = json.loads(content)
                    # Migrate legacy lowercase keys to uppercase
                    if 'auth' in data:
                        data['AUTH'] = data.pop('auth')
                    if 'duts' in data:
                        data['DUTS'] = data.pop('duts')
                    if 'nets' in data:
                        data['NETS'] = data.pop('nets')
                    if 'devenv' in data:
                        data['DEVENV'] = data.pop('devenv')
                    if 'LAGER' in data:
                        data['DEFAULTS'] = data.pop('LAGER')
                else:
                    # INI format - convert to JSON preserving all sections
                    from .config import read_config_file, _configparser_to_json
                    config = read_config_file(str(lager_file))
                    data = _configparser_to_json(config)
        except (json.JSONDecodeError, Exception):
            # If we can't parse it, start fresh
            data = {}

    # Use new DUTS key
    data['DUTS'] = duts

    with open(lager_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def add_dut(name: str, ip: str, user: Optional[str] = None, version: Optional[str] = None) -> None:
    """Add a DUT to the local storage.

    Args:
        name: DUT name
        ip: IP address
        user: Optional username (if None and version is None, stores in legacy format)
        version: Optional version/branch name (e.g., "staging", "main")
    """
    duts = load_duts()
    if user or version:
        # New format with user and/or version
        dut_dict = {"ip": ip}
        if user:
            dut_dict["user"] = user
        if version:
            dut_dict["version"] = version
        duts[name] = dut_dict
    else:
        # Legacy format (just IP string)
        duts[name] = ip
    save_duts(duts)


def get_dut_ip(name: str) -> Optional[str]:
    """Get the IP address for a named DUT."""
    duts = load_duts()
    dut_info = duts.get(name)
    if isinstance(dut_info, dict):
        # Dict format: extract IP
        return dut_info.get("ip")
    elif isinstance(dut_info, str):
        # Legacy format: just the IP
        return dut_info
    return None


def get_dut_user(name: str) -> Optional[str]:
    """Get the username for a named DUT.

    Args:
        name: DUT name

    Returns:
        Username if stored, None otherwise (will use default)
    """
    duts = load_duts()
    dut_info = duts.get(name)
    if isinstance(dut_info, dict):
        return dut_info.get("user")
    # Legacy format (string IP) has no username
    return None


def get_dut_version(name: str) -> Optional[str]:
    """Get the version for a named DUT.

    Args:
        name: DUT name

    Returns:
        Version if stored, None otherwise
    """
    duts = load_duts()
    dut_info = duts.get(name)
    if isinstance(dut_info, dict):
        return dut_info.get("version")
    # Legacy format (string IP) has no version
    return None


def update_dut_version(name: str, version: str) -> bool:
    """Update the version for a named DUT.

    Args:
        name: DUT name
        version: Version/branch name (e.g., "staging", "main")

    Returns:
        True if updated, False if DUT not found
    """
    duts = load_duts()
    if name not in duts:
        return False

    dut_info = duts[name]
    if isinstance(dut_info, dict):
        # Update version in existing dict
        dut_info["version"] = version
    else:
        # Upgrade from legacy format to dict format
        duts[name] = {"ip": dut_info, "version": version}

    save_duts(duts)
    return True


def get_dut_name_by_ip(ip: str) -> Optional[str]:
    """Reverse lookup: find DUT name by IP address.

    Args:
        ip: IP address to lookup

    Returns:
        DUT name if found, None otherwise
    """
    duts = load_duts()
    for name, dut_info in duts.items():
        dut_ip = None
        if isinstance(dut_info, dict):
            dut_ip = dut_info.get("ip")
        elif isinstance(dut_info, str):
            dut_ip = dut_info

        if dut_ip == ip:
            return name
    return None


def delete_dut(name: str) -> bool:
    """Delete a DUT from the local storage. Returns True if deleted, False if not found."""
    duts = load_duts()
    if name in duts:
        del duts[name]
        save_duts(duts)
        return True
    return False


def list_duts() -> Dict[str, str]:
    """List all stored DUTs."""
    return load_duts()


def delete_all_duts() -> int:
    """Delete all DUTs from the local storage. Returns the number of DUTs deleted."""
    duts = load_duts()
    count = len(duts)
    save_duts({})
    return count


def resolve_and_validate_dut_with_name(ctx, dut_name: Optional[str] = None) -> tuple:
    """
    Resolve and validate a DUT name, returning both IP and name.

    Args:
        ctx: Click context
        dut_name: DUT name to resolve (if None, uses default gateway)

    Returns:
        Tuple of (resolved_ip_or_gateway_id, original_dut_name_or_None)

    Exits with error if DUT is invalid or not found.
    """
    import click
    import ipaddress
    from .context import get_default_gateway

    # If no DUT name provided, use default gateway
    if not dut_name:
        return (get_default_gateway(ctx), None)

    # Check if it's a saved DUT name
    saved_ip = get_dut_ip(dut_name)
    if saved_ip:
        return (saved_ip, dut_name)

    # Check if it's a valid IP address
    try:
        ipaddress.ip_address(dut_name)
        return (dut_name, None)  # Direct IP, no DUT name
    except ValueError:
        # Not a valid IP and not in local DUTs - Show helpful error
        click.secho(f"Error: DUT '{dut_name}' not found.", fg='red', err=True)
        click.echo("", err=True)

        saved_duts = list_duts()
        if saved_duts:
            click.echo("Available DUTs:", err=True)
            for name, dut_info in saved_duts.items():
                if isinstance(dut_info, dict):
                    dut_ip = dut_info.get('ip', 'unknown')
                else:
                    dut_ip = dut_info
                click.echo(f"  - {name} ({dut_ip})", err=True)
        else:
            click.echo("No DUTs are currently saved.", err=True)

        click.echo("", err=True)
        click.echo("To add a new box, use:", err=True)
        click.echo(f"  lager boxes add --name {dut_name} --ip <IP_ADDRESS>", err=True)
        ctx.exit(1)


def resolve_and_validate_dut(ctx, dut_name: Optional[str] = None) -> str:
    """
    Resolve and validate a DUT name.

    Args:
        ctx: Click context
        dut_name: DUT name to resolve (if None, uses default gateway)

    Returns:
        Resolved DUT IP address or gateway ID

    Exits with error if DUT is invalid or not found.
    """
    import click
    import ipaddress
    from .context import get_default_gateway

    # If no DUT name provided, use default gateway
    if not dut_name:
        return get_default_gateway(ctx)

    # Check if it's a saved DUT name
    saved_ip = get_dut_ip(dut_name)
    if saved_ip:
        return saved_ip

    # Check if it's a valid IP address
    try:
        ipaddress.ip_address(dut_name)
        return dut_name
    except ValueError:
        # Not a valid IP and not in local DUTs - Show helpful error
        click.secho(f"Error: DUT '{dut_name}' not found.", fg='red', err=True)
        click.echo("", err=True)

        saved_duts = list_duts()
        if saved_duts:
            click.echo("Available DUTs:", err=True)
            for name, dut_info in saved_duts.items():
                if isinstance(dut_info, dict):
                    dut_ip = dut_info.get('ip', 'unknown')
                else:
                    dut_ip = dut_info
                click.echo(f"  - {name} ({dut_ip})", err=True)
        else:
            click.echo("No DUTs are currently saved.", err=True)

        click.echo("", err=True)
        click.echo("To add a new box, use:", err=True)
        click.echo(f"  lager boxes add --name {dut_name} --ip <IP_ADDRESS>", err=True)
        ctx.exit(1)