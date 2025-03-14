"""Constants for the BBOChat app."""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir
import userpaths

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
DOCS_DIR = userpaths.get_my_documents()

# GUI
APP_TITLE = 'BBO Chat'
ICON_FILE = resolve_path('images/icon.png', __file__)

# Dates
YYYYMMDD = '%Y%m%d'

# Data
DATA_FILE = Path(USER_DATA_DIR, 'data.json')

TXT_FILE_TYPES = (
    ('text files', '*.txt'),
    ('All files', '*.*')
)

MODES = {
    'greeting': 0,
    'valediction': 1,
    'chat': 2,
    'chat-detail': 3,
    0: 'greeting',
    1: 'valediction',
    2: 'chat',
    3: 'chat-detail',
}

MODE_TEXT = {
    0: 'greeting',
    1: 'valediction',
    2: 'chat',
    3: 'chat-detail',
}

FRAME_WIDTH = 4000

GEOMETRY = {
    'frm_main': {
        'Linux': '1350x800',
        'Windows': '1350x800',
    },
    'frm_config': {
        'Linux': '700x300',
        'Windows': '700x300',
    },
}

META_CODES = {
    'uuid': 0,
    'text': 1,
    0: 'uuid',
    1: 'text'
}
