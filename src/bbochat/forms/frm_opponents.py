"""Opponents frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD
from psiutils.treeview import sort_treeview

from bbochat.config import get_config


PAIR_TREE_COLUMNS = (
    ('username1', 'Opp 1', 100),
    ('username2', 'Opp 2', 100),
)


class OpponentsFrame():
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.parent = parent
        self.root = parent.root
        self.config = get_config()

        # tk variables
        self.search = parent.parent.search
        self.pairs = parent.parent.pairs
        self.players = parent.parent.players

        self.name_1 = parent.parent.name_1
        self.name_2 = parent.parent.name_2
        self.username_1 = parent.parent.username_1
        self.username_2 = parent.parent.username_2

        self.opponents_frame = self._opponents_frame(master)

        self.search_pairs = []
        self.name_search()
        self._populate_pair_tree()

    def _opponents_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        label = ttk.Label(frame, text='Opponents')
        label.grid(row=0, column=0, padx=PAD)

        self.search_entry = ttk.Entry(frame, textvariable=self.search)
        self.search_entry.grid(row=1, column=0, sticky=tk.EW)
        self.search_entry.bind('<KeyRelease>', self.name_search)
        self.search_entry.focus_set()

        self.pair_tree = self._pair_tree(frame)
        self.pair_tree.grid(row=2, column=0,
                            sticky=tk.NSEW, pady=PAD)

        return frame

    def _populate_pair_tree(self) -> None:
        self.pair_tree.delete(*self.pair_tree.get_children())
        for pair in self.search_pairs:
            values = (pair[0], pair[1])
            self.pair_tree.insert('', 'end', values=values)

    def _pair_tree(self, master: ttk.Frame) -> ttk.Treeview:
        """Return  a tree widget for pairs."""
        tree = ttk.Treeview(
            master,
            selectmode='browse',
            height=15,
            show='headings',
            )
        tree.bind('<<TreeviewSelect>>', self._pair_tree_clicked)

        col_list = tuple(col[0] for col in PAIR_TREE_COLUMNS)
        tree['columns'] = col_list
        for col in PAIR_TREE_COLUMNS:
            (col_key, col_text, col_width) = (col[0], col[1], col[2])
            tree.heading(col_key, text=col_text,
                         command=lambda c=col_key:
                         sort_treeview(tree, c, False))
            tree.column(col_key, width=col_width, anchor=tk.W)
        return tree

    def name_search(self, *args) -> None:
        pairs = []
        input_text = self.search.get()
        for pair in self.pairs:
            if input_text in pair.username_1:
                pairs.append(
                    [pair.username_1, pair.username_2])
            elif input_text in pair.username_2:
                pairs.append(
                    [pair.username_2, pair.username_1])
        pairs.sort(key=lambda item: item[1])
        pairs.sort(key=lambda item: item[0])
        self.search_pairs = pairs
        self._populate_pair_tree()

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

        self.parent.parent.pair_tree_clicked()
