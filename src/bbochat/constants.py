"""Constants for the BBOChat app."""

from enum import Enum
from pathlib import Path

import userpaths
from platformdirs import user_config_dir, user_data_dir, user_state_dir

# General
AUTHOR = "Jeff Watkins"
APP_NAME = "bbochat"
APP_AUTHOR = "psionman"
# HTML_DIR = resolve_path('html', __file__)
HELP_URI = ""
DATA_DIR = str(Path(user_data_dir(APP_NAME, AUTHOR)))

# Config
CONFIG_DIR = user_config_dir(APP_NAME, APP_AUTHOR)
CONFIG_PATH = Path(CONFIG_DIR, "config.toml")
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
DOCS_DIR = userpaths.get_my_documents()
STATE_DIR = user_state_dir(APP_NAME, APP_AUTHOR)

# GUI
APP_TITLE = "BBO Chat"
ICON_DIR = f"{Path(__file__).parent}/icons/"
ICON_FILE = Path(
    Path(__file__).parent, "images", "chat-processing-outline.png"
)

# Dates
YYYYMMDD = "%Y%m%d"

# Data
DATA_FILE = Path(USER_DATA_DIR, "data.json")
DONT_SAVE = False

TXT_FILE_TYPES = (("text files", "*.txt"), ("All files", "*.*"))


class ChatMode(Enum):
    GREETINGS = 0
    VALEDICTION = 1
    CHAT = 2
    CHAT_DETAIL = 3


MODE_TEXT = {
    0: "greeting",
    1: "valediction",
    2: "general text",
    3: "chat-detail",
}

FRAME_WIDTH = 4000

GEOMETRY = {
    "frm_main": {
        "Linux": "1350x800",
        "Windows": "1350x800",
    },
    "frm_config": {
        "Linux": "700x300",
        "Windows": "700x300",
    },
}


HTML_STYLE = """
    <style>
        body {
            font-size: 12px;
        }
        h1 {
            color: green;
            font-size: 20px;
            }
        h2 {
            color: green;
            font-size: 16px;
            }
        p, ul {
            color: black;
            font-size: 15px;
            font-weight: normal;
            }
    </style>
    """
xxx = "body{font-size:12px;}h1{color:green;font-size:20px;}h2{color:green;font-size:16px;}p,ul{color:black;font-size:15px;font-weight:normal;}"

HTML_TEST = """
# Heading 1

## Heading 2

### Heading 3

Text as it will appear
"""
