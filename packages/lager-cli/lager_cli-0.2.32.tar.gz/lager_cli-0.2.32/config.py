"""
    lager.config

    Config file management routines
"""
import os
import json
import configparser
import click

DEFAULT_CONFIG_FILE_NAME = '.lager'
LAGER_CONFIG_FILE_NAME = os.getenv('LAGER_CONFIG_FILE_NAME', DEFAULT_CONFIG_FILE_NAME)

DEVENV_SECTION_NAME = 'DEVENV'


def _is_json_format(path):
    """Check if a file is in JSON format."""
    try:
        with open(path, 'r') as f:
            content = f.read().strip()
            if not content:
                return False
            # Check if it starts with { or [ which indicates JSON
            return content[0] in ('{', '[')
    except (FileNotFoundError, IOError):
        return False


def _json_to_configparser(json_data):
    """Convert JSON data to ConfigParser object."""
    config = configparser.ConfigParser()

    # Add LAGER section
    if 'LAGER' not in config:
        config.add_section('LAGER')

    # Convert DEFAULTS section if it exists in JSON (or legacy LAGER)
    defaults_data = json_data.get('DEFAULTS') or json_data.get('LAGER')
    if defaults_data and isinstance(defaults_data, dict):
        for key, value in defaults_data.items():
            config.set('LAGER', key, str(value))

    # Convert AUTH section if it exists (check both AUTH and legacy 'auth')
    auth_data = json_data.get('AUTH') or json_data.get('auth')
    if auth_data:
        if 'AUTH' not in config:
            config.add_section('AUTH')
        if isinstance(auth_data, dict):
            for key, value in auth_data.items():
                config.set('AUTH', key, str(value))

    # Convert DEVENV section if it exists (check both DEVENV and legacy 'devenv')
    devenv_data = json_data.get('DEVENV') or json_data.get('devenv')
    if devenv_data:
        if DEVENV_SECTION_NAME not in config:
            config.add_section(DEVENV_SECTION_NAME)
        for key, value in devenv_data.items():
            config.set(DEVENV_SECTION_NAME, key, str(value))

    return config


def _configparser_to_json(config, existing_json=None):
    """Convert ConfigParser object to JSON data, preserving existing JSON fields."""
    if existing_json is None:
        json_data = {}
    else:
        json_data = existing_json.copy()

    # Convert LAGER section to DEFAULTS in JSON
    if config.has_section('LAGER'):
        defaults_data = {}
        for key, value in config.items('LAGER'):
            defaults_data[key] = value
        if defaults_data:  # Only add if non-empty
            json_data['DEFAULTS'] = defaults_data
        else:
            # Remove DEFAULTS if LAGER section is empty
            json_data.pop('DEFAULTS', None)
        # Remove legacy LAGER key if it exists
        json_data.pop('LAGER', None)

    # Convert AUTH section to AUTH JSON object
    if config.has_section('AUTH'):
        auth_data = {}
        for key, value in config.items('AUTH'):
            auth_data[key] = value
        if auth_data:  # Only add if non-empty
            json_data['AUTH'] = auth_data
            # Remove legacy 'auth' key if it exists
            json_data.pop('auth', None)

    # Convert DEVENV section to DEVENV JSON object
    if config.has_section(DEVENV_SECTION_NAME):
        devenv_data = {}
        for key, value in config.items(DEVENV_SECTION_NAME):
            devenv_data[key] = value
        if devenv_data:
            json_data['DEVENV'] = devenv_data
            # Remove legacy 'devenv' key if it exists
            json_data.pop('devenv', None)

    return json_data


def get_global_config_file_path():
    if 'LAGER_CONFIG_FILE_DIR' in os.environ:
        return make_config_path(os.getenv('LAGER_CONFIG_FILE_DIR'))
    return make_config_path(os.path.expanduser('~'))

def make_config_path(directory, config_file_name=None):
    """
        Make a full path to a lager config file
    """
    if config_file_name is None:
        config_file_name = LAGER_CONFIG_FILE_NAME

    return os.path.join(directory, config_file_name)

def find_devenv_config_path():
    """
        Find a local .lager config, if it exists
    """
    configs = _find_config_files()
    if not configs:
        return None
    return configs[0]

def _find_config_files():
    """
        Search up from current directory for all .lager files
    """
    cwd = os.getcwd()
    cfgs = []
    global_config_file_path = get_global_config_file_path()
    while True:
        config_path = make_config_path(cwd)
        if os.path.exists(config_path) and config_path != global_config_file_path:
            cfgs.append(config_path)
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent

    return cfgs


def read_config_file(path=None):
    """
        Read our config file into `config` object.
        Supports both JSON and INI formats.
    """
    if path is None:
        path = get_global_config_file_path()

    config = configparser.ConfigParser()

    try:
        # Check if file is in JSON format
        if _is_json_format(path):
            with open(path, 'r') as f:
                json_data = json.load(f)
            config = _json_to_configparser(json_data)
        else:
            # Try reading as INI format
            with open(path) as f:
                config.read_file(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        # If JSON parsing fails, try INI format
        try:
            with open(path) as f:
                config.read_file(f)
        except:
            pass

    if 'LAGER' not in config:
        config.add_section('LAGER')
    return config

def write_config_file(config, path=None):
    """
        Write out `config` into our config file.
        Defaults to JSON format for new files, preserves existing format for existing files.
    """
    if path is None:
        path = get_global_config_file_path()

    # Check if file exists and what format it's in
    file_exists = os.path.exists(path)
    is_json = file_exists and _is_json_format(path)

    # Default to JSON for new files or if existing file is JSON
    if not file_exists or is_json:
        # Read existing JSON data if file exists
        existing_json = {}
        if file_exists:
            with open(path, 'r') as f:
                try:
                    existing_json = json.load(f)
                except json.JSONDecodeError:
                    existing_json = {}

        # Convert config to JSON while preserving existing fields
        json_data = _configparser_to_json(config, existing_json)

        # Write back as JSON
        with open(path, 'w') as f:
            json.dump(json_data, f, indent=2)
    else:
        # Preserve INI format for existing INI files
        with open(path, 'w') as f:
            config.write(f)

def read_lager_json(path=None):
    """
        Read .lager JSON file directly.
        Returns empty dict if file doesn't exist or isn't valid JSON.
    """
    if path is None:
        path = find_devenv_config_path()

    if path is None or not os.path.exists(path):
        return {}

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def write_lager_json(data, path=None):
    """
        Write .lager JSON file directly.
    """
    if path is None:
        path = find_devenv_config_path()
        if path is None:
            raise ValueError("No .lager config path found")

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def get_devenv_json():
    """
        Return a path and JSON data for devenv.
        Exits with error if no config file is found.
    """
    config_path = find_devenv_config_path()
    if config_path is None:
        click.echo(f'Could not find {LAGER_CONFIG_FILE_NAME} in {os.getcwd()} or any parent directories', err=True)
        click.get_current_context().exit(1)

    data = read_lager_json(config_path)
    return config_path, data

def get_includes_from_config(config_path=None):
    """
        Read the 'includes' section from a .lager config file.
        Returns a dictionary mapping destination paths to source paths,
        with source paths resolved relative to the config file location.

        Example .lager file:
        {
            "includes": {
                "dtest": "../dtest",
                "shared": "/abs/path/to/shared"
            }
        }

        Returns: {"dtest": "/abs/path/to/dtest", "shared": "/abs/path/to/shared"}
    """
    if config_path is None:
        config_path = find_devenv_config_path()

    if config_path is None or not os.path.exists(config_path):
        return {}

    includes = {}

    try:
        # Check if file is in JSON format
        if _is_json_format(config_path):
            with open(config_path, 'r') as f:
                json_data = json.load(f)

            # Get includes section (support both 'includes' and 'INCLUDES')
            includes_data = json_data.get('includes') or json_data.get('INCLUDES')

            if includes_data and isinstance(includes_data, dict):
                # Resolve relative paths relative to the config file location
                config_dir = os.path.dirname(os.path.abspath(config_path))

                for dest_path, source_path in includes_data.items():
                    # If source_path is relative, resolve it relative to config file
                    if not os.path.isabs(source_path):
                        abs_source = os.path.abspath(os.path.join(config_dir, source_path))
                    else:
                        abs_source = source_path

                    includes[dest_path] = abs_source
        else:
            # INI format support (optional)
            config = configparser.ConfigParser()
            with open(config_path) as f:
                config.read_file(f)

            if config.has_section('includes') or config.has_section('INCLUDES'):
                section_name = 'includes' if config.has_section('includes') else 'INCLUDES'
                config_dir = os.path.dirname(os.path.abspath(config_path))

                for dest_path, source_path in config.items(section_name):
                    # If source_path is relative, resolve it relative to config file
                    if not os.path.isabs(source_path):
                        abs_source = os.path.abspath(os.path.join(config_dir, source_path))
                    else:
                        abs_source = source_path

                    includes[dest_path] = abs_source
    except Exception:
        # If anything goes wrong, just return empty dict (no includes)
        return {}

    return includes
