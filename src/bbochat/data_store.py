"""Data manipulation for BBO Chat."""

import json
from collections.abc import Callable

from bbochat import logger
from bbochat.constants import DATA_FILE, DONT_SAVE
from bbochat.pair import PairNew
from bbochat.partner import Partner
from bbochat.player import Player

Listener = Callable[[], None]

OK = 0
FILE_NOT_FOUND = 1
INVALID_JSON = 2

if DONT_SAVE:
    logger.warn(f"DONT_SAVE={DONT_SAVE}")


class DataStore:
    def __init__(self) -> None:
        self.partners = {}
        self.players = {}
        self.pairs = []
        self.greetings = []
        self.valedictions = []
        # self.chat = []
        self.notes = {}
        self.my_name = ""
        self._listeners = []
        self._name_1: str = ""
        self._name_2: str = ""
        self._username_1: str = ""
        self._username_2: str = ""
        self.read()

    def read(self):
        raw_data = self._read_data_file()
        application_data = (
            {} if raw_data == FILE_NOT_FOUND else self._get_json(raw_data)
        )
        self.data_sets = {
            "partners": {},
            "pairs": [],
            "players": {},
            "greeting": [],
            "valediction": [],
            "chat": {},
            "notes": {},
            "my_name": "",
        }
        if application_data == INVALID_JSON:
            return INVALID_JSON

        data_sets = {
            "players": self._get_players,
            "partners": self._get_partners,
            "pairs": self._get_pairs,
            "greetings": lambda x: x,
            "valedictions": lambda x: x,
            "chat": lambda x: x,
            "notes": lambda x: x,
            "my_name": lambda x: x,
        }
        for data_set, getter in data_sets.items():
            if data_set in application_data:
                setattr(self, data_set, getter(application_data[data_set]))
                self.data_sets[data_set] = getattr(self, data_set)
        # print(self.data_sets["valedictions"])
        # self.valediction = self.data_sets["valedictions"]
        self._notify()

    def _read_data_file(self) -> str | int | None:
        try:
            with open(DATA_FILE) as f_data:
                return f_data.read()
        except FileNotFoundError:
            return FILE_NOT_FOUND
        return None

    @staticmethod
    def _get_json(data: str) -> dict | None:
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            print(f"*** Invalid json in {DATA_FILE}***")
            return INVALID_JSON

    @staticmethod
    def _get_partners(data: dict) -> dict[str, Partner]:
        partners = {}
        for username, item in data.items():
            partner = Partner()
            partner.deserialize(username, item)
            partners[username] = partner
        return partners

    @staticmethod
    def _get_players(data: dict) -> dict[str, Player]:
        players = {}
        for username, item in data.items():
            player = Player()
            player.deserialize(username, item)
            players[player.username] = player
        return players

    def _get_pairs(self, data: tuple[str]) -> list[Player]:
        pairs = []
        for pair_list in data:
            pair = PairNew(
                self.players[pair_list[0]], self.players[pair_list[1]]
            )
            pairs.append(pair)
        return pairs

    def save(self):
        output = {
            "partners": {
                partner.username: partner.serialize()
                for partner in self.partners.values()
            },
            "pairs": [pair.serialize() for pair in self.pairs],
            "players": {
                player.username: player.name
                for player in self.players.values()
            },
            "greetings": self.data_sets["greetings"],
            "valedictions": self.data_sets["valedictions"],
            "chat": self.data_sets["chat"],
            "notes": self.data_sets["notes"],
            "my_name": self.my_name,
        }
        json_data = self._data_to_json(output)
        self._notify()
        return self._write_data_file(json_data)

    @staticmethod
    def _data_to_json(output: dict) -> str:
        return json.dumps(output)

    @staticmethod
    def _write_data_file(json_data: str):
        if DONT_SAVE:
            logger.warning(f"DONT_SAVE={DONT_SAVE}")
            return None

        try:
            with open(DATA_FILE, "w") as f_data:
                bytes_written = f_data.write(json_data)
                logger.info("data saved")
                return bytes_written

        except FileNotFoundError:
            logger.error(f"File not found: {DATA_FILE}")
            return FILE_NOT_FOUND

        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return None

    # -- observer pattern for UI refresh -----------------------------
    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        self._listeners.remove(listener)

    def _notify(self) -> None:
        for listener in self._listeners:
            listener()


# Module-level singleton - this is the instance everyone imports.
data_store = DataStore()
# data_store.read()
