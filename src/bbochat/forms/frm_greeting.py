"""Greeting frame for BBO Chat."""

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


class GreetingFrame():
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.parent = parent
        self.root = parent.root
        self.config = get_config()

        self.greeting = parent.greeting
        self.greetings = parent.greetings
        self.greetings_list = parent.greetings_list

        self.greeting_frame = self._greeting_frame(master)
        self.context_menu = self._context_menu()

    def _greeting_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Greetings')
        label.grid(row=0, column=0, padx=PAD, pady=PAD)

        self.greetings_listbox = tk.Listbox(
            frame,
            listvariable=self.greetings_list,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.greetings_listbox.grid(row=1, column=0, sticky=tk.NSEW)
        self.greetings_listbox.bind('<<ListboxSelect>>',
                                    self._greeting_selected)
        self.greetings_listbox.bind('<Button-3>', self._show_context_menu)

        label = ttk.Label(frame, text='Selected greeting')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.greeting)
        entry.grid(row=3, column=0, sticky=tk.EW)
        colour = self.config.colours['greeting']
        entry_style = ttk.Style()
        entry_style.configure(
            'greeting.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style='greeting.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        button_frame = ButtonFrame(frame, tk.HORIZONTAL)
        buttons = [
            Button(
                button_frame,
                text='Use',
                command=self._greeting,
                style='greeting.TButton'),
            Button(
                button_frame,
                text=text.EDIT,
                command=self._edit_greetings,
                underline=0),
        ]

        button_frame.buttons = buttons
        button_frame.grid(row=99, column=0, pady=PAD)

        return frame

    def _greeting_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        self.greeting.set(self.greetings[selection[0]])
        self.parent.mode = MODES['greeting']
        self.parent.parent.update_clipboard()
        self._greeting()

    def _edit_greetings(self, *args) -> None:
        dlg = EditFrame(self, MODES['greeting'])
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            self.greetings = dlg.data
            self.parent.greetings = dlg.data
            self.parent.save()
            self.greetings_list.set(dlg.data)

    def _greeting(self, *args) -> None:
        self.parent.parent.mode = MODES['greeting']
        self.parent.parent.update_clipboard()

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.EDIT, self._edit_greetings),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
