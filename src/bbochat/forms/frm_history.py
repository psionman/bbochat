# forms/frm_history.py

import tkinter as tk
from tkinter import messagebox, ttk

from psiutils.buttons import IconButton
from psiutils.constants import PAD
from psiutils.menus import Menu, MenuItem
from psiutils.widgets import ScrollingCanvas

from bbochat.config import config
from bbochat.constants import ChatMode
from bbochat.message import message_store
from bbochat.text import Text

txt = Text()


class HistoryPanel:
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.root = parent.root
        message_store.subscribe(self._populate_history_frame)
        self.radiobutton_styles = {}

        # tk variables
        self.history_selection = tk.StringVar()

        self.main_frame = self._history_panel(master)

        self.context_menu = self._context_menu()

        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        self._populate_history_frame()

    def _history_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        row = 0
        label = ttk.Label(frame, text="History")
        label.grid(row=row, column=0, padx=PAD, pady=PAD)

        row += 1
        self.history_frame = ScrollingCanvas(
            frame,
            relief=tk.SUNKEN,
            borderwidth=2,
        )
        self.history_frame.grid(row=row, column=0, sticky=tk.NSEW)

        row += 1
        delete_button = IconButton(
            frame, "Delete", "delete", command=self._delete_item
        )
        delete_button.grid(row=row, column=0, padx=PAD, pady=PAD)
        return frame

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(txt.DELETE, self._delete_item, True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _populate_history_frame(self) -> None:
        frame = self.history_frame.content
        for child in frame.winfo_children():
            child.destroy()

        for row, (text, mode) in enumerate(message_store.history.items()):
            if row == 0:
                self.history_selection.set(text)
                self.context_menu.enable()
            style_name = self._radio_button_style(ChatMode(mode))
            label = ttk.Label(frame, text="", style=style_name, width=4)
            label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)
            button = ttk.Radiobutton(
                frame,
                text=text,
                variable=self.history_selection,
                value=text,
                # style=style_name,
                command=self._history_selected,
            )
            button.bind("<Button-3>", self._show_context_menu)
            button.grid(row=row, column=1, padx=PAD, pady=2, sticky=tk.W)

    def _delete_item(self, *args) -> None:
        message = self.history_selection.get()
        if config.confirm_history_delete:
            dlg = messagebox.askokcancel(
                "Remove from history", f"Remove {message}"
            )
            if not dlg:
                return
        message_store.history.pop(message)
        first_item = list(message_store.history.keys())[0]
        message_store.mode = message_store.history[first_item]
        self.context_menu.enable(False)

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _history_selected(self) -> None:
        message = self.history_selection.get()
        mode = message_store.history[message]
        message_store.mode = mode
        message_store.message = message
        if len(message_store.history) <= 1:
            return
        self.context_menu.enable()

    def _radio_button_style(self, mode: ChatMode) -> str:
        if mode in self.radiobutton_styles:
            return self.radiobutton_styles[mode]
        colour = config.colours[str(mode.value)]
        style = ttk.Style(self.root)
        style_name = f"{colour.lstrip('#')}.TLabel"
        style.configure(style_name, background=colour)
        self.radiobutton_styles[mode] = style_name
        return style_name

    def _on_mousewheel(self, event) -> None:
        canvas = self.history_frame.canvas
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return
        # only scroll if pointer is over this panel's canvas or its children
        w = widget
        while w is not None:
            if w == canvas or w == self.history_frame.content:
                canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
                return
            w = w.master
