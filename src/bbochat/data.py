"""Data manipulation for BBO Chat."""

import json

from constants import DATA_FILE

OK = 0
FILE_NOT_FOUND = 1
INVALID_JSON = 2


class Partner():
    def __init__(self) -> None:
        self.username: str = ''
        self.name: str = ''
        self.system: str = ''
        self.greeting: str = ''
        self.notes: str = ''

    def __repr__(self):
        return f'Partner: {self.username} {self.name}'

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


class Player():
    def __init__(self, name: str = '', username: str = '') -> None:
        self.name: str = name
        self.username: str = username

    def __repr__(self):
        return f'Player: {self.username} {self.name}'

    def serialize(self) -> dict:
        return {self.username: self.name}

    def deserialize(self, username, name):
        self.name = name
        self.username = username


class Pair():
    def __init__(self, username_1: str = '', username_2: str = '') -> None:
        if username_1 > username_2:
            username_1, username_2 = username_2, username_1
        self.username_1: str = username_1
        self.username_2: str = username_2

    def __repr__(self):
        return f'Pair: {self.username_1} {self.username_2}'

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


class DataStore():
    def __init__(self) -> None:
        self.partners = {}
        self.players = {}
        self.pairs = []
        self.greetings = []
        self.valedictions = []
        self.chat = []
        self.my_name = ''

    def read(self):
        raw_data = self._read_data_file()
        if raw_data == FILE_NOT_FOUND:
            return FILE_NOT_FOUND

        data = self._get_json(raw_data)
        if self._get_json(raw_data) == INVALID_JSON:
            return INVALID_JSON

        if 'partners' in data:
            self.partners = self._get_partners(data['partners'])

        if 'players' in data:
            self.players = self._get_players(data['players'])

        if 'pairs' in data:
            self.pairs = self._get_pairs(data['pairs'])

        if 'greetings' in data:
            self.greetings = data['greetings']

        if 'valedictions' in data:
            self.valedictions = data['valedictions']

        if 'chat' in data:
            self.chat = data['chat']

        if 'my_name' in data:
            self.my_name = data['my_name']

    def _read_data_file(self) -> str | int | None:
        try:
            with open(DATA_FILE, 'r') as f_data:
                return f_data.read()
        except FileNotFoundError:
            return FILE_NOT_FOUND
        return None

    @staticmethod
    def _get_json(data: str) -> dict | None:
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            return INVALID_JSON
        return None

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
            'partners': {partner.username: partner.serialize()
                         for partner in self.partners.values()},
            'pairs': [pair.serialize() for pair in self.pairs],
            'players': {
                player.username: player.name
                for player in self.players.values()
            },
            'greetings': self.greetings,
            'valedictions': self.valedictions,
            'chat': self.chat,
            'my_name': self.my_name,
        }
        json_data = self._data_to_json(output)
        return self._write_data_file(json_data)

    @staticmethod
    def _data_to_json(output: dict) -> str:
        return json.dumps(output)

    @staticmethod
    def _write_data_file(json_data: str):
        try:
            with open(DATA_FILE, 'w') as f_data:
                return f_data.write(json_data)
        except FileNotFoundError:
            return FILE_NOT_FOUND
        return None
