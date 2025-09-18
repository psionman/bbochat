
"""PartnerEditFrame for BBO Chat."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from psiutils.constants import PAD, PADR, PADB, DIALOG_STATUS, MODES
from psiutils.buttons import ButtonFrame
from psiutils.widgets import clickable_widget
from psiutils.utilities import window_resize

from bbochat.data import Partner
from bbochat.constants import ICON_FILE
from bbochat.config import get_config

FRAME_TITLE = 'New partner'


class PartnerEditFrame():
    def __init__(self, parent: tk.Frame, mode: int, partner: Partner = None):
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.mode = mode
        self.data_store = parent.data_store
        self.data_store.read()
        self.partners = parent.partners
        self.greetings = self.data_store.greetings
        self.status = DIALOG_STATUS['null']
        self.config = get_config()

        self.notes_text = None

        if not partner:
            partner = Partner()
            if self.greetings:
                partner.greeting = self.greetings[0]
        self.partner = partner

        # tk variables
        self.username = tk.StringVar(value=self.partner.username)
        self.name = tk.StringVar(value=self.partner.name)
        self.system = tk.StringVar(value=self.partner.system)
        self.greeting = tk.StringVar(value=self.partner.greeting)

        self.username.trace_add('write', self._value_changed)
        self.name.trace_add('write', self._value_changed)
        self.system.trace_add('write', self._value_changed)
        self.greeting.trace_add('write', self._value_changed)

        self._show()

        self.partner.notes = self.partner.notes.strip('\n')
        self.notes_text.insert('0.0', self.partner.notes)
        self.partner.notes = f'{self.partner.notes}\n'
        self._value_changed()

    def _show(self) -> None:
        # pylint: disable=no-member)
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(f'{MODES[self.mode].capitalize()} partner')
        root.iconphoto(False, tk.PhotoImage(file=ICON_FILE))
        root.wait_visibility()
        root.grab_set()
        root.transient(self.parent.root)
        root.bind('<Control-x>', self._dismiss)
        root.bind('<Configure>',
                  lambda e: window_resize(self, __file__))

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
        frame.rowconfigure(5, weight=1)
        frame.columnconfigure(1, weight=1)
        state = 'readonly' if self.mode == MODES['edit'] else 'normal'

        label = ttk.Label(frame, text='Username')
        label.grid(row=0, column=0, sticky=tk.E, padx=PADR)

        entry = ttk.Entry(frame, textvariable=self.username, state=state)
        entry.grid(row=0, column=1, sticky=tk.EW, pady=PADB)
        entry.focus_set()

        label = ttk.Label(frame, text='Name')
        label.grid(row=1, column=0, sticky=tk.E, padx=PADR)

        entry = ttk.Entry(frame, textvariable=self.name)
        entry.grid(row=1, column=1, sticky=tk.EW, pady=PADB)
        if state == 'readonly':
            entry.focus_set()

        label = ttk.Label(frame, text='System')
        label.grid(row=2, column=0, sticky=tk.E, padx=PADR)

        entry = ttk.Entry(frame, textvariable=self.system)
        entry.grid(row=2, column=1, sticky=tk.EW, pady=PADB)

        label = ttk.Label(frame, text='Greeting')
        label.grid(row=3, column=0, sticky=tk.E, padx=PADR)

        combobox = ttk.Combobox(
            frame,
            textvariable=self.greeting,
            values=self.greetings,
            )
        combobox.grid(row=3, column=1, sticky=tk.EW)
        clickable_widget(combobox)

        label = ttk.Label(frame, text='Notes')
        label.grid(row=4, column=0, sticky=tk.W)

        self.notes_text = tk.Text(frame, height=18)
        self.notes_text.grid(row=5, column=0, columnspan=2,
                             sticky=tk.NSEW, pady=PAD)
        self.notes_text.bind('<<Modified>>', self._value_changed)

        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('save', self._save, True),
            frame.icon_button('exit', self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _value_changed(self, *args):  # *args essential here to make it work
        self.button_frame.disable()
        if not self.username.get():
            return
        if (self.mode == MODES['new']
                or self.username.get() != self.partner.username
                or self.name.get() != self.partner.name
                or self.system.get() != self.partner.system
                or self.greeting.get() != self.partner.greeting
                or self.notes_text.get(0.0, tk.END) != self.partner.notes):
            self.button_frame.enable()
        self.notes_text.edit_modified(False)

    def _save(self, *args) -> None:
        self.partner = Partner()
        self.partner.username = self.username.get()
        self.partner.name = self.name.get()
        self.partner.system = self.system.get()
        self.partner.greeting = self.greeting.get()
        self.partner.notes = self.notes_text.get(0.0, tk.END)
        self.partners[self.partner.username] = self.partner
        self.parent.parent.save()
        self.status = DIALOG_STATUS['ok']
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
