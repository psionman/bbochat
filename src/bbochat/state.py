from pathlib import Path

import tomli_w
import tomllib

from bbochat.constants import STATE_DIR


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
        self.sashes = data.get("sashes", {})
        self.session = data.get("session", {})
        self.last_used_text = data.get("last_used_text", {})
        self.pinned_items = data.get("pinned_items", {})

    def serialize(self):
        return {
            "session": self.session,
            "last_used_text": self.last_used_text,
            "pinned_items": self.pinned_items,
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
