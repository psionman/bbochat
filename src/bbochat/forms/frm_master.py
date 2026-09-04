"""Master tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from bbochat.config import config
from bbochat.constants import FRAME_WIDTH, ChatMode
from bbochat.data_store import data_store
from bbochat.forms.frm_chat import ChatFrame
from bbochat.forms.frm_history import HistoryPanel
from bbochat.forms.frm_opponents import OpponentsFrame
from bbochat.forms.frm_text_selection import TextSelectionFrame
from bbochat.mode_data import ModeData


class MasterFrame:
    def __init__(self, parent, master: ttk.Notebook):
        self.root = parent.root
        self.chat = data_store.chat

        self.master_frame = self._master_frame(master)

        if config.vertical_sashes:
            for index, sash in enumerate(config.vertical_sashes):
                self.master_frame.sash_place(index, sash[0], 0)

        if config.horizontal_sashes:
            for index, sash in enumerate(config.horizontal_sashes):
                self.chat_panel.sash_place(index, 0, sash[1])

    def _master_frame(self, master) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.HORIZONTAL)

        opponents_frame = OpponentsFrame(self, frame)
        self.opponents_frame = opponents_frame
        self.players_frame = opponents_frame.opponents_frame
        self.pair_tree = opponents_frame.pair_tree
        self.search_entry = opponents_frame.search_entry
        frame.add(self.players_frame, width=FRAME_WIDTH)

        history_panel = HistoryPanel(self, frame)
        frame.add(history_panel.main_frame, width=FRAME_WIDTH)

        mode = ChatMode.GREETINGS
        data_set = data_store.data_sets[mode.name.lower()]
        mode_data = ModeData(source_data=data_set)
        greetings = TextSelectionFrame(self, frame, mode, mode_data)
        frame.add(greetings.main_frame, width=FRAME_WIDTH)

        mode = ChatMode.VALEDICTION
        data_set = data_store.data_sets["valedictions"]
        mode_data = ModeData(source_data=data_set)
        valedictions = TextSelectionFrame(self, frame, mode, mode_data)
        frame.add(valedictions.main_frame, width=FRAME_WIDTH)

        chat_frame = ChatFrame(self, frame, ChatMode.CHAT)
        self.chat_panel = chat_frame.chat_frame
        frame.add(self.chat_panel, width=FRAME_WIDTH)

        return frame
