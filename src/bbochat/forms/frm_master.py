"""Master tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD
from psiutils.widgets import ScrollingCanvas

from bbochat.config import config
from bbochat.constants import FRAME_WIDTH, ChatMode
from bbochat.data_store import data_store
from bbochat.forms.frm_chat import ChatFrame
from bbochat.forms.frm_opponents import OpponentsFrame
from bbochat.forms.frm_text_selection import TextSelectionFrame
from bbochat.message import message_store
from bbochat.mode_data import ModeData


class MasterFrame:
    def __init__(self, parent, master):
        self.root = parent.root
        message_store.subscribe(self._populate_history_frame)

        self.chat = data_store.chat
        self.radiobutton_styles = {}
        self.history_selection = tk.StringVar()

        self.master_frame = self._master_frame(master)

        if config.vertical_sashes:
            for index, sash in enumerate(config.vertical_sashes):
                self.master_frame.sash_place(index, sash[0], 0)

        if config.horizontal_sashes:
            for index, sash in enumerate(config.horizontal_sashes):
                self.chat_panel.sash_place(index, 0, sash[1])

        self._populate_history_frame()

    def _master_frame(self, master) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.HORIZONTAL)

        opponents_frame = OpponentsFrame(self, frame)
        self.opponents_frame = opponents_frame
        self.players_frame = opponents_frame.opponents_frame
        self.pair_tree = opponents_frame.pair_tree
        self.search_entry = opponents_frame.search_entry
        frame.add(self.players_frame, width=FRAME_WIDTH)

        history_panel = self._history_panel(frame)
        frame.add(history_panel, width=FRAME_WIDTH)

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

    def _history_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        row = 0
        label = ttk.Label(frame, text="History")
        label.grid(row=row, column=0, padx=PAD, pady=PAD)

        row += 1
        self.history_frame = ScrollingCanvas(
            frame,
            relief=tk.SUNKEN,
            borderwidth=2,
        )
        self.history_frame.grid(row=row, column=0, sticky=tk.NSEW)
        self._bind_mousewheel()
        return frame

    def _populate_history_frame(self) -> None:
        frame = self.history_frame.content
        for child in frame.winfo_children():
            child.destroy()

        for row, (text, mode) in enumerate(message_store.history.items()):
            style_name = self._radio_button_style(ChatMode(mode))
            button = ttk.Radiobutton(
                frame,
                text=text,
                variable=self.history_selection,
                value=text,
                style=style_name,
            )
            button.grid(row=row, column=0, padx=PAD, pady=2, sticky=tk.W)

    def _radio_button_style(self, mode: ChatMode) -> str:
        if mode in self.radiobutton_styles:
            return self.radiobutton_styles[mode]
        colour = config.colours[mode.name]
        style = ttk.Style()
        style_name = f"{colour.lstrip('#')}.TRadiobutton"
        style.configure(style_name, background=colour)
        self.radiobutton_styles[mode] = style_name
        return style_name

    def _bind_mousewheel(self) -> None:
        canvas = self.history_frame.canvas
        canvas.bind_all(
            "<Button-4>", lambda e: canvas.yview_scroll(-1, "units")
        )
        canvas.bind_all(
            "<Button-5>", lambda e: canvas.yview_scroll(1, "units")
        )

    def _unbind_mousewheel(self) -> None:
        canvas = self.history_frame.canvas
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
