"""Master tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from constants import MODES
from config import get_config

from forms.frm_players import PlayersFrame
from forms.frm_text_selection import TextSelectionFrame
from forms.frm_chat import ChatFrame

FRAME_WIDTH = 4000


class MasterFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root
        self.config = get_config()
        self.data_store = parent.data_store

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

        self.chat = parent.chat
        self.chat_list = parent.chat_list
        self.chat_line = parent.chat_line

        self.master_frame = self._master_frame(master)

        # self.parent.root.update()
        if self.config.vertical_sashes:
            for index, sash in enumerate(self.config.vertical_sashes):
                self.master_frame.sash_place(index, sash[0], 0)

        if self.config.horizontal_sashes:
            for index, sash in enumerate(self.config.horizontal_sashes):
                self.chat_panel.sash_place(index, 0, sash[1])

    def _master_frame(self, master) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.HORIZONTAL)

        players = PlayersFrame(self, frame)
        self.players_frame = players.players_frame
        self.pair_tree = players.pair_tree
        self.search_entry = players.search_entry
        frame.add(self.players_frame, width=FRAME_WIDTH)

        greetings = TextSelectionFrame(self, frame, MODES['greeting'])
        frame.add(greetings.main_frame, width=FRAME_WIDTH)

        valedictions = TextSelectionFrame(self, frame, MODES['valediction'])
        frame.add(valedictions.main_frame, width=FRAME_WIDTH)

        chat_frame = ChatFrame(self, frame)
        self.chat_frame = chat_frame.chat_frame
        self.chat_panel = chat_frame.chat_panel
        frame.add(self.chat_frame, width=FRAME_WIDTH)

        return frame
