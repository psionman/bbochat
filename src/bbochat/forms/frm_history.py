# forms/frm_history.py

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD
from psiutils.widgets import ScrollingCanvas

from bbochat.config import config
from bbochat.constants import ChatMode
from bbochat.message import message_store


class HistoryPanel:
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.root = parent.root
        message_store.subscribe(self._populate_history_frame)
        self.radiobutton_styles = {}

        # tk variables
        self.history_selection = tk.StringVar()

        self.main_frame = self._history_panel(master)
        self._populate_history_frame()

        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

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
        style = ttk.Style(self.root)
        style_name = f"{colour.lstrip('#')}.TRadiobutton"
        style.configure(style_name, background=colour)
        self.radiobutton_styles[mode] = style_name
        return style_name

    def _on_mousewheel(self, event) -> None:
        canvas = self.history_frame.canvas
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return
        # only scroll if pointer is over this panel's canvas or its children
        w = widget
        while w is not None:
            if w == canvas or w == self.history_frame.content:
                canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
                return
            w = w.master
