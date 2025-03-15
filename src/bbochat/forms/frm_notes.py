"""Notes tab for BBO Chat notebook"""


import contextlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path
import json
import pypandoc

from psiutils.constants import PAD
from psiutils.widgets import PsiText
from psiutils.buttons import Button, ButtonFrame

from config import get_config
import text
from constants import TXT_FILE_TYPES, DOCS_DIR, APP_NAME, YYYYMMDD, FRAME_WIDTH
from data import Partner


class NotesFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root
        self.partner = parent.partner
        self.config = get_config()

        # Tk variables
        path = Path(DOCS_DIR, APP_NAME)
        if self.partner:
            path = Path(DOCS_DIR, APP_NAME, self.partner.username)
        date = datetime.now().strftime(YYYYMMDD)
        path = Path(path, f'{date}.txt')

        self.path = tk.StringVar()
        self.set_path()

        self.notes_frame = self._get_notes_frame(master)

        if self.config.notes_sashes:
            for index, sash in enumerate(self.config.notes_sashes):
                self.notes_panel.sash_place(index, sash[0], 0)

        self.change_partner(self.partner)

    def set_path(self) -> None:
        path = Path(DOCS_DIR, APP_NAME)
        if self.partner:
            path = Path(DOCS_DIR, APP_NAME, self.partner.username)
        date = datetime.now().strftime(YYYYMMDD)
        path = Path(path, f'{date}.txt')
        self.path.set(path)

    def _get_notes_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.notes_panel = self._notes_panel(frame)
        self.notes_panel.grid(row=0, column=0, columnspan=4,
                              sticky=tk.NSEW, padx=PAD, pady=PAD)

        label = ttk.Label(frame, text='Path')
        label.grid(row=1, column=0, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.path)
        entry.grid(row=1, column=1, sticky=tk.EW)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=2, column=1, sticky=tk.W, pady=PAD)
        return frame

    def _button_frame(self, master: ttk.Frame) -> ttk.Frame:
        button_frame = ButtonFrame(master, tk.HORIZONTAL)
        button_frame.buttons = [
            Button(button_frame, text=text.OPEN, command=self._open_file),
            Button(
                button_frame,
                text=text.SAVE,
                command=self._save,
                dimmable=True),
            Button(
                button_frame,
                text=text.REPORT,
                command=self._report,
                dimmable=True),
            ]
        button_frame.disable()
        return button_frame

    def _notes_panel(self, master: ttk.Frame) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.HORIZONTAL,)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        board_frame = self._board_frame(frame)
        board_frame.grid(row=0, column=0, sticky=tk.NSEW)

        general_frame = self._general_frame(frame)
        general_frame.grid(row=0, column=0, sticky=tk.NSEW)

        frame.add(board_frame, width=FRAME_WIDTH)
        frame.add(general_frame, width=FRAME_WIDTH)

        return frame

    def _board_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Board notes')
        label.grid(row=0, column=0)

        self.board_notes = PsiText(frame, height=18)
        self.board_notes.grid(row=1, column=0,
                              sticky=tk.NSEW)
        self.board_notes.bind('<KeyRelease>', self._value_changed)

        return frame

    def _general_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='General notes')
        label.grid(row=0, column=0)

        self.general_notes = PsiText(frame, height=18)
        self.general_notes.grid(row=1, column=0,
                                sticky=tk.NSEW)
        self.general_notes.bind('<KeyRelease>', self._value_changed)
        return frame

    def change_partner(self, partner: Partner) -> None:
        self.partner = partner
        self.set_path()
        self._notes_contents()
        self._value_changed()

    def _save(self, *args) -> None:
        board_notes = self. board_notes.get('1.0', tk.END)
        general_notes = self.general_notes.get('1.0', tk.END)
        notes = {
            'board_notes': board_notes.strip('\n'),
            'general_notes': general_notes.strip('\n'),
        }

        path = Path(self.path.get())
        Path(path.parent).mkdir(parents=True, exist_ok=True)
        f_notes = filedialog.asksaveasfile(
            initialfile=path,
            mode='w',
            defaultextension=".txt")
        if f_notes is None:
            return

        # with open(self.path.get(), 'w') as f_notes:
        #     f_notes.write(notes)

        json_path = self.path.get().replace('txt', 'json')
        with open(json_path, 'w') as f_notes:
            json.dump(notes, f_notes)

        self.button_frame.enable(False)

    def _open_file(self, *args) -> None:
        path = Path(self.path.get()).parent
        while not path.is_dir():
            path = Path(self.path.get()).parent.parent

        if path := filedialog.askopenfilename(
            initialdir=path,
            initialfile=self.path.get(),
            parent=self.root,
            filetypes=TXT_FILE_TYPES,
        ):
            if Path(path).suffix != '.txt':
                messagebox.showerror(
                    'Open file',
                    'Notes file must be a ".txt" file.',
                    parent=self.root,)
                return
            self.path.set(path)
            self._notes_contents()

    def _get_notes_and_display(self) -> None:
        json_path = Path(self.path.get().replace('txt', 'json'))
        if not json_path.is_file():
            return

    def _notes_contents(self) -> str:
        self.general_notes.delete('0.0', tk.END)
        self.board_notes.delete('0.0', tk.END)
        with contextlib.suppress(FileNotFoundError):
            json_path = self.path.get().replace('txt', 'json')
            with open(json_path, 'r') as f_notes:
                notes = json.load(f_notes)
            self.board_notes.insert('1.0', notes['board_notes'])
            self.general_notes.insert('1.0', notes['general_notes'])

    def _report(self, *args) -> None:
        output = pypandoc.convert_file(
            'input.md', 'pdf', outputfile='output.pdf')

    def _value_changed(self, *args):  # *args essential here to make it work
        board_notes = self. board_notes.get('1.0', tk.END)
        general_notes = self.general_notes.get('1.0', tk.END)
        self.button_frame.disable()
        if f'{board_notes}{general_notes}'.replace('\n', ''):
            self.button_frame.enable()
