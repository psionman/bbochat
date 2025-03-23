"""Config for BBO Chat."""
from pathlib import Path

from psiconfig import TomlConfig

from constants import CONFIG_PATH, USER_DATA_DIR, APP_NAME, DOCS_DIR


DEFAULT_CONFIG = {
    'data_directory': USER_DATA_DIR,
    'last_partner': '',
    'last_greeting': '',
    'last_valediction': '',
    'last_chat': '',
    'randomize_name_order': True,
    'show_tooltips': True,
    'tournament_notes_directory': str(Path(DOCS_DIR, APP_NAME)),
    'geometry': {
        'frm_main': '1100x540',
        'frm_edit': '500x500',
        'frm_config': '700x540',
        'frm_config_css': '500x400',
        'frm_text_dialog': '500x150',
        'frm_partner_edit': '500x500',
        'frm_report': '880x550',
        'frm_notes_edit': '880x550',
    },
    'colours': {
        'greeting': 'limegreen;',
        'valediction': 'salmon',
        'chat': 'aqua',
    },
    'vertical_sashes': [(250, 1), (465, 1), (720, 1)],
    'horizontal_sashes': [(1, 165)],
    'notes_sashes': [(530, 1)],
    'css': {
        'body': {'color': 'black', 'font-size': 12},
        'h1': {'color': 'green', 'font-size': 20},
        'h2': {'color': 'green', 'font-size': 18},
        'h3': {'color': 'green', 'font-size': 16},
        'p,ul': {'color': 'black', 'font-size': 15, 'font-weight': 'normal'},
    },
}


def get_config(restore_defaults: bool = False) -> TomlConfig:
    """Return the config file."""
    return TomlConfig(
        path=CONFIG_PATH,
        defaults=DEFAULT_CONFIG,
        restore_defaults=restore_defaults)


def save_config(config: TomlConfig) -> TomlConfig | None:
    ic()
    result = config.save()
    return None if result != config.STATUS_OK else config


config = get_config()
