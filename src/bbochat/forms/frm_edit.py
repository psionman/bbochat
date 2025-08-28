
"""Text Edit Frame for BBO Chat."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import uuid
import copy

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.widgets import HAND
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.menus import Menu, MenuItem
from psiutils.utilities import window_resize
from psiutils import messagebox

from bbochat.config import get_config
from bbochat.constants import META_CODES
import text as txt

from bbochat.forms.frm_text_dialog import TextDialogFrame

FRAME_TITLE = 'Edit'


class EditFrame():
    def __init__(self, parent) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.mode = parent.mode

        self.save_button = None
        self.listbox = None
        self.button_frame = None

        # self.master_selected_text is the value of the text selected
        # in the calling function
        self.master_selected_text = parent.selected_text

        self.config = get_config()
        self.status = DIALOG_STATUS['null']

        # Original text in data store - used to check change
        self.original_data = [item for item in parent.data.text_list if item]

        # Current text in frame
        self.text_list = [item for item in parent.data.text_list if item]

        self.meta_dict = {}
        if parent.data.meta_dict:
            self.meta_dict = copy.deepcopy(parent.data.meta_dict)

        # self.selected_item is the index of the item selected in the listbox
        self.selected_item = None

        # self.selected_text contains the text selected from the listbox
        self.selected_text = ''

        self._show()
        self.context_menu = self._context_menu()
        self.button_frame.disable()
        self._populate_text_items()

    def _show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-s>', self._save)
        root.bind('<Configure>',
                  lambda e: window_resize(self, __file__))

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
        self.listbox.bind('<<ListboxSelect>>', self._select_item)
        self.listbox.bind('<Button-3>', self._show_context_menu)

        scroll_buttons = self._scroll_buttons(frame)
        scroll_buttons.grid(row=0, column=1, sticky=tk.NS)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=0, column=2,
                               sticky=tk.NS, padx=PAD)

        return frame

    def _scroll_buttons(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button = ttk.Button(frame, text=txt.CHEVRON_UP,
                            command=self._move_up, width=1)
        button.grid(row=0, column=0, sticky=tk.NS)

        button = ttk.Button(frame, text=txt.CHEVRON_DOWN,
                            command=self._move_down, width=1)
        button.grid(row=1, column=0, sticky=tk.NS)
        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.VERTICAL)
        self.save_button = IconButton(
            frame, txt.SAVE, 'save', True, self._save)
        frame.buttons = [
            frame.icon_button('new', False, self._new_item),
            frame.icon_button('edit', True, self._edit_item),
            frame.icon_button('delete', True, self._delete_item),
            self.save_button,
            frame.icon_button('exit', False, self._dismiss),
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
            self.listbox.insert('end', item)
            if self.master_selected_text and item == self.master_selected_text:
                self.listbox.selection_set(index)
                self.selected_text = self.master_selected_text
                self.selected_item = index

        if self.master_selected_text:
            self.master_selected_text = ''
            self._enable_menu()
        self._enable_buttons()

    def _new_item(self, *args) -> None:
        dlg = TextDialogFrame(self, 'New')
        self.root.wait_window(dlg.root)
        if dlg.text:
            self.text_list.append(dlg.text)
            uid = str(uuid.uuid4())
            self.meta_dict[uid] = (META_CODES['uuid'], dlg.text)
            self.meta_dict[dlg.text] = (META_CODES['text'], uid)
            self._populate_text_items()

    def _edit_item(self, *args) -> None:
        dlg = TextDialogFrame(self, 'Edit', self.selected_text)
        self.root.wait_window(dlg.root)
        if dlg.text == self.selected_text:
            return

        if self.meta_dict:
            self._update_meta_dict(dlg.text)

        index = self.text_list.index(self.selected_text)
        self.text_list.remove(self.selected_text)
        self.text_list.insert(index, dlg.text)
        self.selected_text = dlg.text
        self._populate_text_items()
        self.listbox.select_set(index)

    def _update_meta_dict(self, text: str):
        # Get the meta_dict text item relating to the old value
        meta_text_item = self.meta_dict[self.selected_text]

        # Get the related uuid item
        meta_uuid_key = meta_text_item[1]

        # Rebuild the uuid item with the new text
        self.meta_dict[meta_uuid_key] = (META_CODES['uuid'], text)

        # Create a text item with the new text
        self.meta_dict[text] = (META_CODES['text'], meta_uuid_key)
        # ic(len(self.meta_dict))

        # Remove the text item relating to the old value
        self.meta_dict.pop(self.selected_text)

    def _delete_item(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_ITEM):
            return

        if self.meta_dict:
            meta_text_item = self.meta_dict[self.selected_text]
            self.meta_dict.pop(self.selected_text)
            self.meta_dict.pop(meta_text_item[1])

        self.text_list.remove(self.selected_text)
        self.selected_text = ''
        self._populate_text_items()

    def _move_up(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == 0:
            return
        index = self.selected_item
        (self.text_list[index-1], self.text_list[index]) = (
            self.text_list[index], self.text_list[index-1]
        )
        self._populate_text_items()
        self.listbox.select_set(index-1)
        self.selected_item -= 1
        self._enable_buttons()

    def _move_down(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == len(self.text_list) - 1:
            return
        index = self.selected_item
        (self.text_list[index+1], self.text_list[index]) = (
            self.text_list[index], self.text_list[index+1]
        )
        self._populate_text_items()
        self.listbox.select_set(index+1)
        self.selected_item += 1
        self._enable_buttons()

    def _enable_buttons(self) -> None:
        self.button_frame.disable()
        if self.selected_item is not None:
            self.button_frame.enable()

        self.save_button.disable()
        if self.text_list != self.original_data:
            self.save_button.enable()

    def _save(self, *args) -> None:
        if self.meta_dict:
            for index, value in enumerate(self.text_list):
                meta_item = self.meta_dict[value]
                self.meta_dict[value] = (meta_item[0], meta_item[1], index)

        self.status = DIALOG_STATUS['updated']
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
