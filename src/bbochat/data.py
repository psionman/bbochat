"""Data manipulation for BBO Chat."""

import json

from bbochat import logger
from bbochat.constants import DATA_FILE, DONT_SAVE

OK = 0
FILE_NOT_FOUND = 1
INVALID_JSON = 2

if DONT_SAVE:
    logger.warn(f"DONT_SAVE={DONT_SAVE}")


class Partner:
    def __init__(self) -> None:
        self.username: str = ""
        self.name: str = ""
        self.system: str = ""
        self.greeting: str = ""
        self.notes: str = ""

    def __repr__(self):
        return f"Partner: {self.username} {self.name}"

    def serialize(self) -> dict:
        return [self.name, self.system, self.greeting, self.notes]

    def deserialize(self, username: str, item: list[str]) -> None:
        self.username = username
        if not item:
            return

        self.name = item[0]
        if len(item) < 2:
            return

        self.system = item[1]
        if len(item) < 3:
            return

        self.greeting = item[2]
        if len(item) < 4:
            return

        self.notes = item[3]


class Player:
    def __init__(self, name: str = "", username: str = "") -> None:
        self.name: str = name
        self.username: str = username

    def __repr__(self):
        return f"Player: {self.username} {self.name}"

    def serialize(self) -> dict:
        return {self.username: self.name}

    def deserialize(self, username, name):
        self.name = name
        self.username = username


class Pair:
    def __init__(self, username_1: str = "", username_2: str = "") -> None:
        if username_1 > username_2:
            username_1, username_2 = username_2, username_1
        self.username_1: str = username_1
        self.username_2: str = username_2

    def __repr__(self):
        return f"Pair: {self.username_1} {self.username_2}"

    def __eq__(self, other) -> bool:
        return (
            self.username_1 == other.username_1
            and self.username_2 == other.username_2
        )

    def serialize(self) -> dict:
        if self.username_1 > self.username_2:
            self.username_1, self.username_2 = self.username_2, self.username_1
        return [self.username_1, self.username_2]

    def deserialize(self, username_1, username_2):
        self.username_1 = username_1
        self.username_2 = username_2


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

    def read(self):
        raw_data = self._read_data_file()
        data = {} if raw_data == FILE_NOT_FOUND else self._get_json(raw_data)
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
        if data == INVALID_JSON:
            return INVALID_JSON

        for key, value in data.items():
            if key == "partners":
                self.partners = self._get_partners(value)
                self.data_sets["partners"] = self.partners
            elif key == "players":
                self.players = self._get_players(value)
                self.data_sets["players"] = self.players
            elif key == "pairs":
                self.pairs = self._get_pairs(value)
                self.data_sets["pairs"] = self.pairs
            elif key == "greetings":
                self.greetings = value
                self.data_sets["greetings"] = self.greetings
            elif key == "valedictions":
                self.valedictions = value
                self.data_sets["valediction"] = self.valedictions
            elif key == "chat":
                self.chat = value
                self.data_sets["chat"] = value
            elif key == "notes":
                self.notes = value
                self.data_sets["notes"] = self.notes
            elif key == "my_name":
                self.my_name = value
                self.data_sets["my_name"] = self.my_name

    def _read_data_file(self) -> str | int | None:
        try:
            with open(DATA_FILE, "r") as f_data:
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

    @staticmethod
    def _get_pairs(data: list) -> list[Player]:
        pairs = []
        for raw_pair in data:
            pair = Pair()
            pair.deserialize(raw_pair[0], raw_pair[1])
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
            "valedictions": self.data_sets["valediction"],
            "chat": self.data_sets["chat"],
            "notes": self.data_sets["notes"],
            "my_name": self.my_name,
        }
        # print("-" * 25)
        # for key, value in self.data_sets["chat"].items():
        #     print("save", key, value)
        json_data = self._data_to_json(output)
        # TODO: remove this when ready to save
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
