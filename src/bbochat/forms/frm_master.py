"""Master tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from config import get_config

from forms.frm_players import PlayersFrame
from forms.frm_greeting import GreetingFrame
from forms.frm_valediction import ValedictionFrame
from forms.frm_chat import ChatFrame


class MasterFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root
        self.config = get_config()

        # tk variables
        self.search = parent.search
        self.pairs = parent.pairs
        self.pairs_list = parent.pairs_list
        self.search_pairs = parent.search_pairs
        self.players = parent.players

        self.name_1 = parent.name_1
        self.name_2 = parent.name_2
        self.username_1 = parent.username_1
        self.username_2 = parent.username_2

        self.greeting = parent.greeting
        self.greetings = parent.greetings
        self.greetings_list = parent.greetings_list

        self.valediction = parent.valediction
        self.valedictions = parent.valedictions

        self.chat = parent.chat
        self.chat_list = parent.chat_list
        self.chat_line = parent.chat_line

        self.master_frame = self._master_frame(master)

        self.parent.root.update()
        if self.config.vertical_sashes:
            for index, sash in enumerate(self.config.vertical_sashes):
                self.master_frame.sash_place(index, sash[0], 0)

    def _master_frame(self, master) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.HORIZONTAL)

        players = PlayersFrame(self, frame)
        self.players_frame = players.players_frame
        self.pair_tree = players.pair_tree
        self.search_entry = players.search_entry
        frame.add(self.players_frame)

        self.greetings_frame = GreetingFrame(self, frame).greeting_frame
        frame.add(self.greetings_frame)

        valediction_frame = ValedictionFrame(self, frame).valediction_frame
        frame.add(valediction_frame)

        self.chat_frame = ChatFrame(self, frame).chat_frame
        frame.add(self.chat_frame)

        return frame
