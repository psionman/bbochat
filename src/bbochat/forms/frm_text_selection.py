"""Text Selection frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from bbochat.message_store import message_store
from psiutils import messagebox
from psiutils.buttons import IconButton
from psiutils.constants import PAD, Status
from psiutils.menus import Menu, MenuItem
from psiutils.widgets import HAND

from bbochat.buttons import ButtonFrame
from bbochat.config import config
from bbochat.constants import MODE_TEXT, ChatMode
from bbochat.forms.frm_edit_select import EditSelectFrame
from bbochat.forms.frm_text_dialog import TextDialogFrame
from bbochat.mode_data import ModeData
from bbochat.text import Text

txt = Text()

WHITE = "#ffffff"
BLACK = "#000000"


class TextSelectionFrame:
    def __init__(
        self,
        parent: ttk.Frame,
        master: ttk.Frame,
        mode: ChatMode,
        mode_data: ModeData,
        show_use_frame: bool = True,
        show_title: bool = True,
        slave=None,
    ) -> None:

        self.root = parent.root
        self.show_use_frame = show_use_frame
        self.show_title = show_title
        self.has_slave_frame = slave
        self.master_frame = None
        self.mode_data = mode_data
        self.mode = mode
        self.mode_text = MODE_TEXT[mode.value]
        self.use_frame = None

        self.config_key = f"last_{self.mode.name.lower()}"
        self.config = config
        config.subscribe(self._on_config_change)

        # last_value = (
        #     self.config.config[self.config_key]
        #     if self.config_key in self.config.config
        #     else ""
        # )
        # print(mode.value, config.last_chat)
        last_value = (
            config.last_used_text[str(mode.value)]
            if str(mode.value) in config.last_used_text
            else ""
        )
        self.text_var = tk.StringVar(value=last_value)

        # self.selected_text contains the text selected from the listbox
        self.selected_text = ""
        # self.selected_index is the index of selected text in self.text_data
        self.selected_index = -1

        self.main_frame = self._main_frame(master)
        self.context_menu = self._context_menu()

        self.populate_text_items()
        self.root.update_idletasks()

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        if self.show_title:
            label = ttk.Label(frame, text=f"{self.mode_text.capitalize()}s")
            label.grid(row=0, column=0)

        self.listbox = tk.Listbox(
            frame,
            selectmode=tk.BROWSE,
            cursor=HAND,
            exportselection=False,  # ← Important
            activestyle="none",  # ← Removes the dotted underline
        )
        self.listbox.grid(row=1, column=0, sticky=tk.NSEW)
        self.listbox.bind("<<ListboxSelect>>", self._item_selected)
        self.listbox.bind("<Button-3>", self._show_context_menu)
        self.listbox.bind("<FocusIn>", self._on_focus_in)
        self.listbox.bind("<FocusOut>", self._on_focus_out)

        if self.show_use_frame:
            self.use_frame = self._use_frame(frame)
            self.use_frame.grid(row=2, column=0, sticky=tk.EW)

        return frame

    def _on_focus_in(self, event=None):
        colour = self.config.colours[str(self.mode.value)]
        self.listbox.config(selectbackground=colour)

    def _on_focus_out(self, event=None):
        self.listbox.config(selectbackground=WHITE)
        self.listbox.config(selectforeground=BLACK)

    def _use_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        self._populate_use_frame(frame)
        return frame

    def _populate_use_frame(self, frame: ttk.Frame):
        if frame:
            for widget in frame.winfo_children():
                widget.destroy()

        label = ttk.Label(frame, text=f"Selected {self.mode_text}")
        label.grid(row=0, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.text_var)
        entry.grid(row=1, column=0, sticky=tk.EW)
        colour = self.config.colours[str(self.mode.value)]
        entry_style = ttk.Style()
        entry_style.configure(
            f"{self.mode}.TEntry",
            fieldbackground=colour,
        )
        entry.configure(style=f"{self.mode}.TEntry")
        entry.bind("<Key>", lambda e: "break")

        button_frame = ButtonFrame(frame, tk.HORIZONTAL)
        use_button = IconButton(button_frame, txt.USE, "done", self._use_item)
        use_button.widget.configure(style=f"{self.mode}.TButton")
        button_frame.buttons = [
            use_button,
            IconButton(button_frame, txt.EDIT, "edit", self._edit_all),
        ]
        button_frame.grid(row=2, column=0, pady=PAD)

        return frame

    def _item_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return

        self.selected_text = self.mode_data.display_list[selection[0]]

        self.text_var.set(self.selected_text)
        self._use_item()
        self.context_menu.enable()
        if self.has_slave_frame:
            # This is a master: it has a slave frame
            # This line breaks after edit all
            self.has_slave_frame.display_list = self.mode_data.data_items[
                self.selected_text
            ]
            self.mode_data.update_slave_data(
                self.has_slave_frame, self.selected_text
            )

    def _new_item(self, *args) -> None:
        dlg = TextDialogFrame(self, "New", show_save=True)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if not dlg.text:
            return

        self.mode_data.add(self, dlg.text)

        self.text_var.set(dlg.text)
        self._use_item()
        self.selected_text = dlg.text

        self.populate_text_items(dlg.text)

    def _edit_item(self, *args) -> None:
        dlg = TextDialogFrame(self, "Edit", self.selected_text, show_save=True)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.status != Status.UPDATED:
            return

        self.mode_data.amend(self, self.selected_text, dlg.text)

        self.populate_text_items(self.mode_data.display_list_raw)

        self.selected_text = dlg.text
        self.text_var.set(dlg.text)
        self._use_item()

    def _delete_item(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_ITEM):
            return

        self.mode_data.delete(self)

        if self.has_slave_frame:
            # This is a master: it has a slave frame
            self.has_slave_frame.populate_text_items()

        self.text_var.set("")
        self._use_item()
        self.populate_text_items()

    def _edit_all(self, *args) -> None:
        dlg = EditSelectFrame(self)
        self.root.wait_window(dlg.root)
        if dlg.status != Status.UPDATED:
            return
        self.mode_data.edit_all(self, dlg.display_list)

        self.populate_text_items(dlg.selected_text)
        self.selected_text = dlg.selected_text
        self.text_var.set(dlg.selected_text)
        self._use_item()

    def _update_text_list(
        self, display_list: list[str], old_text: str, new_text: str
    ) -> None:
        index = display_list.index(old_text)
        display_list.remove(old_text)
        display_list.insert(index, new_text)

    def _use_item(self, *args) -> None:
        if not self.text_var.get():
            return
        if self.text_var.get() and self.text_var.get()[0] == "#":
            return

        message_store.mode = self.mode
        message_store.selected_messages[self.mode] = self.text_var.get()
        message_store.message = self.text_var.get()
        config.config["last_used_text"][str(self.mode.value)] = (
            self.text_var.get()
        )
        config.save()

    def populate_text_items(self, selected_item: str = "") -> None:
        self.listbox.delete(0, tk.END)
        for index, item in enumerate(self.mode_data.display_list):
            self.listbox.insert("end", item)
            if selected_item and item == selected_item:
                self.listbox.selection_set(index)

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(txt.NEW, self._new_item, dimmable=False),
            MenuItem(txt.EDIT_ALL, self._edit_all, dimmable=False),
            MenuItem(txt.EDIT_ITEM, self._edit_item, dimmable=True),
            MenuItem(txt.DELETE, self._delete_item, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _on_config_change(self) -> None:
        if self.use_frame:
            self._populate_use_frame(self.use_frame)

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
