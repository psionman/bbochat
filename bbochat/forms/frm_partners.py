"""Partners tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk, messagebox

from psiutils.constants import PAD, PADT, DIALOG_STATUS
from psiutils.widgets import HAND, PsiText, clickable_widget
from psiutils.buttons import ButtonFrame, Button, VERTICAL

from config import config, save_config
import text

from forms.frm_partner_edit import PartnerEditFrame


class PartnerFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root
        self.partner = parent.partner
        self.partners = parent.partners
        self.greetings = parent.greetings
        self.partners_names = self.parent.partners_names
        self.last_partner = config.last_partner
        self.greeting = parent.greeting

        # tk variables
        self.partners_list = parent.partners_list
        self.selected_partner = parent.selected_partner
        self.partners_name = parent.partners_name
        self.system = parent.system
        self.partners_username = parent.partners_username
        self.partners_names = parent.partners_names

        self.partners_frame = self._get_partners_frame(master)
        self.partners_frame.grid(row=0, column=0, sticky=tk.EW)
        self._update_partner_values()

        self.system.trace('w', self._partner_changed)
        self.partners_name.trace('w', self._partner_changed)
        self.notes_text.bind('<<TextModified>>', self._partner_changed)

    def _get_partners_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(3, weight=1)

        label = ttk.Label(frame, text='Partners')
        label.grid(row=0, column=0)

        self.listbox = tk.Listbox(
            frame,
            listvariable=self.partners_list,
            height=20,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.listbox.grid(row=1, column=0, rowspan=3,
                          sticky=tk.N, padx=PAD, pady=PAD)
        index = self.partners_names.index(config.last_partner)
        self.listbox.select_set(index)
        self.listbox.bind('<<ListboxSelect>>', self._partner_selected)

        label = ttk.Label(frame, text='Name')
        label.grid(row=0, column=1, sticky=tk.E, padx=PAD)

        entry = ttk.Entry(frame, width=30, textvariable=self.partners_name)
        entry.grid(row=0, column=2, sticky=tk.EW, pady=PADT)

        label = ttk.Label(frame, text='System')
        label.grid(row=1, column=1, sticky=tk.E, padx=PAD)

        entry = ttk.Entry(frame, width=80, textvariable=self.system)
        entry.grid(row=1, column=2, sticky=tk.EW, pady=PADT)

        label = ttk.Label(frame, text='Greeting')
        label.grid(row=2, column=1, sticky=tk.E, padx=PAD)

        combobox = ttk.Combobox(
            frame,
            textvariable=self.greeting,
            values=self.greetings,
            )
        combobox.grid(row=2, column=2, sticky=tk.EW, pady=PADT)
        clickable_widget(combobox)

        # label = ttk.Label(frame, text='Notes')
        # label.grid(row=2, column=1, padx=PAD, sticky=tk.W)

        self.notes_text = PsiText(frame, height=18)
        self.notes_text.grid(row=3, column=1, columnspan=4,
                             sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=0, column=5, rowspan=9,
                               sticky=tk.N, padx=PAD, pady=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        buttons = [
            Button(text.NEW, self._new, underline=0),
            Button(text.DELETE, self._delete, underline=0),
            Button(text.SAVE, self._save, underline=0, dimmable=False),
        ]
        frame = ButtonFrame(master, buttons, VERTICAL)
        frame.enable(False)
        return frame

    def _partner_selected(self, event: object = None) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        partners_names = sorted([username
                                 for username in self.partners.keys()])
        self.partner = self.partners[partners_names[selection[0]]]
        self._update_partner_values()
        config.config['last_partner'] = self.partner.username
        save_config(config)

    def _update_partner_values(self) -> None:
        self.partners_username.set(
                f'{self.partner.username}, {self.partner.name}'
            )
        self.greeting.set(self.partner.greeting)
        self.partners_name.set(self.partner.name)
        self.system.set(self.partner.system)
        self.notes_text.delete('0.0', tk.END)
        self.notes_text.insert('0.0', self.partner.notes)

    def _partner_changed(self, *args) -> None:
        self.button_frame.enable(False)
        notes = self.notes_text.get('0.0', tk.END)
        if (self.system.get() != self.partner.system
                or self.partners_name.get() != self.partner.system
                or notes != self.partner.notes):
            self.button_frame.enable()

    def _new(self, *args) -> None:
        dlg = PartnerEditFrame(self)
        self.root.wait_window(dlg.root)
        if dlg.status != DIALOG_STATUS['ok']:
            return
        self.partner = dlg.partner
        partners_names = sorted([username
                                 for username in self.partners.keys()])
        self.partners_list.set(partners_names)

        selection = self.listbox.curselection()
        self.listbox.select_clear(selection[0])
        index = partners_names.index(self.partner.username)
        self.listbox.select_set(index)
        self.listbox.event_generate("<<ListboxSelect>>")

    def _delete(self, *args) -> None:
        ...

    def _save(self, *args) -> None:
        self.partner.name = self.partners_name.get()
        self.partner.system = self.system.get()
        self.partner.greeting = self.greeting.get()
        self.partner.notes = self.notes_text.get(0.0, tk.END)
        self.partners[self.partner.name] = self.partner
        self.parent.save()
        messagebox.showinfo(
            '',
            'Partner saved',
            parent=self.parent.root,
        )
