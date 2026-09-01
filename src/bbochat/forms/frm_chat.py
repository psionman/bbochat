"""Chat frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from bbochat.constants import FRAME_WIDTH, ChatMode
from bbochat.data_store import data_store
from bbochat.forms.frm_text_selection import TextSelectionFrame
from bbochat.mode_data import ModeData


class ChatFrame:
    def __init__(self, parent, master: ttk.Frame, mode: int) -> None:
        self.root = parent.root
        self.config_key = f"last_{mode}"

        self.chat_line = parent.chat_line
        self.chat_frame = self._main_frame(master)

    def _main_frame(self, master: ttk.Frame) -> ttk.PanedWindow:
        frame = tk.PanedWindow(
            master,
            orient=tk.VERTICAL,
        )
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        chat_slave = self._get_chat_slave(frame, ChatMode.CHAT_DETAIL)
        chat_master = self._get_chat_master(frame, ChatMode.CHAT, chat_slave)
        chat_slave.master_frame = chat_master

        frame.add(chat_master.main_frame, height=FRAME_WIDTH)
        frame.add(chat_slave.main_frame, height=FRAME_WIDTH)

        return frame

    def _get_chat_slave(
        self, master: ttk.Frame, mode: str
    ) -> TextSelectionFrame:
        mode_data = ModeData(source_data=None, has_master=True, slave=False)

        return TextSelectionFrame(
            self,
            master,
            mode,
            mode_data,
            show_use_frame=True,
            show_title=False,
            slave=None,
        )

    def _get_chat_master(
        self, master: ttk.Frame, mode: ChatMode, chat_slave: TextSelectionFrame
    ) -> TextSelectionFrame:

        data_set = data_store.data_sets[mode.name.lower()]
        mode_data = ModeData(
            source_data=data_set,
            has_master=False,
            slave=True,
        )

        return TextSelectionFrame(
            self,
            master,
            mode,
            mode_data,
            show_use_frame=False,
            show_title=True,
            slave=chat_slave,
        )
