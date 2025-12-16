"""
    Net storage utilities for managing local net configurations
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


def get_lager_file_path() -> Path:
    """Get the path to the .lager file in home directory."""
    import os

    # Check for environment variable override
    if lager_config := os.getenv('LAGER_CONFIG_FILE_DIR'):
        return Path(lager_config) / '.lager'

    # Always use global config in home directory
    return Path.home() / '.lager'


def load_nets(dut_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load nets from the .lager file.

    Args:
        dut_name: If provided, return only nets for this DUT. Otherwise return all nets.

    Returns:
        List of net dictionaries
    """
    lager_file = get_lager_file_path()
    if not lager_file.exists():
        return []

    try:
        with open(lager_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Check for new NETS key, fallback to legacy 'nets'
            nets = data.get('NETS') or data.get('nets', {})

            if dut_name:
                # Return nets for specific DUT
                return nets.get(dut_name, [])
            else:
                # Return all nets (flattened from all DUTs)
                all_nets = []
                for dut_nets in nets.values():
                    all_nets.extend(dut_nets)
                return all_nets
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_nets(nets: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Save nets to the .lager file, preserving all existing data.

    Args:
        nets: Dictionary mapping DUT names to lists of net dictionaries
    """
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
                    import sys
                    sys.path.insert(0, str(lager_file.parent))
                    from config import read_config_file, _configparser_to_json
                    config = read_config_file(str(lager_file))
                    data = _configparser_to_json(config)
        except (json.JSONDecodeError, Exception):
            # If we can't parse it, start fresh
            data = {}

    # Use new NETS key
    data['NETS'] = nets

    with open(lager_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def add_net(dut_name: str, net_data: Dict[str, Any]) -> None:
    """
    Add a net to the local storage for a specific DUT.

    Args:
        dut_name: The DUT this net belongs to
        net_data: Net configuration dictionary
    """
    lager_file = get_lager_file_path()

    # Load existing data
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
                    import sys
                    sys.path.insert(0, str(lager_file.parent))
                    from config import read_config_file, _configparser_to_json
                    config = read_config_file(str(lager_file))
                    data = _configparser_to_json(config)
        except (json.JSONDecodeError, Exception):
            data = {}

    # Get or create nets structure
    if 'NETS' not in data:
        data['NETS'] = {}

    if dut_name not in data['NETS']:
        data['NETS'][dut_name] = []

    # Add net (avoid duplicates by name)
    existing_names = {n.get('name') for n in data['NETS'][dut_name]}
    if net_data.get('name') not in existing_names:
        data['NETS'][dut_name].append(net_data)
    else:
        # Update existing net
        for i, net in enumerate(data['NETS'][dut_name]):
            if net.get('name') == net_data.get('name'):
                data['NETS'][dut_name][i] = net_data
                break

    with open(lager_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def delete_net(dut_name: str, net_name: str) -> bool:
    """
    Delete a net from local storage.

    Args:
        dut_name: The DUT this net belongs to
        net_name: Name of the net to delete

    Returns:
        True if deleted, False if not found
    """
    lager_file = get_lager_file_path()

    if not lager_file.exists():
        return False

    try:
        with open(lager_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False

    # Check both NETS and legacy 'nets'
    nets = data.get('NETS') or data.get('nets', {})
    if not nets or dut_name not in nets:
        return False

    # Find and remove net
    original_len = len(nets[dut_name])
    nets[dut_name] = [n for n in nets[dut_name] if n.get('name') != net_name]

    if len(nets[dut_name]) < original_len:
        # Update using new NETS key and remove legacy
        data['NETS'] = nets
        data.pop('nets', None)
        with open(lager_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True

    return False


def list_nets(dut_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    List all nets, optionally filtered by DUT.

    Args:
        dut_name: If provided, return only nets for this DUT

    Returns:
        Dictionary mapping DUT names to lists of nets
    """
    lager_file = get_lager_file_path()

    if not lager_file.exists():
        return {}

    try:
        with open(lager_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Check for new NETS key, fallback to legacy 'nets'
            nets = data.get('NETS') or data.get('nets', {})

            if dut_name:
                if dut_name in nets:
                    return {dut_name: nets[dut_name]}
                else:
                    return {}
            else:
                return nets
    except (json.JSONDecodeError, FileNotFoundError):
        return {}
