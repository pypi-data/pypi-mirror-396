"""
aici  CLI for AI

This module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

test
    env only
    env and configuration file
    configuration file only

"""
import os
import sys
from .version import __version__
from dotenv import load_dotenv
import platform
import re

env_candidates = []
if platform.system() == 'Windows': # Windows specific
    env_candidates.extend([
        os.path.expanduser('~/AppData/Local/aici/config'), # 1st priority
        os.path.expanduser('~/AppData/Roaming/aici/config')
    ]) # 2nd priority
env_candidates.extend([
            os.path.expanduser('~/.config/aici/config'), # 1st priority
            os.path.expanduser('~/.aici')]) # 2nd priority

API_KEY = None
_API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('DEEPSEEK_API_KEY') # preserve value before reading config file

ary = []
for fn in env_candidates:
    if os.path.exists(fn):
        ary.append(fn)

# Global variables to track config file loading status
ENV_FILE = None
CONFIG_LOADED = False
CONFIG_VALIDATION_ERRORS = []

def validate_config_file(file_path):
    """
    Validate configuration file and return list of issues found.

    Args:
        file_path (str): Path to config file

    Returns:
        list: List of validation error messages
    """
    errors = []

    if not os.path.exists(file_path):
        return [f"Config file not found: {file_path}"]

    if not os.path.isfile(file_path):
        return [f"Config path is not a file: {file_path}"]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Cannot read config file: {e}"]

    if not lines:
        errors.append(f"Config file is empty: {file_path}")
        return errors

    # Check for valid key-value pairs
    valid_keys = {
        'AICI_OPENAI_KEY', 'OPENAI_API_KEY',
        'AICI_DEEPSEEK_KEY', 'DEEPSEEK_API_KEY',
        'AICI_MODEL', 'AICI_OPENAI_MODEL', 'AICI_DEEPSEEK_MODEL',
        'AICI_SYSTEM', 'AICI_SYSTEM_FILE'
    }

    has_api_key = False
    line_number = 0

    for line in lines:
        line_number += 1
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue

        # Check for key=value format
        if '=' not in stripped:
            errors.append(f"Line {line_number}: Invalid format (missing '='): {stripped[:50]}")
            continue

        key, value = stripped.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Check if key is recognized
        if key not in valid_keys:
            errors.append(f"Line {line_number}: Unknown key '{key}' (will be ignored)")

        # Check for API keys
        if key in {'AICI_OPENAI_KEY', 'OPENAI_API_KEY', 'AICI_DEEPSEEK_KEY', 'DEEPSEEK_API_KEY'}:
            if value:
                has_api_key = True
                # Validate API key format (should start with 'sk-')
                if not value.startswith('sk-'):
                    errors.append(f"Line {line_number}: API key '{key}' should start with 'sk-'")
                # Check if key looks too short
                if len(value) < 20:
                    errors.append(f"Line {line_number}: API key '{key}' seems too short (may be invalid)")
            else:
                errors.append(f"Line {line_number}: API key '{key}' is empty")

    if not has_api_key:
        errors.append("No valid API key found in config file")
        errors.append("  Add one of: AICI_OPENAI_KEY, OPENAI_API_KEY, AICI_DEEPSEEK_KEY, or DEEPSEEK_API_KEY")

    return errors

def show_config_advice():
    """Show helpful advice about configuration if there are issues."""
    if not CONFIG_VALIDATION_ERRORS:
        return

    print("⚠️  Configuration File Issues Detected:", file=sys.stderr)
    print(file=sys.stderr)

    for error in CONFIG_VALIDATION_ERRORS:
        print(f"  • {error}", file=sys.stderr)

    print(file=sys.stderr)
    print("📝 Configuration File Help:", file=sys.stderr)
    print(file=sys.stderr)
    print("  Config file locations (in priority order):", file=sys.stderr)
    if platform.system() == 'Windows':
        print("    1. ~/AppData/Local/aici/config", file=sys.stderr)
        print("    2. ~/AppData/Roaming/aici/config", file=sys.stderr)
    print("    3. ~/.config/aici/config", file=sys.stderr)
    print("    4. ~/.aici", file=sys.stderr)
    print(file=sys.stderr)
    print("  Required format:", file=sys.stderr)
    print("    AICI_OPENAI_KEY=sk-your-api-key-here", file=sys.stderr)
    print("    # or", file=sys.stderr)
    print("    AICI_DEEPSEEK_KEY=sk-your-api-key-here", file=sys.stderr)
    print(file=sys.stderr)
    print("  Get API keys:", file=sys.stderr)
    print("    OpenAI:   https://platform.openai.com/api-keys", file=sys.stderr)
    print("    DeepSeek: https://platform.deepseek.com/", file=sys.stderr)
    print(file=sys.stderr)

if len(ary) > 0:
    ENV_FILE = ary[0]
    # Validate config file before loading
    CONFIG_VALIDATION_ERRORS = validate_config_file(ENV_FILE)

    load_dotenv(ENV_FILE)
    CONFIG_LOADED = True
    API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')  # env value is prior to config file

if API_KEY is None:
    API_KEY = _API_KEY

# Note: API key validation is now done in main.py when actually needed
# This allows the module to be imported without side effects

from .main import main



