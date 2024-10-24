"""Partners tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD
from psiutils.widgets import HAND, PsiText

from config import config


class PartnerFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.partner = parent.partner
        self.partners = parent.partners
        self.partners_names = self.parent.partners_names
        self.last_partner = config.last_partner

        # tk variables
        self.partners_list = parent.partners_list
        self.selected_partner = parent.selected_partner
        self.system = parent.system
        self.partners_username = parent.partners_username
        self.partners_names = parent.partners_names

        self.partners_frame = self._get_partners_frame(master)
        self.partners_frame.grid(row=0, column=0, sticky=tk.EW)
        self._update_partner_values()

        self.system.trace('w', self._system_changed)

    def _get_partners_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text='Partners')
        label.grid(row=0, column=0)

        listbox = tk.Listbox(
            frame,
            listvariable=self.partners_list,
            height=10,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        listbox.grid(row=1, column=0, rowspan=3,
                     sticky=tk.N, padx=PAD, pady=PAD)
        index = self.partners_names.index(config.last_partner)
        listbox.select_set(index)
        listbox.bind('<<ListboxSelect>>', self._partner_selected)

        label = ttk.Label(frame, text='System')
        label.grid(row=0, column=1, sticky=tk.W, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.system)
        entry.grid(row=1, column=1, sticky=tk.EW, padx=PAD)

        label = ttk.Label(frame, text='Notes')
        label.grid(row=2, column=1, padx=PAD)

        self.notes_text = PsiText(frame, height=18)
        self.notes_text.grid(row=3, column=1,
                             sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.notes_text.bind('<<TextModified>>', self._notes_changed)

        return frame

    def _partner_selected(self, event: object = None) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        self.partner = self.partners[self.partners_names[selection[0]]]
        self._update_partner_values()

    def _update_partner_values(self) -> None:
        self.partners_username.set(
                f'{self.partner.username}, {self.partner.name}'
            )
        self.system.set(self.partner.system)
        self.notes_text.delete('0.0', tk.END)
        self.notes_text.insert('0.0', self.partner.notes)

    def _system_changed(self, *args) -> None:
        if self.system.get() != self.partner.system:
            self.partner.system = self.system.get()
            self.parent.enable_buttons()

    def _notes_changed(self, event: object = None) -> None:
        if self.partner.username != self.last_partner:
            self.last_partner = self.partner.username
            return
        notes = self.notes_text.get('0.0', tk.END)
        if notes != self.partner.notes:
            # self.partner.notes = notes
            self.parent.enable_buttons()
