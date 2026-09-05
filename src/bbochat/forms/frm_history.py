# forms/frm_history.py

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import messagebox, ttk

from psiutils.buttons import IconButton
from psiutils.constants import PAD
from psiutils.menus import Menu, MenuItem
from psiutils.widgets import ScrollingCanvas

from bbochat.config import config
from bbochat.constants import ChatMode
from bbochat.message_store import message_store
from bbochat.state import state
from bbochat.text import Text

txt = Text()

FRAME_HEIGHT = 400
HISTORY_SASH_COUNT = 1


@dataclass
class PanelPopulateInfo:
    item_type: str
    data_source: dict[str, str]
    tk_variable: tk.StringVar
    canvas: ScrollingCanvas
    click_command: Callable
    context_menu_command: Callable


class HistoryPanel:
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.root = parent.root
        message_store.subscribe(self._populate_panels)
        self.radiobutton_styles = {}

        # tk variables
        self.history_selection = tk.StringVar()
        self.pinned_selection = tk.StringVar()

        self.main_frame = self._main_frame(master)

        self.history_context_menu = self._history_context_menu()
        self.pinned_context_menu = self._pinned_context_menu()

        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        self._populate_panels()

        if state.sashes["history_sashes"]:
            for index, sash in enumerate(state.sashes["history_sashes"]):
                self.main_frame.sash_place(index, 0, sash[1])

    def _main_frame(self, master: tk.Frame) -> tk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.VERTICAL)
        frame.rowconfigure(0, weight=1)

        pinned_panel = self._pinned_panel(master)
        frame.add(pinned_panel, height=FRAME_HEIGHT)

        history_panel = self._history_panel(master)
        frame.add(history_panel, height=FRAME_HEIGHT)
        return frame

    def _pinned_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        row = 0
        self.pinned_frame = ScrollingCanvas(
            frame,
            relief=tk.SUNKEN,
            borderwidth=2,
        )
        self.pinned_frame.grid(row=row, column=0, sticky=tk.NSEW)
        return frame

    def _history_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        row = 0
        self.history_frame = ScrollingCanvas(
            frame,
            relief=tk.SUNKEN,
            borderwidth=2,
        )
        self.history_frame.grid(row=row, column=0, sticky=tk.NSEW)

        row += 1
        delete_button = IconButton(
            frame, "Delete", "delete", command=self._delete_history_item
        )
        delete_button.grid(row=row, column=0, padx=PAD, pady=PAD)
        return frame

    def _pinned_context_menu(self) -> Menu:
        menu_items = [
            MenuItem(txt.DELETE, self._delete_pinned_item, True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _history_context_menu(self) -> Menu:
        menu_items = [
            MenuItem("Pin", self._pin_item, True),
            MenuItem(txt.DELETE, self._delete_history_item, True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _populate_history_frame(self) -> None:
        info = PanelPopulateInfo(
            "history",
            data_source=message_store.history,
            tk_variable=self.history_selection,
            canvas=self.history_frame,
            click_command=self._history_selected,
            context_menu_command=self._show_history_context_menu,
        )
        self._populate_message_frame(info)

    def _populate_pinned_frame(self) -> None:
        info = PanelPopulateInfo(
            "pinned",
            data_source=message_store.pinned,
            tk_variable=self.pinned_selection,
            canvas=self.pinned_frame,
            click_command=self._pin_selected,
            context_menu_command=self._show_pinned_context_menu,
        )
        self._populate_message_frame(info)

    def _populate_message_frame(self, info: PanelPopulateInfo) -> None:
        frame = info.canvas.content
        self._delete_message_frame_children(frame)
        items = list(info.data_source.items())
        if items and info.item_type == "pinned":
            if not info.tk_variable.get():
                info.tk_variable.set(items[0][0])
            self.pinned_context_menu.enable()

        for row, (text, mode) in enumerate(items):
            style_name = self._radio_button_style(ChatMode(mode))
            label = ttk.Label(frame, text="", style=style_name, width=4)
            label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

            button = ttk.Radiobutton(
                frame,
                text=text,
                variable=info.tk_variable,
                value=text,
                command=info.click_command,
            )
            button.bind("<Button-3>", info.context_menu_command)
            button.grid(row=row, column=1, padx=PAD, pady=2, sticky=tk.W)

    def _delete_message_frame_children(self, frame: ScrollingCanvas) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _pin_item(self, *args) -> None:
        text = self.history_selection.get()
        mode = message_store.history[text]
        if text not in message_store.pinned:
            message_store.pinned[text] = mode
            state.save()
        # message_store.history.pop(text)
        first_item = list(message_store.history.keys())[0]
        message_store.mode = message_store.history[first_item]
        self.history_selection.set(first_item)
        self._populate_panels()

    def _delete_pinned_item(self, *args) -> None:
        if len(message_store.pinned) < 1:
            return
        message = self.pinned_selection.get()
        if config.confirm_history_delete:
            dlg = messagebox.askokcancel(
                "Remove from pinned", f"Remove {message}"
            )
            if not dlg:
                return
        message_store.pinned.pop(message)

    def _delete_history_item(self, *args) -> None:
        if len(message_store.history) < 1:
            return
        message = self.history_selection.get()
        if config.confirm_history_delete:
            dlg = messagebox.askokcancel(
                "Remove from history", f"Remove {message}"
            )
            if not dlg:
                return
        message_store.history.pop(message)

        self.history_context_menu.enable(False)
        self._populate_panels()
        if len(message_store.history) < 1:
            return
        first_item = list(message_store.history.keys())[0]
        message_store.mode = message_store.history[first_item]
        self.history_selection.set(first_item)

    def _show_history_context_menu(self, event: tk.Event) -> None:
        self.history_context_menu.tk_popup(event.x_root, event.y_root)

    def _show_pinned_context_menu(self, event: tk.Event) -> None:
        self.pinned_context_menu.tk_popup(event.x_root, event.y_root)

    def _populate_panels(self) -> None:
        self._populate_history_frame()
        self._populate_pinned_frame()

    def _pin_selected(self) -> None:
        message = self.pinned_selection.get()
        mode = message_store.pinned[message]
        message_store.mode = mode
        message_store.message = message
        self.history_selection.set("")

    def _history_selected(self) -> None:
        message = self.history_selection.get()
        mode = message_store.history[message]
        message_store.mode = mode
        message_store.message = message
        if len(message_store.history) <= 1:
            return
        self.pinned_selection.set("")
        self.history_context_menu.enable()

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
