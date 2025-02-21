
"""EditFrame for BBO Chat."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.buttons import ButtonFrame, Button
from psiutils.utilities import window_resize

from constants import MODES
from config import get_config
import text

FRAME_TITLE = 'Edit'


class EditFrame():
    def __init__(self, parent, mode, data):
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = get_config()
        self.mode = mode

        self.data_text = '\n'.join(data)
        self.data = ''
        self.status = DIALOG_STATUS['null']

        # tk variables

        self.show()

    def show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(f'{FRAME_TITLE} - {MODES[self.mode]}')
        root.transient(self.parent.root)

        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-s>', self._save)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.text = tk.Text(frame)
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.text.insert('0.0', self.data_text)
        self.text.focus_set()

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        buttons = [
            Button(
                frame,
                text=text.SAVE,
                command=self._save,
                underline=0),
            Button(
                frame,
                text=text.EXIT,
                command=self.dismiss,
                sticky=tk.E,
                underline=1),
        ]
        frame.buttons = buttons
        frame.enable(False)
        return frame

    def _save(self, *args) -> None:
        self.status = DIALOG_STATUS['updated']
        self.data = self.text.get('0.0', tk.END).split('\n')
        self.dismiss()

    def dismiss(self, *args) -> None:
        self.root.destroy()
