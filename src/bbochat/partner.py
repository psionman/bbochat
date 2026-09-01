# partner.py


class Partner:
    def __init__(self) -> None:
        self.username: str = ""
        self.name: str = ""
        self.system: str = ""
        self.greeting: str = ""
        self.notes: str = ""

    def __repr__(self):
        return f"Partner: {self.username}"

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
