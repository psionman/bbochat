"""Notes tab for BBO Chat notebook"""

import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from pathlib import Path

from psiutils.constants import PAD
from psiutils.widgets import PsiText
from psiutils.buttons import ButtonFrame, Button, HORIZONTAL
from psiutils.utilities import create_directories

from config import config
import text


class NotesFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root
        self.partner = parent.partner

        # Tk variables
        self.path = tk.StringVar(value='')

        self.path.trace_add('write', self._data_changed)

        self.notes_frame = self._get_notes_frame(master)
        self.root.bind("<FocusIn>", self._load)

    def _get_notes_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.notes_text = PsiText(frame, height=18)
        self.notes_text.grid(row=0, column=0, columnspan=4,
                             sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.notes_text.bind('<<TextModified>>', self._data_changed)

        label = ttk.Label(frame, text='Path')
        label.grid(row=1, column=0, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.path)
        entry.grid(row=1, column=1, sticky=tk.EW)

        button = ttk.Button(frame, text=text.ELLIPSIS, command=self._get_path)
        button.grid(row=1, column=2)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=2, column=2,
                               sticky=tk.E, padx=PAD, pady=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        buttons = [
            Button(text.SAVE, self._save, dimmable=True),
        ]
        frame = ButtonFrame(master, buttons, HORIZONTAL)
        frame.enable(False)
        return frame

    def _notes_contents(self) -> str:
        self.notes_text.delete('0.0', tk.END)
        try:
            with open(self.path.get(), 'r') as f_notes:
                notes = f_notes.read()
                self.notes_text.insert('0.0', notes)
        except FileNotFoundError:
            pass

    def _save(self, *args) -> None:
        notes = self.notes_text.get('0.0', tk.END)
        create_directories(Path(self.path.get()).parent)

        with open(self.path.get(), 'w') as f_notes:
            f_notes.write(notes)
        self.button_frame.enable(False)

    def _get_path(self, *args) -> None:
        path = filedialog.askopenfilename(
            initialfile= self.path,
            parent=self.root,
        )
        self.path.set(path)

    def _data_changed(self, *args):  # *args essential here to make it work
        enable = False
        notes = self.notes_text.get('0.0', tk.END)
        if notes == '\n':
            notes = ''
        if self.path.get() and notes:
            enable = True
        self.button_frame.enable(enable)

    def _load(self, *args) -> None:
        self.partner = self.parent.partner
        date = datetime.now().strftime('%Y%m%d')
        file_name = f'{self.partner.username}_{date}.txt'
        path = str(Path(config.notes_path, file_name))
        self.path.set(value=path)
        self._notes_contents()
