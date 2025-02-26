"""Chat frame for BBO Chat."""

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


class ChatFrame():
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.parent = parent
        self.root = parent.root
        self.config = get_config()

        self.chat = parent.chat
        self.chat_list = parent.chat_list
        self.chat_line = parent.chat_line
        self.chat_topics = list(self.chat.keys())
        self.chat_topic = ''

        self.chat_frame = self._chat_frame(master)
        self.context_menu = self._context_menu()

        self._populate_chat()

    def _chat_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Chat')
        label.grid(row=0, column=0, pady=PAD)

        self.chat_panel = self._chat_panel(frame)
        self.chat_panel.grid(row=1, column=0, sticky=tk.NSEW)

        label = ttk.Label(frame, text='Selected chat')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.chat_line)
        entry.grid(row=3, column=0, sticky=tk.EW, padx=(0, PAD))
        colour = self.config.colours['chat']
        entry_style = ttk.Style()
        entry_style.configure(
            'chat.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style='chat.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        button_frame = ButtonFrame(frame, tk.HORIZONTAL)
        buttons = [
            Button(
                button_frame,
                text='Use',
                command=self._chat,
                style='chat.TButton'),
            Button(
                button_frame,
                text=text.EDIT,
                command=self._edit_chat,
                underline=0),
        ]

        button_frame.buttons = buttons
        button_frame.grid(row=4, column=0, pady=PAD)

        return frame

    def _chat_panel(self, master: ttk.Frame) -> ttk.PanedWindow:
        frame = tk.PanedWindow(master, orient=tk.VERTICAL)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.chat_selector = tk.Listbox(
            frame,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.chat_selector.grid(row=0, column=0, sticky=tk.NSEW)
        self.chat_selector.bind('<<ListboxSelect>>', self._chat_topic_selected)
        self.chat_selector.bind('<Button-3>', self._show_context_menu)
        frame.add(self.chat_selector)

        self.chat_listbox = tk.Listbox(
            frame,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.chat_listbox.grid(row=0, column=0, sticky=tk.NSEW)
        frame.add(self.chat_listbox)
        self.chat_listbox.bind('<<ListboxSelect>>', self._chat_selected)

        return frame

    def _populate_chat(self) -> None:
        self.chat_selector.delete('0', tk.END)
        for chat_text in self.chat_topics:
            self.chat_selector.insert(tk.END, chat_text)

    def _chat_topic_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        self.chat_topic = self.chat_topics[selection[0]]
        self.chat_listbox.delete('0', tk.END)
        for chat_text in self.chat[self.chat_topic]:
            self.chat_listbox.insert(tk.END, chat_text)

    def _chat(self, *args) -> None:
        self.parent.parent.mode = MODES['chat']
        self.parent.parent.update_clipboard()

    def _chat_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        selected_chat = self.chat[self.chat_topic][selection[0]]
        self.chat_line.set(selected_chat)
        self.parent.mode = MODES['chat']
        self.parent.parent.update_clipboard()
        self._chat()

    def _edit_chat(self, *args) -> None:
        dlg = EditFrame(self, MODES['chat'])
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            self.chat = dlg.data
            self.parent.chat = dlg.data
            self.parent.save()
            self.chat_list.set(dlg.data)
            self._populate_chat()

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.EDIT, self._edit_chat),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
