# player.py


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
