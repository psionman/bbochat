"""Notes tab for BBO Chat notebook"""


import contextlib
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from pathlib import Path

from psiutils.constants import PAD
from psiutils.widgets import PsiText
from psiutils.buttons import Button
from psiutils.utilities import create_directories

from config import config
import text
from constants import TXT_FILE_TYPES
from data import Partner


class NotesFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root
        self.partner = parent.partner

        # Tk variables
        self.path = tk.StringVar(value='')

        self.notes_frame = self._get_notes_frame(master)
        self._get_partners_notes()

    def _get_notes_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.notes_text = PsiText(frame, height=18)
        self.notes_text.grid(row=0, column=0, columnspan=4,
                             sticky=tk.NSEW, padx=PAD, pady=PAD)

        label = ttk.Label(frame, text='Path')
        label.grid(row=1, column=0, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.path)
        entry.grid(row=1, column=1, sticky=tk.EW)

        button = ttk.Button(frame, text=text.ELLIPSIS, command=self._get_path)
        button.grid(row=1, column=2)

        self.save_button = Button(
                frame,
                text=text.SAVE,
                command=self._save,
                dimmable=True)
        self.save_button.grid(row=2, column=2, padx=PAD, pady=PAD)

        return frame

    def _save(self, *args) -> None:
        notes = self.notes_text.get('1.0', tk.END)
        create_directories(Path(self.path.get()).parent)
        with open(self.path.get(), 'w') as f_notes:
            f_notes.write(notes)
        self.save_button.enable(False)

    def _get_path(self, *args) -> None:
        file_path = Path(self.path.get())
        path = filedialog.askopenfilename(
            initialdir=file_path.parent,
            initialfile=file_path,
            parent=self.root,
            filetypes=TXT_FILE_TYPES,
        )
        if path:
            self.path.set(path)
            self._notes_contents()

    def _get_partners_notes(self, *args) -> None:
        date = datetime.now().strftime('%Y%m%d')
        file_name = f'{self.partner.username}_{date}.txt'
        path = str(Path(config.notes_path, file_name))
        self.path.set(value=path)
        self._notes_contents()

    def _notes_contents(self) -> str:
        self.notes_text.delete('1.0', tk.END)
        with contextlib.suppress(FileNotFoundError):
            with open(self.path.get(), 'r') as f_notes:
                notes = f_notes.read()
                self.notes_text.insert('1.0', notes)

    def change_partner(self, partner: Partner) -> None:
        self.partner = partner
        self._get_partners_notes()
