
"""EditFrame for BBO Chat."""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.widgets import HAND
from psiutils.buttons import ButtonFrame, Button
from psiutils.menus import Menu, MenuItem
from psiutils.utilities import window_resize

from config import get_config
from constants import MODES
from data import DataStore
import text

from forms.frm_text_dialog import TextDialogFrame

FRAME_TITLE = 'Edit'


class EditFrame():
    def __init__(self, parent, mode: int) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = get_config()
        self.status = DIALOG_STATUS['null']
        self.data_store = DataStore()
        self.data_store.read()
        ds = self.data_store
        data = ds.data_sets[MODES[mode]]

        self.data = [item for item in data if item]
        self.text = [item for item in data if item]
        self.selected_item = None
        self.selected_text = ''

        # tk variables

        self.show()
        self.context_menu = self._context_menu()
        self._populate_text_items()
        self.button_frame.disable()

    def show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)

        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-s>', self._process)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.text_items = tk.Listbox(
            frame,
            height=6,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.text_items.grid(row=0, column=0, rowspan=6,
                             sticky=tk.NSEW, padx=PAD)
        self.text_items.bind('<<ListboxSelect>>', self._enable_menu)
        self.text_items.bind('<Button-3>', self._show_context_menu)

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

        button = ttk.Button(frame, text=text.CHEVRON_UP,
                            command=self._move_up, width=1)
        button.grid(row=0, column=0, sticky=tk.NS)

        button = ttk.Button(frame, text=text.CHEVRON_DOWN,
                            command=self._move_down, width=1)
        button.grid(row=1, column=0, sticky=tk.NS)
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.VERTICAL)
        self.save_button = Button(
                frame,
                text=text.SAVE,
                command=self._process,
                underline=0,
                dimmable=True)
        frame.buttons = [
            Button(
                frame,
                text=text.NEW,
                command=self._new_item,
                underline=0,
                dimmable=False),
            Button(
                frame,
                text=text.EDIT,
                command=self._edit_item,
                underline=0,
                dimmable=True),
            Button(
                frame,
                text=text.DELETE,
                command=self._delete_item,
                underline=0,
                dimmable=True),
            self.save_button,
            Button(
                frame,
                text=text.EXIT,
                command=self.dismiss,
                sticky=tk.S,
                underline=1),
        ]
        return frame

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.NEW, self._new_item, dimmable=False),
            MenuItem(text.EDIT, self._edit_item, dimmable=True),
            MenuItem(text.DELETE, self._delete_item, dimmable=True),
            MenuItem(text.MOVE_UP, self._move_up, dimmable=True),
            MenuItem(text.MOVE_DOWN, self._move_down, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _enable_menu(self, event: tk.Event) -> None:
        self.context_menu.enable()
        self._show_context_menu(event)

    def _show_context_menu(self, event: tk.Event) -> None:
        self.selected_item = None
        self.context_menu.tk_popup(event.x_root, event.y_root)
        if len(event.widget.curselection()) == 0:
            return
        self.selected_item = event.widget.curselection()[0]
        self.selected_text = self.text[self.selected_item]
        self._enable_buttons()

    def _populate_text_items(self):
        self.text_items.delete(0, tk.END)
        for item in self.text:
            self.text_items.insert('end', item)
        self._enable_buttons()

    def _new_item(self, *args) -> None:
        dlg = TextDialogFrame(self, 'New')
        self.root.wait_window(dlg.root)
        if dlg.text:
            self.text.append(dlg.text)
            self._populate_text_items()

    def _edit_item(self, *args) -> None:
        dlg = TextDialogFrame(self, 'Edit', self.selected_text)
        self.root.wait_window(dlg.root)
        if dlg.text != self.selected_text:
            index = self.text.index(self.selected_text)
            self.text.remove(self.selected_text)
            self.text.insert(index, dlg.text)
            self._populate_text_items()

    def _delete_item(self, *args) -> None:
        if messagebox.askyesno('Delete item', text.DELETE_ITEM):
            self.text.remove(self.selected_text)
            self._populate_text_items()

    def _move_up(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == 0:
            return
        index = self.selected_item
        (self.text[index-1], self.text[index]) = (
            self.text[index], self.text[index-1]
        )
        self._populate_text_items()
        self.text_items.select_set(index-1)
        self.selected_item -= 1
        self._enable_buttons()

    def _move_down(self, *args) -> None:
        if self.selected_item is None:
            return
        if self.selected_item == len(self.text) - 1:
            return
        index = self.selected_item
        (self.text[index+1], self.text[index]) = (
            self.text[index], self.text[index+1]
        )
        self._populate_text_items()
        self.text_items.select_set(index+1)
        self.selected_item += 1
        self._enable_buttons()

    def _enable_buttons(self) -> None:
        self.button_frame.disable()
        if self.selected_item is not None:
            self.button_frame.enable()

        self.save_button.disable()
        if self.text != self.data:
            self.save_button.enable()

    def _process(self, *args) -> None:
        ...

    def dismiss(self, *args) -> None:
        self.root.destroy()
