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

if len(ary) > 0:
    ENV_FILE = ary[0]
    load_dotenv(ENV_FILE)
    CONFIG_LOADED = True
    API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')  # env value is prior to config file

if API_KEY is None:
    API_KEY = _API_KEY

# Note: API key validation is now done in main.py when actually needed
# This allows the module to be imported without side effects

from .main import main



