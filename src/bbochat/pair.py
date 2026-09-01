# pair.py


from bbochat.player import Player


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


class PairNew:
    def __init__(self, player_1: Player, player_2: Player) -> None:
        self.player_1: Player = player_1
        self.player_2: Player = player_2

    def __repr__(self):
        return f"Pair: {self.player_1} {self.player_1}"

    def __eq__(self, other) -> bool:
        return (
            self.player_1.username == other.player_1.username
            and self.player_2.username == other.player_2.username
        )

    def serialize(self) -> dict:
        if self.player_1.username > self.player_2.username:
            self.player_1, self.player_2 = self.player_2, self.player_1
        return [self.player_1.username, self.player_2.username]

    def deserialize(self, username_1, username_2):
        self.username_1 = username_1
        self.username_2 = username_2
