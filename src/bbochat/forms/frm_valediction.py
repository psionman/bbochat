"""Valediction frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.widgets import HAND
from psiutils.buttons import ButtonFrame, Button
from psiutils.menus import Menu, MenuItem

from constants import MODES
from config import get_config
import text

from forms.frm_edit import EditFrame


class ValedictionFrame():
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.parent = parent
        self.root = parent.root
        self.config = get_config()

        self.valediction = parent.valediction
        self.valedictions = parent.valedictions
        self.valedictions_list = tk.StringVar(
            value=[u'{unicodes_value}'.format(unicodes_value=item)
                   for item in parent.valedictions
                   if item and item[0] != '#'])

        self.valediction_frame = self._valediction_frame(master)
        self.context_menu = self._context_menu()

    def _valediction_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Valedictions')
        label.grid(row=0, column=0, pady=PAD)

        listbox = tk.Listbox(
            frame,
            listvariable=self.valedictions_list,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        listbox.grid(row=1, column=0, sticky=tk.NSEW)
        listbox.bind('<<ListboxSelect>>', self._valediction_selected)
        listbox.bind('<Button-3>', self._show_context_menu)

        label = ttk.Label(frame, text='Selected valediction')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.valediction)
        entry.grid(row=3, column=0, sticky=tk.EW)
        colour = self.config.colours['valediction']
        entry_style = ttk.Style()
        entry_style.configure(
            'valediction.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style='valediction.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        button_frame = ButtonFrame(frame, tk.HORIZONTAL)
        buttons = [
            Button(
                button_frame,
                text='Use',
                command=self._valediction,
                style='valediction.TButton'),
            Button(
                button_frame,
                text=text.EDIT,
                command=self._edit_valedictions,
                underline=0),
        ]

        button_frame.buttons = buttons
        button_frame.grid(row=4, column=0, pady=PAD)

        return frame

    def _valediction_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        self.valediction.set(self.valedictions[selection[0]])
        self.parent.mode = MODES['valediction']
        self.parent.parent.update_clipboard()

    def _edit_valedictions(self, *args) -> None:
        dlg = EditFrame(self, MODES['valediction'])
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            self.valedictions = dlg.data
            self.parent.valedictions = dlg.data
            self.parent.save()
            self.valedictions_list.set(dlg.data)

    def _valediction(self, *args) -> None:
        self.parent.parent.mode = MODES['valediction']
        self.parent.parent.update_clipboard()

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.EDIT, self._edit_valedictions),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
