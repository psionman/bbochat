# message.py
"""Single source of truth for message."""

import random
import re
from collections.abc import Callable

import clipboard
import emoji

from bbochat.constants import ChatMode
from bbochat.partner import Partner

DEFAULT_MODE = ChatMode.GREETINGS

Listener = Callable[[], None]


class Message:
    """Message class."""

    def __init__(self) -> None:
        self.mode = DEFAULT_MODE
        self.message = ""
        self.randomize = False
        self._my_name = ""
        self._partner: Partner = None
        self._opponent_1 = ""
        self._opponent_2 = ""
        self.listeners = []

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
        self._notify()

    @property
    def opponent_1(self) -> str:
        return self._opponent_1

    @opponent_1.setter
    def opponent_1(self, value: str) -> None:
        self._opponent_1 = value
        self._notify()

    @property
    def opponent_2(self) -> str:
        return self._opponent_2

    @opponent_2.setter
    def opponent_2(self, value: str) -> None:
        self._opponent_2 = value
        self._notify()

    def update_clipboard(
        self, message: str = "", mode: int = None, *args
    ) -> None:
        if mode is None:
            mode = DEFAULT_MODE
        self.mode = mode
        self._set_clipboard_colour()
        self._create_message(message)

    def _create_message(self, message: str) -> None:
        if self._partner:
            names = f"{self._partner.name} and {self._my_name}"
            system = self._partner.system
        else:
            names = f"{self._my_name}"
            system = ""

        opps = self._get_opps()
        message = message.replace("<opps>", opps)
        message = message.replace("<names>", names)
        message = message.replace("<system>", system)
        self.clipboard.set(message)
        self.copy_to_clipboard()

    def copy_to_clipboard(self, *args) -> None:
        text = self.clipboard.get()
        emoji_re = r":.*:"

        found = True
        while found:
            match = re.search(emoji_re, text)
            if not match:
                break
            emoji_text = match.group()
            emoji_ = emoji.emojize(emoji_text)
            text = text.replace(emoji_text, emoji_)
            if emoji_text == emoji_:
                found = False
        clipboard.copy(text)

    def _get_opps(self) -> str:
        opp_1, opp_2 = self._opponent_1, self._opponent_2
        if self.randomize:
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
