"""Chat frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from constants import MODES, FRAME_WIDTH, MODES
from config import get_config
from data_manager import DataManager

from forms.frm_text_selection import TextSelectionFrame


class ChatFrame():
    def __init__(self, parent, master: ttk.Frame, mode: int) -> None:
        self.parent = parent
        self.root = parent.root
        self.config = get_config()
        self.data_store = parent.data_store
        self.config_key = f'last_{MODES[mode]}'

        self.chat_line = parent.chat_line
        self.chat_frame = self._main_frame(master)

    def _main_frame(self, master: ttk.Frame) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.VERTICAL,)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        mode = 'chat'
        data_manager = DataManager(self.data_store, None, True, False)
        chat_slave = TextSelectionFrame(
            self, frame, MODES[mode], data_manager, True, False)

        mode = 'chat'
        data_set = self.data_store.data_sets[mode]
        data_manager = DataManager(self.data_store, data_set, False, True)
        chat_master = TextSelectionFrame(
            self, frame, MODES[mode], data_manager, False, True, chat_slave)
        chat_slave.master_frame = chat_master

        frame.add(chat_master.main_frame, height=FRAME_WIDTH)
        frame.add(chat_slave.main_frame, height=FRAME_WIDTH)

        return frame
