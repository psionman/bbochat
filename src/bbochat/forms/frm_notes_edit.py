"""Notes Edit dialog for BBO Chat."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from psiutils.buttons import ButtonFrame
from psiutils.constants import PAD, Mode, Status
from psiutils.utilities import window_resize

from bbochat.config import get_config
from bbochat.constants import APP_TITLE
from bbochat.data_store import data_store


class NotesEditFrame:
    def __init__(self, parent: ttk.Frame, mode: int) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.mode = mode
        self.notes = parent.notes
        self.notes_text = ""

        self.config = get_config()
        self.title = f"{APP_TITLE} - {Mode[mode].name.capitalize()} notes"
        self.status = Status.UNDEFINED

        category = "" if mode == Mode.NEW else parent.category
        self.text = ""
        if category and category in parent.notes:
            self.text = parent.notes[category]

        # tk variables
        self.category_text = tk.StringVar(value=category)

        self.show()

    def show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(self.title)

        root.bind("<Control-x>", self._dismiss)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)
        self.root.update_idletasks()
        root.bind("<Configure>", lambda e: window_resize(self, __file__))

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text="Category")
        label.grid(row=0, column=0, sticky=tk.E)

        state = "readonly" if self.mode == Mode["edit"] else ""
        entry = ttk.Entry(frame, textvariable=self.category_text, state=state)
        entry.grid(row=0, column=1, sticky=tk.W, padx=PAD)
        entry.focus_set()

        self.notes_text = tk.Text(frame)
        self.notes_text.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.notes_text.insert("0.0", self.text)
        self.notes_text.bind("<KeyRelease>", self._text_changed)
        if state:
            self.notes_text.focus_set()

        return frame

    def _button_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("save", self._save, True),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _text_changed(self, *args):
        if self.notes_text.get(0.0, tk.END) != self.text:
            self.button_frame.enable()

    def _save(self, *args) -> None:
        text = self.notes_text.get(0.0, tk.END).strip("\n")
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")
        self.text = text.replace("\n", "\n\n")
        self.notes[self.category_text.get()] = self.text
        data_store.save()

        self.status = Status.UPDATED
        self.root.destroy()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
