"""Text Selection frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk, messagebox

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.widgets import HAND
from psiutils.buttons import ButtonFrame, Button
from psiutils.menus import Menu, MenuItem

from constants import MODES, MODE_TEXT
from config import get_config
from utilities import build_text_list
import text

from forms.frm_edit import EditFrame
from forms.frm_text_dialog import TextDialogFrame


class TextSelectionFrame():
    def __init__(self, parent: tk.Frame, master: tk.Frame, mode: int) -> None:
        self.parent = parent
        self.root = self.parent.root
        self.data_store = self.parent.data_store

        self.mode = mode
        self.mode_text = MODE_TEXT[mode]

        self.config_key = f'last_{self.mode_text}'
        self.config = get_config()
        self.text_var = tk.StringVar(value=self.config.config[self.config_key])

        self.parent_text_list = self.data_store.data_sets[MODES[self.mode]]

        # self.text_list is a cleaned version of the list in data store
        self.text_list = build_text_list(self.parent_text_list)

        # self.selected_text contains the text selected from the listbox
        self.selected_text = ''

        self.main_frame = self._main_frame(master)
        self.context_menu = self._context_menu()

        self._populate_text_items()

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text=f'{self.mode_text.capitalize()}s')
        label.grid(row=0, column=0, pady=PAD)

        self.listbox = tk.Listbox(
            frame,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.listbox .grid(row=1, column=0, sticky=tk.NSEW)
        self.listbox .bind('<<ListboxSelect>>', self._item_selected)
        self.listbox .bind('<Button-3>', self._show_context_menu)

        label = ttk.Label(frame, text=f'Selected {self.mode_text}')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.text_var)
        entry.grid(row=3, column=0, sticky=tk.EW)
        colour = self.config.colours[self.mode_text]
        entry_style = ttk.Style()
        entry_style.configure(
            f'{self.mode_text}.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style=f'{self.mode_text}.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        button_frame = ButtonFrame(frame, tk.HORIZONTAL)
        buttons = [
            Button(
                button_frame,
                text='Use',
                command=self._use_item,
                style=f'{self.mode_text}.TButton'),
            Button(
                button_frame,
                text=text.EDIT,
                command=self._edit_all,
                underline=0),
        ]

        button_frame.buttons = buttons
        button_frame.grid(row=4, column=0, pady=PAD)

        return frame

    def _item_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return

        self.selected_text = self.text_list[selection[0]]
        self.text_var.set(self.selected_text)
        self._use_item()
        self.context_menu.enable()

    def _new_item(self, *args) -> None:
        dlg = TextDialogFrame(self, 'New')
        self.root.wait_window(dlg.root)
        if not dlg.text:
            return

        self.text_list.append(dlg.text)
        self.parent_text_list.append(dlg.text)
        self.text_var.set(dlg.text)
        self._use_item()
        self._populate_text_items(dlg.text)
        self._save()

    def _edit_item(self, *args) -> None:
        dlg = TextDialogFrame(self, 'Edit', self.selected_text)
        self.root.wait_window(dlg.root)
        if dlg.status != DIALOG_STATUS['updated']:
            return

        index = self.text_list.index(self.selected_text)
        self._update_text_list(self.text_list, dlg.text, index)
        self._update_text_list(self.parent_text_list, dlg.text, index)

        self._populate_text_items(dlg.text)

        self.selected_text = dlg.text
        self.text_var.set(dlg.text)
        self._use_item()
        self._save()

    def _delete_item(self, *args) -> None:
        if not messagebox.askyesno('Delete item', text.DELETE_ITEM):
            return

        self.text_list.remove(self.selected_text)
        self.parent_text_list.remove(self.selected_text)
        self.text_var.set('')
        self._use_item()
        self._populate_text_items()
        self._save()

    def _edit_all(self, *args) -> None:
        dlg = EditFrame(self, self.mode, self.selected_text)
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            index = self.text_list.index(self.selected_text)
            self._update_text_list(self.text_list, dlg.text, index)
            self._update_text_list(self.parent_text_list, dlg.text, index)

            self._populate_text_items(dlg.selected_text)
            self.selected_text = dlg.selected_text
            self.text_var.set(dlg.selected_text)
            self._use_item()

    def _update_text_list(
            self, text_list: list[str], text: str, index: int) -> None:
        text_list.remove(self.selected_text)
        text_list.insert(index, text)

    def _use_item(self, *args) -> None:
        self.parent.parent.update_clipboard(self.text_var.get(), self.mode)
        self.config = get_config()
        self.config.update(self.config_key, self.text_var.get())
        self.config.save()

    def _populate_text_items(self, selected_item: str = '') -> None:
        self.listbox.delete(0, tk.END)
        for index, item in enumerate(self.text_list):
            self.listbox.insert('end', item)
            if selected_item and item == selected_item:
                self.listbox.selection_set(index)

    def _save(self, *args) -> None:
        self.data_store.data_sets[MODES[self.mode]] = self.text_list
        self.data_store.save()

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.NEW, self._new_item, dimmable=False),
            MenuItem(text.EDIT, self._edit_item, dimmable=True),
            MenuItem(text.DELETE, self._delete_item, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
