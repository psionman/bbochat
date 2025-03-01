"""Chat frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from constants import MODES, FRAME_WIDTH, MODE_TEXT
from config import get_config

from forms.frm_text_selection import TextSelectionFrame


class ChatFrame():
    def __init__(self, parent, master: ttk.Frame, mode: int) -> None:
        self.parent = parent
        self.root = parent.root
        self.config = get_config()
        self.data_store = parent.data_store
        self.mode_text = MODE_TEXT[mode]
        self.config_key = f'last_{self.mode_text}'

        self.chat_line = parent.chat_line
        self.chat_frame = self._main_frame(master)

    def _main_frame(self, master: ttk.Frame) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.VERTICAL,)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        mode = 'chat'
        chat_slave = TextSelectionFrame(self, frame, MODES[mode], [],
                                        True, False)

        data_set = self.data_store.data_sets[mode]
        text_list = data_set
        chat_master = TextSelectionFrame(self, frame, MODES[mode], text_list,
                                         False, True, data_set, chat_slave)
        chat_slave.master = chat_master

        frame.add(chat_master.main_frame, height=FRAME_WIDTH)
        frame.add(chat_slave.main_frame, height=FRAME_WIDTH)

        return frame
