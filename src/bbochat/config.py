"""Config for BBO Chat."""

from psiconfig import TomlConfig

from constants import CONFIG_PATH, USER_DATA_DIR

DEFAULT_CONFIG = {
    'data_directory': USER_DATA_DIR,
    'last_partner': '',
    'last_greeting': '',
    'last_valediction': '',
    'last_chat': '',
    'randomize_name_order': True,
    'show_tooltips': True,
    'notes_path': '',
    'geometry': {
        'frm_main': '1250x700',
        'frm_edit': '500x600',
        'frm_config': '700x350',
        'frm_text_dialog': '500x150',
    },
    'colours': {
        'greeting': 'limegreen',
        'valediction': 'salmon',
        'chat': 'aqua',
    },
    'vertical_sashes': [(250, 1), (500, 1), (750, 1)],
    'horizontal_sashes': [(1, 200)],
}


def get_config() -> TomlConfig:
    """Return the config file."""
    return TomlConfig(path=CONFIG_PATH, defaults=DEFAULT_CONFIG)


def save_config(config: TomlConfig) -> TomlConfig | None:
    result = config.save()
    return None if result != config.STATUS_OK else config


config = get_config()
