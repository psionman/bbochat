"""Text entry dialog."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import emoji

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.buttons import ButtonFrame, Button
from psiutils.utilities import window_resize
from psiutils.widgets import Tooltip

from bbochat.constants import APP_TITLE
from bbochat.config import get_config
import bbochat.text as txt


class TextDialogFrame():
    def __init__(self,
                 parent: ttk.Frame,
                 title: str = 'Text dialog',
                 default: str = '') -> None:
        self.root = tk.Toplevel(parent.root)

        self.parent = parent
        self.config = get_config()
        self.title = title
        self.default = default
        self.text_ = default
        self.hidden = False

        self.entry = None

        self.status = DIALOG_STATUS['null']

        # tk variables
        self.text_value = tk.StringVar(value=default)
        tooltip = txt.TOOLTIP if self.config.show_tooltips else ''
        self.tooltip_text = tk.StringVar(value=tooltip)
        self.hidden_item = tk.BooleanVar()
        self._hidden_item()

        self.text_value.trace_add('write', self._text_changed)
        self.hidden_item.trace_add('write', self._text_changed)

        self._show()

    def _show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(f'{APP_TITLE} - {self.title}')
        root.bind('<Configure>',
                  lambda e: window_resize(self, __file__))

        root.bind('<Control-x>', self._dismiss)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text='Text')
        label.grid(row=0, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        self.entry = self._get_entry(frame)
        self.entry.grid(row=0, column=1, sticky=tk.EW)

        check_button = ttk.Checkbutton(frame, text='Hidden item',
                                       variable=self.hidden_item)
        check_button.grid(row=1, column=1, sticky=tk.W)

        return frame

    def _button_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            Button(
                frame,
                text=txt.OK,
                command=self._process,
                underline=0,
                dimmable=True),
            Button(
                frame,
                text=txt.CANCEL,
                command=self._dismiss,
                sticky=tk.E,),
        ]
        frame.enable(False)
        return frame

    def _get_entry(self, master: ttk.Frame) -> ttk.Entry:
        entry = ttk.Entry(master, textvariable=self.text_value)
        entry.select_range(start=0, end='end')
        entry.icursor(len(self.default))
        entry.focus_set()
        entry.bind('<KeyRelease>', self._text_key_release)

        entry.tooltip = Tooltip(
            entry,
            textvariable=self.tooltip_text,
            wrap_length=2000,
            vertical_offset=17)
        entry.bind('<Enter>', entry.tooltip.onEnter)
        entry.bind('<Leave>', entry.tooltip.onLeave)
        return entry

    def _text_changed(self, *args) -> None:
        self.button_frame.disable()
        text = self.text_value.get()
        if text != self.default or self.hidden_item.get() != self.hidden:
            self.button_frame.enable()
        # self.hidden_item.set(False)

    def _hidden_item(self) -> None:
        text = self.text_value.get()
        if text and text[0] == '#':
            self.hidden_item.set(True)
            text = text[1:].strip()
            self.text_value.set(text)
            self.hidden = True

    def _text_key_release(self, *args) -> None:
        text = self.text_value.get()
        list_ = [emoji.demojize(char_) for char_ in text]
        self.text_value.set(''.join(list_))
        # self.entry.icursor(len(self.text_value.get()))

    def _process(self, *args) -> None:
        self.text_ = self.text_value.get()
        if self.hidden_item .get():
            self.text_ = f'# {self.text_}'
        self.status = DIALOG_STATUS['updated']
        self._dismiss()

    @property
    def text(self) -> str:
        return self.text_

    def _dismiss(self, *args) -> None:
        self.root.destroy()
