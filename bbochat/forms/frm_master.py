"""Master tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.widgets import HAND, clickable_widget
from psiutils.treeview import sort_treeview
from psiutils.buttons import ButtonFrame, Button, HORIZONTAL


from constants import MODES, MODE_COLOURS

import text

from forms.frm_edit import EditFrame

PAIR_TREE_COLUMNS = (
    ('username1', 'Opp 1', 100),
    ('username2', 'Opp 2', 100),
)

TEXT_WIDTH = 45

CHAT_HEADINGS_COLOUR = 'red'


class MasterFrame():
    def __init__(self, parent, master):
        self.parent = parent
        self.root = parent.root

        # tk variables
        self.search = parent.search
        self.pairs = parent.pairs
        self.pairs_list = parent.pairs_list
        self.search_pairs = parent.search_pairs
        self.players = parent.players

        self.name_1 = parent.name_1
        self.name_2 = parent.name_2
        self.username_1 = parent.username_1
        self.username_2 = parent.username_2

        self.greeting = parent.greeting
        self.greetings = parent.greetings
        self.greetings_list = parent.greetings_list

        self.valediction = parent.valediction
        self.valedictions = parent.valedictions
        self.valedictions_list = parent.valedictions_list

        self.chat = parent.chat
        self.chat_list = parent.chat_list
        self.chat_line = parent.chat_line

        self.master_frame = self._get_master_frame(master)
        self.master_frame.grid(row=0, column=0, sticky=tk.EW)

    def _get_master_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        search_frame = self._search_frame(frame)
        search_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=PAD)

        # opponents_frame = self._opponents_frame(frame)
        # opponents_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=PAD)

        greetings_frame = self._greetings_frame(frame)
        greetings_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=PAD)

        valediction_frame = self._valediction_frame(frame)
        valediction_frame.grid(row=0, column=2, sticky=tk.NSEW, pady=PAD)

        chat_frame = self._chat_frame(frame)
        chat_frame.grid(row=0, column=3, sticky=tk.NSEW, pady=PAD)

        return frame

    def _search_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        label = ttk.Label(frame, text='Opponents')
        label.grid(row=0, column=0, padx=PAD, pady=PAD)

        self.search_entry = ttk.Entry(frame, textvariable=self.search)
        self.search_entry.grid(row=1, column=0, sticky=tk.EW, padx=PAD)
        self.search_entry.bind('<KeyRelease>', self._search)
        self.search_entry.focus_set()

        opponents_frame = self._opponents_frame(frame)
        opponents_frame.grid(row=2, column=0, sticky=tk.NSEW, pady=PAD)

        return frame

    def _opponents_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # label = ttk.Label(frame, text='Opponents')
        # label.grid(row=0, column=0, padx=PAD, pady=PAD)

        self.pair_tree = self._get_pair_tree(frame)
        self.pair_tree.grid(row=1, column=0,
                            sticky=tk.NSEW, padx=PAD)

        return frame

    def _greetings_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Greetings')
        label.grid(row=0, column=0, padx=PAD, pady=PAD)

        self.greetings_listbox = tk.Listbox(
            frame,
            listvariable=self.greetings_list,
            width=TEXT_WIDTH,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.greetings_listbox.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD)
        self.greetings_listbox.bind('<<ListboxSelect>>',
                                    self._greeting_selected)

        label = ttk.Label(frame, text='Selected greeting')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.greeting)
        entry.grid(row=3, column=0, sticky=tk.EW, padx=PAD)
        colour = MODE_COLOURS[MODES['greeting']]
        entry_style = ttk.Style()
        entry_style.configure(
            'greeting.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style='greeting.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        buttons = [
            Button('Use', self._greeting, style='greeting.TButton'),
            Button(text.EDIT, self._edit_greetings, underline=0),
        ]

        button_frame = ButtonFrame(frame, buttons, HORIZONTAL)
        button_frame.grid(row=4, column=0, pady=PAD)

        return frame

    def _valediction_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Valedictions')
        label.grid(row=0, column=0, padx=PAD, pady=PAD)

        listbox = tk.Listbox(
            frame,
            listvariable=self.valedictions_list,
            width=TEXT_WIDTH,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        listbox.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD)
        listbox.bind('<<ListboxSelect>>', self._valediction_selected)

        label = ttk.Label(frame, text='Selected valediction')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.valediction)
        entry.grid(row=3, column=0, sticky=tk.EW, padx=PAD)
        colour = MODE_COLOURS[MODES['valediction']]
        entry_style = ttk.Style()
        entry_style.configure(
            'valediction.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style='valediction.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        buttons = [
            Button('Use', self._valediction, style='valediction.TButton'),
            Button(text.EDIT, self._edit_valedictions, underline=0),
        ]

        button_frame = ButtonFrame(frame, buttons, HORIZONTAL)
        button_frame.grid(row=4, column=0, pady=PAD)

        return frame

    def _chat_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text='Chat')
        label.grid(row=0, column=0, padx=PAD, pady=PAD)

        self.chat_listbox = tk.Listbox(
            frame,
            width=TEXT_WIDTH,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.chat_listbox.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD)
        self.chat_listbox.bind('<<ListboxSelect>>', self._chat_selected)
        self._populate_chat()

        label = ttk.Label(frame, text='Selected chat')
        label.grid(row=2, column=0, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.chat_line)
        entry.grid(row=3, column=0, sticky=tk.EW, padx=PAD)
        colour = MODE_COLOURS[MODES['chat']]
        entry_style = ttk.Style()
        entry_style.configure(
            'chat.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style='chat.TEntry')
        entry.bind("<Key>", lambda e: 'break')

        buttons = [
            Button('Use', self._chat, style='chat.TButton'),
            Button(text.EDIT, self._edit_chat, underline=0),
        ]

        button_frame = ButtonFrame(frame, buttons, HORIZONTAL)
        button_frame.grid(row=4, column=0, pady=PAD)

        return frame

    def _populate_chat(self) -> None:
        self.chat_listbox.delete('0', tk.END)
        for chat_text in self.chat:
            self.chat_listbox.insert(tk.END, chat_text)
            if '---' in chat_text:
                self.chat_listbox.itemconfig(tk.END, fg=CHAT_HEADINGS_COLOUR)

    def _search(self, *args) -> None:
        pairs = []
        text = self.search.get()
        for pair in self.pairs:
            if text in pair.username_1:
                pairs.append(
                    [pair.username_1, pair.username_2])
            elif text in pair.username_2:
                pairs.append(
                    [pair.username_2, pair.username_1])
        pairs.sort(key=lambda item: item[1])
        pairs.sort(key=lambda item: item[0])
        self.pairs_list.set(pairs)
        self.search_pairs = pairs
        self._populate_pair_tree()

    def _populate_pair_tree(self) -> None:
        self.pair_tree.delete(*self.pair_tree.get_children())
        for pair in self.search_pairs:
            values = (pair[0], pair[1])
            self.pair_tree.insert('', 'end', values=values)

    def _get_pair_tree(self, master: tk.Frame) -> ttk.Treeview:
        """Return  a tree widget for pairs."""
        tree = ttk.Treeview(
            master,
            selectmode='browse',
            height=15,
            show='headings',
            )
        tree.bind('<<TreeviewSelect>>', self._pair_tree_clicked)

        col_list = tuple([col[0] for col in PAIR_TREE_COLUMNS])
        tree['columns'] = col_list
        for col in PAIR_TREE_COLUMNS:
            (col_key, col_text, col_width) = (col[0], col[1], col[2])
            tree.heading(col_key, text=col_text,
                         command=lambda c=col_key:
                         sort_treeview(tree, c, False))
            tree.column(col_key, width=col_width, anchor=tk.W)
        return tree

    def _pair_tree_clicked(self, *args) -> None:
        self.selected_item = self.pair_tree.selection()
        values = self.pair_tree.item(self.selected_item)['values']
        if not values:
            return
        self.pair = [self.players[values[0]], self.players[values[1]]]
        self.username_1.set(self.pair[0].username)
        self.name_1.set(self.pair[0].name)
        self.username_2.set(self.pair[1].username)
        self.name_2.set(self.pair[1].name)
        self.parent.mode = MODES['greeting']
        self.parent.update_clipboard()

    def _greeting_selected(self, event: object = None) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        self.greeting.set(self.greetings[selection[0]])
        self.parent.mode = MODES['greeting']
        self.parent.update_clipboard()

    def _valediction_selected(self, event: object = None) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        self.valediction.set(self.valedictions[selection[0]])
        self.parent.mode = MODES['valediction']
        self.parent.update_clipboard()

    def _chat_selected(self, event: object = None) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        selected_chat = self.chat[selection[0]]
        if '---' in selected_chat:
            return
        self.chat_line.set(selected_chat)
        self.parent.mode = MODES['chat']
        self.parent.update_clipboard()

    def _edit_greetings(self, *args) -> None:
        dlg = EditFrame(self, MODES['greeting'], self.greetings)
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            self.greetings = dlg.data
            self.parent.greetings = dlg.data
            self.parent.save()
            self.greetings_list.set(dlg.data)

    def _edit_valedictions(self, *args) -> None:
        dlg = EditFrame(self, MODES['valediction'], self.valedictions)
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            self.valedictions = dlg.data
            self.parent.valedictions = dlg.data
            self.parent.save()
            self.valedictions_list.set(dlg.data)

    def _edit_chat(self, *args) -> None:
        dlg = EditFrame(self, MODES['chat'], self.chat)
        self.root.wait_window(dlg.root)
        if dlg.status == DIALOG_STATUS['updated']:
            self.chat = dlg.data
            self.parent.chat = dlg.data
            self.parent.save()
            self.chat_list.set(dlg.data)
            self._populate_chat()

    def _greeting(self, *args) -> None:
        self.parent.mode = MODES['greeting']
        self.parent.update_clipboard()

    def _valediction(self, *args) -> None:
        self.parent.mode = MODES['valediction']
        self.parent.update_clipboard()

    def _chat(self, *args) -> None:
        self.parent.mode = MODES['chat']
        self.parent.update_clipboard()
