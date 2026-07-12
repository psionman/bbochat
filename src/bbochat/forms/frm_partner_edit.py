"""PartnerEditFrame for BBO Chat."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from psiutils.buttons import ButtonFrame
from psiutils.constants import PAD, PADB, PADR, Mode, Status
from psiutils.utilities import window_resize
from psiutils.widgets import clickable_widget

from bbochat.config import get_config
from bbochat.constants import ICON_FILE
from bbochat.data_store import Partner, data_store

FRAME_TITLE = "New partner"


class PartnerEditFrame:
    def __init__(self, parent: tk.Frame, mode: int, partner: Partner = None):
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.mode = mode
        self.partners = parent.partners
        self.greetings = data_store.greetings
        self.status = Status.NULL
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

        self.username.trace_add("write", self._value_changed)
        self.name.trace_add("write", self._value_changed)
        self.system.trace_add("write", self._value_changed)
        self.greeting.trace_add("write", self._value_changed)

        self._show()

        self.partner.notes = self.partner.notes.strip("\n")
        self.notes_text.insert("0.0", self.partner.notes)
        self.partner.notes = f"{self.partner.notes}\n"
        self._value_changed()

    def _show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(f"{self.mode.name.capitalize()} partner")
        root.iconphoto(False, tk.PhotoImage(file=ICON_FILE))
        root.wait_visibility()
        root.grab_set()
        root.transient(self.parent.root)
        root.bind("<Control-x>", self._dismiss)

        row = 0
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=row, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        row += 1
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=row, column=0, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)
        self.root.update_idletasks()
        root.bind("<Configure>", lambda e: window_resize(self, __file__))

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(5, weight=1)
        frame.columnconfigure(1, weight=1)
        state = "readonly" if self.mode == Mode.EDIT else "normal"

        label = ttk.Label(frame, text="Username")
        label.grid(row=0, column=0, sticky=tk.E, padx=PADR)

        entry = ttk.Entry(frame, textvariable=self.username, state=state)
        entry.grid(row=0, column=1, sticky=tk.EW, pady=PADB)
        entry.focus_set()

        label = ttk.Label(frame, text="Name")
        label.grid(row=1, column=0, sticky=tk.E, padx=PADR)

        entry = ttk.Entry(frame, textvariable=self.name)
        entry.grid(row=1, column=1, sticky=tk.EW, pady=PADB)
        if state == "readonly":
            entry.focus_set()

        label = ttk.Label(frame, text="System")
        label.grid(row=2, column=0, sticky=tk.E, padx=PADR)

        entry = ttk.Entry(frame, textvariable=self.system)
        entry.grid(row=2, column=1, sticky=tk.EW, pady=PADB)

        label = ttk.Label(frame, text="Greeting")
        label.grid(row=3, column=0, sticky=tk.E, padx=PADR)

        combobox = ttk.Combobox(
            frame,
            textvariable=self.greeting,
            values=self.greetings,
        )
        combobox.grid(row=3, column=1, sticky=tk.EW)
        clickable_widget(combobox)

        label = ttk.Label(frame, text="Notes")
        label.grid(row=4, column=0, sticky=tk.W)

        self.notes_text = tk.Text(frame, height=18)
        self.notes_text.grid(
            row=5, column=0, columnspan=2, sticky=tk.NSEW, pady=PAD
        )
        self.notes_text.bind("<<Modified>>", self._value_changed)

        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("save", self._save, True),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _value_changed(self, *args):  # *args essential here to make it work
        self.button_frame.disable()
        if not self.username.get():
            return
        if (
            self.mode == Mode.NEW
            or self.username.get() != self.partner.username
            or self.name.get() != self.partner.name
            or self.system.get() != self.partner.system
            or self.greeting.get() != self.partner.greeting
            or self.notes_text.get(0.0, tk.END) != self.partner.notes
        ):
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
        data_store.save()
        self.status = Status.OK
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
