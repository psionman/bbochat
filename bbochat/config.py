"""Config for BBO Chat."""

from psiconfig import TomlConfig

from constants import CONFIG_PATH, USER_DATA_DIR

DEFAULT_CONFIG = {
    'data_directory': USER_DATA_DIR,
    'last_partner': 'eirikr',
    'last_greeting': 'Hi <opps>: <names>: <system>',
    'last_valediction': 'Thanks both',
    'randomize_name_order': True,
}


def get_config() -> TomlConfig:
    """Return the config file."""
    return TomlConfig(path=CONFIG_PATH, defaults=DEFAULT_CONFIG)


def save_config(config: TomlConfig) -> TomlConfig | None:
    # NB new attributes need to be updated in gui.write_config
    result = config.save()
    if result != config.STATUS_OK:
        return None
    config = TomlConfig(CONFIG_PATH)
    return config


config = get_config()
