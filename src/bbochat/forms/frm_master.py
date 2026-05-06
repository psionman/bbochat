"""Master tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from bbochat.constants import FRAME_WIDTH, ChatMode
from bbochat.config import get_config

from bbochat.forms.frm_opponents import OpponentsFrame
from bbochat.forms.frm_text_selection import TextSelectionFrame
from bbochat.data_manager import DataManager
from bbochat.forms.frm_chat import ChatFrame


class MasterFrame():
    def __init__(self, parent, master):
        # pylint: disable=no-member)
        self.parent = parent
        self.root = parent.root
        # used in text_selection
        self.update_clipboard = parent.update_clipboard
        self.config = get_config()
        self.data_store = parent.data_store

        self.chat = parent.chat
        self.chat_list = parent.chat_list
        self.chat_line = parent.chat_line

        self.master_frame = self._master_frame(master)

        if self.config.vertical_sashes:
            for index, sash in enumerate(self.config.vertical_sashes):
                self.master_frame.sash_place(index, sash[0], 0)

        if self.config.horizontal_sashes:
            for index, sash in enumerate(self.config.horizontal_sashes):
                self.chat_panel.sash_place(index, 0, sash[1])

    def _master_frame(self, master) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.HORIZONTAL)

        opponents_frame = OpponentsFrame(self, frame)
        self.opponents_frame = opponents_frame
        self.players_frame = opponents_frame.opponents_frame
        self.pair_tree = opponents_frame.pair_tree
        self.search_entry = opponents_frame.search_entry
        frame.add(self.players_frame, width=FRAME_WIDTH)

        mode = ChatMode.GREETING
        data_set = self.data_store.data_sets[mode.name.lower()]
        data_manager = DataManager(self.data_store, data=data_set)
        greetings = TextSelectionFrame(self, frame, mode, data_manager)
        frame.add(greetings.main_frame, width=FRAME_WIDTH)

        mode = ChatMode.VALEDICTION
        data_set = self.data_store.data_sets[mode.name.lower()]
        data_manager = DataManager(self.data_store, data=data_set)
        valedictions = TextSelectionFrame(
            self, frame, mode, data_manager)
        frame.add(valedictions.main_frame, width=FRAME_WIDTH)

        chat_frame = ChatFrame(self, frame, ChatMode.CHAT)
        self.chat_panel = chat_frame.chat_frame
        frame.add(self.chat_panel, width=FRAME_WIDTH)

        return frame
