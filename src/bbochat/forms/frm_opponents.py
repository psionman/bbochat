"""Opponents frame for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils.constants import PAD
from psiutils.treeview import sort_treeview

from bbochat.constants import ChatMode
from bbochat.data_store import data_store
from bbochat.message_store import message_store
from bbochat.pair import PairNew
from bbochat.state import state

PAIR_TREE_COLUMNS = (
    ("username1", "Opp 1", 100),
    ("username2", "Opp 2", 100),
)


class OpponentsFrame:
    def __init__(self, parent, master: ttk.Frame) -> None:
        self.root = parent.root

        # tk variables
        self.search = tk.StringVar()

        self.opponents_frame = self._opponents_frame(master)

        self.search_pairs = []
        self.name_search()
        self._populate_pair_tree()

    def _opponents_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        label = ttk.Label(frame, text="Opponents")
        label.grid(row=0, column=0, padx=PAD)

        self.search_entry = ttk.Entry(frame, textvariable=self.search)
        self.search_entry.grid(row=1, column=0, sticky=tk.EW)
        self.search_entry.bind("<KeyRelease>", self.name_search)
        self.search_entry.focus_set()

        self.pair_tree = self._pair_tree(frame)
        self.pair_tree.grid(row=2, column=0, sticky=tk.NSEW, pady=PAD)

        return frame

    def _populate_pair_tree(self) -> None:
        self.pair_tree.delete(*self.pair_tree.get_children())
        for pair in self.search_pairs:
            values = (pair[0], pair[1])
            self.pair_tree.insert("", "end", values=values)

    def _pair_tree(self, master: ttk.Frame) -> ttk.Treeview:
        """Return  a tree widget for pairs."""
        tree = ttk.Treeview(
            master,
            selectmode="browse",
            height=15,
            show="headings",
        )
        tree.bind("<<TreeviewSelect>>", self._pair_tree_clicked)

        col_list = tuple(col[0] for col in PAIR_TREE_COLUMNS)
        tree["columns"] = col_list
        for col in PAIR_TREE_COLUMNS:
            (col_key, col_text, col_width) = (col[0], col[1], col[2])
            tree.heading(
                col_key,
                text=col_text,
                command=lambda c=col_key: sort_treeview(tree, c, False),
            )
            tree.column(col_key, width=col_width, anchor=tk.W)
        return tree

    def name_search(self, *args) -> None:
        pairs = []
        input_text = self.search.get()
        for pair in data_store.pairs:
            if input_text in pair.player_1.username:
                pairs.append([pair.player_1.username, pair.player_2.username])
            elif input_text in pair.player_2.username:
                pairs.append([pair.player_2.username, pair.player_1.username])
        pairs.sort(key=lambda item: item[1])
        pairs.sort(key=lambda item: item[0])
        self.search_pairs = pairs
        self._populate_pair_tree()

    def _pair_tree_clicked(self, *args) -> None:
        selected_item = self.pair_tree.selection()
        values = self.pair_tree.item(selected_item)["values"]
        if not values:
            return
        player_1 = data_store.players[values[0]]
        player_2 = data_store.players[values[1]]

        message_store.pair = PairNew(player_1, player_2)
        message_store.mode = ChatMode.GREETINGS
        message_store.message = state.last_used_text[ChatMode.GREETINGS.value]
