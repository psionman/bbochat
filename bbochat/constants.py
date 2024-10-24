"""Constants for the BBOChat app."""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir

from psiutils.known_paths import resolve_path

# General
AUTHOR = 'Jeff Watkins'
APP_NAME = 'bbochat'
APP_AUTHOR = 'psionman'
# HTML_DIR = resolve_path('html', __file__)
HELP_URI = ''

# Config
CONFIG_PATH = Path(user_config_dir(APP_NAME, APP_AUTHOR), 'config.toml')
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)

# GUI
APP_TITLE = 'Application Title'
ICON_FILE = resolve_path('images/icon.png', __file__)

# Data
DATA_FILE = Path(USER_DATA_DIR, 'data.json')

MODES = {
    'greeting': 0,
    'valediction': 1,
    'chat': 2,
    0: 'greeting',
    1: 'valediction',
    2: 'chat',
}

MODE_COLOURS = {
    0: 'limegreen',
    1: 'salmon',
    2: 'aqua',
}
