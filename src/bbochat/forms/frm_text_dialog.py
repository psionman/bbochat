"""Text entry dialog."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button
from psiutils.utilities import window_resize

from constants import APP_TITLE
from config import get_config
import text


class TextDialogFrame():
    def __init__(self,
                 parent: tk.Frame,
                 title: str = 'Text dialog',
                 default: str = '') -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = get_config()
        self.title = title
        self.default = default
        self._text = default

        # tk variables
        self.text_value = tk.StringVar(value=default)
        self.text_value.trace_add('write', self._text_changed)

        self.show()

    def show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(f'{APP_TITLE} - {self.title}')
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.bind('<Control-x>', self.dismiss)

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
        # frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        label = ttk.Label(frame, text='Text')
        label.grid(row=0, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.text_value)
        entry.grid(row=0, column=1, sticky=tk.EW)
        entry.focus_set()
        entry.select_range(start=0, end='end')
        entry.icursor(len(self.default))

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            Button(
                frame,
                text=text.OK,
                command=self._process,
                underline=0,
                dimmable=True),
            Button(
                frame,
                text=text.EXIT,
                command=self.dismiss,
                sticky=tk.E,
                underline=1),
        ]
        frame.enable(False)
        return frame

    def _text_changed(self, *args) -> None:
        self.button_frame.disable()
        if self.text_value.get() != self.default:
            self.button_frame.enable()

    def _process(self, *args) -> None:
        self._text = self.text_value.get()
        self.dismiss()

    @property
    def text(self) -> str:
        return self._text

    def dismiss(self, *args) -> None:
        self.root.destroy()
