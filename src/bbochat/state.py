from pathlib import Path

import tomli_w
import tomllib

from bbochat.constants import STATE_DIR, ChatMode

DEFAULT_GEOMETRY = {
    "frm_main": "1154x101",
    "frm_edit_select": "500x500",
    "frm_config": "700x540+2920",
    "frm_config_css": "500x400",
    "frm_text_dialog": "500x150",
    "frm_partner_edit": "500x500",
    "frm_report": "880x550",
    "frm_notes_edit": "880x550",
}
DEFAULT_SASHES = {
    "vertical_sashes": [[219, 1], [526, 1], [773, 1], [1037, 1]],
    "horizontal_sashes": [[1, 291]],
    "notes_sashes": [[530, 1]],
    "history_sashes": [[1, 212]],
}

DEFAULT_PARTNER = "eirikr"


class State:
    def __init__(self):
        self.geometry = {}
        self.sashes = {}
        self.session = {}
        self.last_used_text = {}
        self.pinned_items = []

        self.get_state()

    def get_state(self) -> Path:
        state_file = Path(STATE_DIR, "state.toml")
        with open(state_file, "rb") as f:
            data = tomllib.load(f)
        self.geometry = data.get("geometry", {})
        if not self.geometry:
            self.geometry = DEFAULT_GEOMETRY
        self.sashes = data.get("sashes", {})
        if not self.sashes:
            self.sashes = DEFAULT_SASHES
        self.session = data.get("session", {})
        if not self.session:
            self.session["last_partner"] = DEFAULT_PARTNER
        self.last_used_text = data.get("last_used_text", {})
        if not self.last_used_text:
            self.last_used_text = {}

        self.history = {
            item[0]: ChatMode(item[1]) for item in data.get("history")
        }
        self.pinned_items = {
            item[0]: ChatMode(item[1]) for item in data.get("pinned_items")
        }
        # self.pinned_items = data.get("pinned_items", {})
        if not self.pinned_items:
            self.pinned_items = []
        # self.history = data.get("history", {})
        # if not self.history:
        #     self.history = []

    def serialize(self):
        return {
            "session": self.session,
            "last_used_text": self.last_used_text,
            "pinned_items": [
                (item, mode.value)
                for (item, mode) in self.pinned_items.items()
            ],
            "history": [
                (item, mode.value) for item, mode in self.history.items()
            ],
            "geometry": self.geometry,
            "sashes": self.sashes,
        }

    def save(self):
        data = self.serialize()
        state_file = Path(STATE_DIR, "state.toml")
        with open(state_file, "wb") as f:
            tomli_w.dump(data, f)

    def update(self, key: str, value: any):
        self.__dict__[key] = value
        self.save()


state = State()
