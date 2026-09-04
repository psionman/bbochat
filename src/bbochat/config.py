"""Config for BBO Chat."""

from collections.abc import Callable
from pathlib import Path

from psiconfig import ConfigField
from psiconfig import TomlConfig as BaseTomlConfig

from bbochat.constants import (
    APP_NAME,
    CONFIG_PATH,
    DOCS_DIR,
    USER_DATA_DIR,
    ChatMode,
)

Listener = Callable[[], None]


# FIELDS for config, and to create tkinter variables in frm_config.py
# e.g. self.data_directory is a tk.StringVar
FIELDS = {
    "data_directory": ConfigField(str, USER_DATA_DIR),
    "tournament_notes_directory": ConfigField(
        str, str(Path(DOCS_DIR, APP_NAME))
    ),
    "randomize_name_order": ConfigField(bool, True),
    "show_tooltips": ConfigField(bool, True),
    "confirm_history_delete": ConfigField(bool, True),
}

DEFAULT_GEOMETRY = {
    "frm_main": "1100x540",
    "frm_edit_select": "500x500",
    "frm_config": "700x540",
    "frm_config_css": "500x400",
    "frm_text_dialog": "500x150",
    "frm_partner_edit": "500x500",
    "frm_report": "880x550",
    "frm_notes_edit": "880x550",
}

DEFAULT_COLOURS = {
    ChatMode.GREETINGS.value: "limegreen",
    ChatMode.VALEDICTION.value: "salmon",
    ChatMode.CHAT.value: "aqua",
    ChatMode.CHAT_DETAIL.value: "aqua",
}

DEFAULT_CONFIG = {
    "last_partner": "",
    "last_used_text": {str(mode.value): "" for mode in ChatMode},
    "geometry": DEFAULT_GEOMETRY,
    "colours": DEFAULT_COLOURS,
    "vertical_sashes": [(219, 1), (494, 1), (773, 1), (1055, 1)],
    "horizontal_sashes": [(1, 165)],
    "notes_sashes": [(530, 1)],
    "history_sashes": [(530, 1)],
    "css_body": {"name": "body", "color": "black", "font-size": 12},
    "css_h1": {"name": "h1", "color": "green", "font-size": 20},
    "css_h2": {"name": "h2", "color": "green", "font-size": 18},
    "css_h3": {"name": "h3", "color": "green", "font-size": 16},
    "css_p_ul": {
        "name": "p,ul",
        "color": "black",
        "font-size": 15,
        "font-weight": "normal",
    },
}

for name, field in FIELDS.items():
    DEFAULT_CONFIG[name] = field.default_value


class TomlConfig(BaseTomlConfig):
    """Redefinition of TomlConfig to allow for css."""

    def __init__(self, path: str, defaults: dict, restore_defaults: bool):
        super().__init__(path, defaults, restore_defaults)
        self._listeners: list[Listener] = []
        self.last_config = self.config.copy()

    def save(self) -> None:
        if "css" in self.config:
            self.config.pop("css")
        test_config = self.config.copy()
        test_config.pop("geometry", {})
        self.last_config.pop("geometry", {})
        if test_config != self.last_config:
            self.last_config = test_config.copy()
        super().save()
        # self._notify()

    # -- observer pattern for UI refresh -----------------------------
    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        self._listeners.remove(listener)

    def _notify(self) -> None:
        for listener in self._listeners:
            listener()


def get_config(restore_defaults: bool = False) -> TomlConfig:
    """Return the config file."""
    toml_config = TomlConfig(
        path=CONFIG_PATH,
        defaults=DEFAULT_CONFIG,
        restore_defaults=restore_defaults,
    )
    css = _get_css(toml_config)
    toml_config.css = css
    toml_config.config["css"] = css
    return toml_config


def _get_css(toml_config: TomlConfig) -> TomlConfig:
    def _update(toml_config: TomlConfig, css: dict, key: str):
        if key not in toml_config.config:
            return
        css_item = toml_config.config[key]
        css[css_item["name"]] = {
            key: item for key, item in css_item.items() if key != "name"
        }

    css = {}
    _update(toml_config, css, "css_body")
    _update(toml_config, css, "css_h1")
    _update(toml_config, css, "css_h2")
    _update(toml_config, css, "css_h3")
    _update(toml_config, css, "css_p_ul")
    return css


# Module-level singleton (TomlConfig) - this is the instance everyone imports.
config = get_config()
