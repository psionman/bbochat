# message.py
"""Single source of truth for message."""

import random
import re
from collections.abc import Callable

import clipboard
import emoji

from bbochat.constants import ChatMode
from bbochat.pair import PairNew
from bbochat.partner import Partner

DEFAULT_MODE = ChatMode.GREETINGS

Listener = Callable[[], None]


class Message:
    """Message class."""

    def __init__(self) -> None:
        self._mode: ChatMode = DEFAULT_MODE
        self._message: str = ""
        self._randomize: bool = False
        self._my_name: str = ""
        self._partner: Partner | None = None
        self._pair: PairNew | None = None
        self.listeners: list[Listener] = []
        self.selected_messages = {}

    @property
    def mode(self) -> ChatMode:
        return self._mode

    @mode.setter
    def mode(self, value: ChatMode) -> None:
        self._mode = value
        self._notify()

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value
        self._notify()

    @property
    def my_name(self) -> str:
        return self._my_name

    @my_name.setter
    def my_name(self, value: str) -> None:
        self._my_name = value
        self._notify()

    @property
    def partner(self) -> Partner:
        return self._partner

    @partner.setter
    def partner(self, value: Partner) -> None:
        if not isinstance(value, Partner):
            raise TypeError("partner must be a Partner instance")
        self._partner = value
        if self._partner:
            self.message = self._partner.greeting
        self._notify()

    @property
    def pair(self) -> PairNew:
        return self._pair

    @pair.setter
    def pair(self, value: PairNew) -> None:
        self._pair = value
        self._notify()

    @property
    def randomize(self) -> bool:
        return self._randomize

    @randomize.setter
    def randomize(self, value: bool) -> None:
        self._randomize = value
        self._notify()

    def output_message(self) -> str:
        names, system = self._get_names_and_system()
        opps = self._get_opps()

        message = self.message.replace("<opps>", opps)
        message = message.replace("<names>", names)
        message = message.replace("<system>", system)
        message = self._insert_emojis(message)
        clipboard.copy(message)
        return message

    def _get_names_and_system(self) -> tuple[str, str]:
        if self._partner:
            names = f"{self._partner.name} and {self._my_name}"
            system = self._partner.system
        else:
            names = f"{self._my_name}"
            system = ""
        return names, system

    def _insert_emojis(self, message: str) -> str:
        emoji_re = r":.*:"

        while True:
            match = re.search(emoji_re, message)
            if not match:
                break
            emoji_text = match.group()
            emoji_ = emoji.emojize(emoji_text)
            message = message.replace(emoji_text, emoji_)
            if emoji_text == emoji_:
                break
        return message

    def _get_opps(self) -> str:
        if not self.pair:
            return ""

        opp_1, opp_2 = self.pair.player_1.name, self.pair.player_2.name
        if self._randomize:
            opps = [opp_1, opp_2]
            choice = random.choice([0, 1])
            opp_1 = opps[choice]
            choice = (choice + 1) % 2
            opp_2 = opps[choice]

        if opp_1.lower() == "robot":
            opp_1, opp_2 = opp_2, opp_1
        if opp_2.lower() == "robot":
            opp_2 = ""

        if opp_1:
            return f"{opp_1} and {opp_2}" if opp_2 else opp_1
        return opp_2

    # -- observer pattern for UI refresh -----------------------------
    def subscribe(self, listener: Listener) -> None:
        self.listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        self.listeners.remove(listener)

    def _notify(self, caller: str = "") -> None:
        if caller:
            print(f"Notifying listeners from {caller}")
        for listener in self.listeners:
            listener()


chat_message = Message()
