"""Text Edit Frame for BBO Chat."""

import copy
import tkinter as tk
import uuid
from pathlib import Path
from tkinter import ttk

from psiutils import messagebox
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD, Status
from psiutils.menus import Menu, MenuItem
from psiutils.utilities import window_resize
from psiutils.widgets import HAND

from bbochat.config import get_config
from bbochat.forms.frm_text_dialog import TextDialogFrame
from bbochat.text import Text

txt = Text()

FRAME_TITLE = "Edit"


class EditSelectFrame:
    def __init__(self, parent) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.data_store = parent.data_store

        self.mode = parent.mode

        self.save_button = None
        self.listbox = None
        self.button_frame = None

        # self.master_selected_text is the value of the text selected
        # in the calling function
        self.master_selected_text = parent.selected_text

        self.config = get_config()
        self.status = Status.NULL

        # Original text in data store - used to check change
        self.original_data = [item for item in parent.data.text_list if item]

        # Current text in frame
        self.text_list = [item for item in parent.data.text_list if item]

        # item_register is a dictionary mapping listbox text to unique identifiers
        # It ensures item identity persists during edits or reordering
        # by associating display text with UUIDs.
        self.item_register = {}
        self.text_register = {}
        self.key_register = {}
        self.uuid_register = {}
        if parent.data.text_register:
            self.item_register = copy.deepcopy(parent.data.item_register)
            self.text_register = parent.data.text_register
            self.key_register = parent.data.key_register
            self.uuid_register = parent.data.uuid_register

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
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-s>", self._update_data_set)
        root.bind("<Configure>", lambda e: window_resize(self, __file__))

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

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
            frame, txt.SAVE, "save", self._update_data_set, True
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
        self.selected_text = self.text_list[self.selected_item]
        self._enable_menu()

    def _enable_menu(self, *args) -> None:
        self.context_menu.enable()
        self._enable_buttons()

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _populate_text_items(self) -> None:
        self.listbox.delete(0, tk.END)
        for index, item in enumerate(self.text_list):
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
        self.root.wait_window(dlg.root)
        if dlg.text:
            self.text_list.append(dlg.text)
            if self.text_register:
                uid = str(uuid.uuid4())
                # self.item_register[uid] = (ItemRegistryFields.UUID, dlg.text)
                # self.item_register[dlg.text] = (ItemRegistryFields.TEXT, uid)

                self.text_register[uid] = dlg.text
                self.key_register[dlg.text] = uid
                self.uuid_register[uid] = dlg.text
                self._populate_text_items()

    def _edit_item(self, *args) -> None:
        old_text = self.selected_text
        dlg = TextDialogFrame(self, "Edit", self.selected_text)
        self.root.wait_window(dlg.root)
        if dlg.text == self.selected_text:
            return

        if self.text_register:
            self._update_item_register(old_text, dlg.text)

        index = self.text_list.index(self.selected_text)
        self.text_list.remove(self.selected_text)
        self.text_list.insert(index, dlg.text)
        self.selected_text = dlg.text
        self._populate_text_items()
        self.listbox.select_set(index)

    def _update_item_register(self, old_text: str, new_text: str):
        # Get the item_register text item relating to the
        # old value and replace it with the new text

        # Get the uuid_key for the text
        uuid_key = self.key_register[old_text]
        print(f"{uuid_key=}")

        # swap key register keys
        self.key_register[new_text] = uuid_key
        self.key_register.pop(old_text)

        # update uuid register
        self.uuid_register[uuid_key] = new_text
        print(f"{old_text=}")
        print(f"{new_text=}")
        print(f"{self.uuid_register[uuid_key]=}")
        for key, uuid_text in self.key_register.items():
            print(f"{key=} {uuid_text=}")

    def _delete_item(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_ITEM):
            return

        if self.key_register:
            item_register_member = self.item_register[self.selected_text]
            self.item_register.pop(self.selected_text)
            self.item_register.pop(item_register_member[1])

        self.text_list.remove(self.selected_text)
        self.selected_text = ""
        self._populate_text_items()

    def _move_up(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == 0:
            return
        index = self.selected_item
        (self.text_list[index - 1], self.text_list[index]) = (
            self.text_list[index],
            self.text_list[index - 1],
        )
        self._populate_text_items()
        self.listbox.select_set(index - 1)
        self.selected_item -= 1
        self._enable_buttons()

    def _move_down(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == len(self.text_list) - 1:
            return
        index = self.selected_item
        (self.text_list[index + 1], self.text_list[index]) = (
            self.text_list[index],
            self.text_list[index + 1],
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
        if self.text_list != self.original_data:
            self.save_button.enable()

    def _update_data_set(self, *args) -> None:
        # Problem: mode is chat, but how to you update child data?
        mode = self.mode.name.lower()
        print(f"{len(self.text_register)=} {mode=}")
        if self.text_register:
            # then the dict must be saved with the new key (if any)
            data_set = {}
            for key, value in self.key_register.items():
                data_set[key] = self.text_register[value]

            self.data_store.data_sets[mode] = data_set
        else:
            self.data_store.data_sets[mode] = self.text_list
        self.status = Status.UPDATED
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
