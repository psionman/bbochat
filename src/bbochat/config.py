"""Config for BBO Chat."""
from pathlib import Path

from psiconfig import TomlConfig as BaseTomlConfig

from bbochat.constants import (
    CONFIG_PATH, USER_DATA_DIR, APP_NAME, DOCS_DIR, ChatMode)


class TomlConfig(BaseTomlConfig):
    """Redefinition of TomlConfig to allow for css."""
    def __init__(self, path: str, defaults: dict, restore_defaults: bool):
        super().__init__(path, defaults, restore_defaults)

    def save(self) -> None:
        if 'css' in self.config:
            self.config.pop('css')
        super().save()


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
        # 'greeting': 'limegreen',
        # 'valediction': 'salmon',
        # 'chat': 'aqua',
        ChatMode.GREETING.name: 'limegreen',
        f'{ChatMode.VALEDICTION}': 'salmon',
        f'{ChatMode.CHAT}': 'aqua',
    },
    'vertical_sashes': [(250, 1), (465, 1), (720, 1)],
    'horizontal_sashes': [(1, 165)],
    'notes_sashes': [(530, 1)],
    'css_body': {'name': 'body', 'color': 'black', 'font-size': 12},
    'css_h1': {'name': 'h1', 'color': 'green', 'font-size': 20},
    'css_h2': {'name': 'h2', 'color': 'green', 'font-size': 18},
    'css_h3': {'name': 'h3', 'color': 'green', 'font-size': 16},
    'css_p_ul': {
        'name': 'p,ul', 'color': 'black', 'font-size': 15,
        'font-weight': 'normal'},
    # 'css': {
    #     'body': {'color': 'black', 'font-size': 12},
    #     'h1': {'color': 'green', 'font-size': 20},
    #     'h2': {'color': 'green', 'font-size': 18},
    #     'h3': {'color': 'green', 'font-size': 16},
    #     'p,ul': {'color': 'black', 'font-size': 15, 'font-weight': 'normal'},
    # },
}


def get_config(restore_defaults: bool = False) -> TomlConfig:
    """Return the config file."""
    toml_config = TomlConfig(
        path=CONFIG_PATH,
        defaults=DEFAULT_CONFIG,
        restore_defaults=restore_defaults)
    css = _get_css(toml_config)
    toml_config.css = css
    toml_config.config['css'] = css
    return toml_config


def _get_css(toml_config: TomlConfig) -> TomlConfig:
    def _update(toml_config: TomlConfig, css: dict, key: str):
        if key not in toml_config.config:
            return
        css_item = toml_config.config[key]
        css[css_item['name']] = {
            key: item for key, item in css_item.items() if key != 'name'}

    css = {}
    _update(toml_config, css, 'css_body')
    _update(toml_config, css, 'css_h1')
    _update(toml_config, css, 'css_h2')
    _update(toml_config, css, 'css_h3')
    _update(toml_config, css, 'css_p_ul')
    return css


config = get_config()
