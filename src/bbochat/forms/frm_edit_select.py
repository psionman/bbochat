"""Text Edit Frame for BBO Chat."""

import tkinter as tk
import uuid
from pathlib import Path
from tkinter import ttk

from bidict import bidict
from psiutils import messagebox
from psiutils.buttons import IconButton
from psiutils.constants import PAD, Status
from psiutils.menus import Menu, MenuItem
from psiutils.utilities import window_resize
from psiutils.widgets import HAND

from bbochat.buttons import ButtonFrame
from bbochat.forms.frm_text_dialog import TextDialogFrame
from bbochat.state import state
from bbochat.text import Text

txt = Text()

FRAME_TITLE = "Edit"


class EditSelectFrame:
    def __init__(self, parent) -> None:
        self.root = tk.Toplevel(parent.root)
        self.mode_data = parent.mode_data

        self.mode = parent.mode

        self.save_button = None
        self.listbox = None
        self.button_frame = None

        # self.master_selected_text is the value of the text selected
        # in the calling function
        self.master_selected_text = parent.selected_text

        self.status = Status.NULL

        # Original text in data store - used to check change
        self.original_data = [
            item for item in self.mode_data.display_list_raw if item
        ]

        # Current text in frame
        self.display_list = [
            item for item in self.mode_data.display_list_raw if item
        ]

        self.changes = {item: (item, item) for item in self.display_list}

        # text_register is a dict of text items (a list) keyed on uuids
        # key_register is a  bidict of uuids and
        # the keys (text) to the text items list
        self.text_register = {}
        self.key_register = bidict()

        if self.mode_data.text_register:
            self.text_register = self.mode_data.text_register
            self.key_register = self.mode_data.key_register

        # self.selected_item is the index of the item selected in the listbox
        self.selected_item = None

        # self.selected_text contains the text selected from the listbox
        self.selected_text = ""

        self._show()
        self.context_menu = self._context_menu()
        self.button_frame.disable()
        self._populate_text_items()

    def _show(self) -> None:
        root = self.root
        root.geometry(state.geometry[Path(__file__).stem])
        root.title(FRAME_TITLE)

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-s>", self._save_data)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

        self.root.update_idletasks()
        root.bind(
            "<Configure>", lambda e: window_resize(root, __file__, state)
        )

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(frame, cursor=HAND)
        self.listbox.grid(row=0, column=0, rowspan=6, sticky=tk.NSEW, padx=PAD)
        self.listbox.bind("<<ListboxSelect>>", self._select_item)
        self.listbox.bind("<Button-3>", self._show_context_menu)

        scroll_buttons = self._scroll_buttons(frame)
        scroll_buttons.grid(row=0, column=1, sticky=tk.NS)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=0, column=2, sticky=tk.NS, padx=PAD)

        return frame

    def _scroll_buttons(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button = ttk.Button(
            frame, text=txt.CHEVRON_UP, command=self._move_up, width=1
        )
        button.grid(row=0, column=0, sticky=tk.NS)

        button = ttk.Button(
            frame, text=txt.CHEVRON_DOWN, command=self._move_down, width=1
        )
        button.grid(row=1, column=0, sticky=tk.NS)
        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.VERTICAL)
        self.save_button = IconButton(
            frame, txt.SAVE, "save", self._save_data, True
        )
        frame.buttons = [
            frame.icon_button("new", self._new_item),
            frame.icon_button("edit", self._edit_item, True),
            frame.icon_button("delete", self._delete_item, True),
            self.save_button,
            frame.icon_button("exit", self._dismiss),
        ]
        return frame

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(txt.NEW, self._new_item, dimmable=False),
            MenuItem(txt.EDIT, self._edit_item, dimmable=True),
            MenuItem(txt.DELETE, self._delete_item, dimmable=True),
            MenuItem(txt.MOVE_UP, self._move_up, dimmable=True),
            MenuItem(txt.MOVE_DOWN, self._move_down, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _select_item(self, event: tk.Event) -> None:
        self.selected_item = None
        if len(event.widget.curselection()) == 0:
            return
        self.selected_item = event.widget.curselection()[0]
        self.selected_text = self.display_list[self.selected_item]
        self._enable_menu()

    def _enable_menu(self, *args) -> None:
        self.context_menu.enable()
        self._enable_buttons()

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _populate_text_items(self) -> None:
        self.listbox.delete(0, tk.END)
        for index, item in enumerate(self.display_list):
            self.listbox.insert("end", item)
            if self.master_selected_text and item == self.master_selected_text:
                self.listbox.selection_set(index)
                self.selected_text = self.master_selected_text
                self.selected_item = index

        if self.master_selected_text:
            self.master_selected_text = ""
            self._enable_menu()
        self._enable_buttons()

    def _new_item(self, *args) -> None:
        dlg = TextDialogFrame(self, "New")
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.text:
            if self.text_register:
                uid = str(uuid.uuid4())

                self.text_register[uid] = dlg.text
                self.key_register[dlg.text] = uid
                self._populate_text_items()

            self._add_item_to_list(len(self.display_list), dlg.text)

        # print("-" * 50)
        # for key, value in self.key_register.items():
        #     print(f"{key}: {value}")
        # for key, value in self.key_register.inverse.items():
        #     print(f"{key}: {value}")

    def _edit_item(self, *args) -> None:
        dlg = TextDialogFrame(self, "Edit", self.selected_text)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.text == self.selected_text:
            return

        # Update the changes dictionary
        self.changes[self.selected_text] = (self.selected_text, dlg.text)

        # if self.text_register:
        #     self._update_item_register(old_text, dlg.text)

        index = self.display_list.index(self.selected_text)
        self.display_list.remove(self.selected_text)
        self._add_item_to_list(index, dlg.text)

    def _add_item_to_list(self, index: int, text: str) -> None:
        self.display_list.insert(index, text)
        self.selected_text = text
        self._populate_text_items()
        self.listbox.select_set(index)

    def _update_item_register(self, old_text: str, new_text: str):
        # Get the uuid_key for the text
        uuid_key = self.key_register[old_text]

        # swap key register keys
        self.key_register.pop(old_text)
        self.key_register[new_text] = uuid_key

    def _delete_item(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_ITEM):
            return

        if self.key_register:
            pass  # ????

        self.display_list.remove(self.selected_text)
        self.selected_text = ""
        self._populate_text_items()

    def _move_up(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == 0:
            return
        index = self.selected_item
        (self.display_list[index - 1], self.display_list[index]) = (
            self.display_list[index],
            self.display_list[index - 1],
        )
        self._populate_text_items()
        self.listbox.select_set(index - 1)
        self.selected_item -= 1
        self._enable_buttons()

    def _move_down(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == len(self.display_list) - 1:
            return
        index = self.selected_item
        (self.display_list[index + 1], self.display_list[index]) = (
            self.display_list[index],
            self.display_list[index + 1],
        )
        self._populate_text_items()
        self.listbox.select_set(index + 1)
        self.selected_item += 1
        self._enable_buttons()

    def _enable_buttons(self) -> None:
        self.button_frame.disable()
        if self.selected_item is not None:
            self.button_frame.enable()

        self.save_button.disable()
        if self.display_list != self.original_data:
            self.save_button.enable()

    def _save_data(self, *args) -> None:
        if self.text_register:
            self._update_data_set()
        self._sort_data()

        mode = self.mode.name.lower()
        self.mode_data.save(mode)

        self.status = Status.UPDATED
        self._dismiss()

    def _sort_data(self) -> None:
        if isinstance(self.mode_data.data_items, dict):
            sorted_items = {}
            for key in self.display_list:
                sorted_items[key] = self.mode_data.data_items[key]
            self.mode_data.data_items = sorted_items
        else:
            self.mode_data.data_items = self.display_list

    def _update_data_set(self) -> None:
        for old_text, new_text in self.changes.values():
            if old_text != new_text:
                # Update the text register
                uid = self.key_register[old_text]
                self.text_register[uid] = new_text
                # Update the key register
                self.key_register.pop(old_text)
                self.key_register[new_text] = uid
                self.mode_data.amend(self, old_text, new_text)

    def _dismiss(self, *args) -> None:
        self.root.destroy()
