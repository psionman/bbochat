"""Partner's class for BBO Chat."""


class Partner():
    def __init__(self) -> None:
        self.name: str
        self.system: str
        self.notes: str

    def __repr__(self):
        return f'Partner: {self.name}'

    def deserialize(self, name, system):
        self.name = name
        self.system = system


def get_partners(data: dict) -> list[Partner]:
    partners = []
    for name, item in data.items():
        partner = Partner()
        partner.deserialize(name, item)
        partners.append(partner)
    return partners
