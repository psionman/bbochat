"""Config for BBO Chat."""

from psiconfig import TomlConfig

from constants import CONFIG_PATH, USER_DATA_DIR

DEFAULT_CONFIG = {
    'data_directory': USER_DATA_DIR,
    'last_partner': '',
    'last_greeting': '',
    'last_valediction': '',
    'randomize_name_order': True,
    'notes_path': '',
    'geometry': {
        'frm_main': '1350x800',
        'frm_edit': '500x600',
        'frm_edit_tree': '500x600',
        'frm_config': '700x300',
    },
    'colours': {
        'greeting': 'limegreen',
        'valediction': 'salmon',
        'chat': 'aqua',
    },
    'vertical_sashes': [],
    'horizontal_sashes': [],
}


def get_config() -> TomlConfig:
    """Return the config file."""
    return TomlConfig(path=CONFIG_PATH, defaults=DEFAULT_CONFIG)


def save_config(config: TomlConfig) -> TomlConfig | None:
    # NB new attributes need to be updated in gui.write_config
    result = config.save()
    return None if result != config.STATUS_OK else config


config = get_config()
