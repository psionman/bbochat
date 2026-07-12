"""MainFrame for BBO Chat."""

import contextlib
import random
import re
import tkinter as tk
from pathlib import Path
from tkinter import simpledialog, ttk

import clipboard
import emoji
from psiutils import messagebox
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD
from psiutils.utilities import window_resize

from bbochat.config import config, get_config
from bbochat.constants import ChatMode
from bbochat.data_store import Pair, Player, data_store
from bbochat.forms.frm_master import MasterFrame
from bbochat.forms.frm_notes import NotesFrame
from bbochat.forms.frm_partners import PartnerFrame
from bbochat.forms.frm_tournament import TournamentFrame
from bbochat.main_menu import MainMenu
from bbochat.text import Text

txt = Text()
FRAME_TITLE = "BBO Chat"

VERTICAL_FRAME_COUNT = 3
HORIZONTAL_FRAME_COUNT = 1
NOTES_FRAME_COUNT = 1

# Handles cases when size gets corrupted, e.g. after stop on error
DEFAULT_GEOMETRY = "1250x700"


class MainFrame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = config
        config.subscribe(self._on_config_change)
        self.mode = ChatMode.GREETINGS

        data_store.read()
        data_store.subscribe(self._on_data_change)
        self.data_server = data_store

        self.greetings = data_store.greetings
        self.valedictions = data_store.valedictions
        self.chat = data_store.chat
        self.my_name = data_store.my_name

        self.pair = []

        self.partner = ""
        self.partners = data_store.partners
        self.partners_names = sorted(list(self.partners.keys()))
        if config.last_partner and config.last_partner in self.partners:
            self.partner = self.partners[config.last_partner]

        # tk variables
        self._create_tk_variables()
        self.username_1.trace_add("write", self._pair_username_change)
        self.username_2.trace_add("write", self._pair_username_change)
        self.name_1.trace_add("write", self._update_clipboard)
        self.name_2.trace_add("write", self._update_clipboard)

        self.last_mode_text = {
            ChatMode.GREETINGS: config.last_greeting,
            ChatMode.VALEDICTION: config.last_valediction,
            ChatMode.CHAT: config.last_chat,
        }

        self.save_button = None
        self.delete_button = None
        self.button_frame = None
        self.clipboard_entry = None
        self.master_tab = None
        self.tournament_tab = None
        self.notes_tab = None

        self._show()

        self.pair_tree = self.master_tab.pair_tree
        self.search_entry = self.master_tab.search_entry

        self._set_clipboard_colour()
        self._pair_username_change()

        # On setup
        if not data_store.data_sets["my_name"]:
            self._get_my_name()

    def _create_tk_variables(self) -> None:
        self.clipboard = tk.StringVar()

        # Main
        self.search = tk.StringVar()
        self.username_1 = tk.StringVar()
        self.username_2 = tk.StringVar()
        self.name_1 = tk.StringVar()
        self.name_2 = tk.StringVar()
        self.randomize = tk.BooleanVar(value=config.randomize_name_order)

        greeting = self.partner.greeting if self.partner else ""
        self.greeting = tk.StringVar(value=greeting)
        self.greetings_list = tk.StringVar(value=self.greetings)
        self.valediction = tk.StringVar(value=config.last_valediction)
        self.chat_list = tk.StringVar(value=self.chat)
        self.system = tk.StringVar()
        self.chat_line = tk.StringVar()

        # Partners
        self.partners_list = tk.StringVar(value=self.partners_names)
        self.selected_partner = tk.StringVar(value=config.last_partner)
        self.my_name_text = tk.StringVar(value=self.my_name)
        self.partners_name = tk.StringVar(value="")
        self.partners_username = tk.StringVar()

    def _show(self):
        root = self.root
        root.protocol("WM_DELETE_WINDOW", self._dismiss)
        root.geometry(self._geometry())
        root.title(FRAME_TITLE)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_menu = MainMenu(self)
        main_menu.create()

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=1, column=0, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

        self.root.update_idletasks()
        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-g>", self._greeting)
        root.bind("<Control-v>", self._valediction)
        root.bind("<Control-c>", self._chat)
        # root.bind("<Control-s>", self.save)
        root.bind("<Configure>", lambda e: window_resize(self, __file__))

    def _geometry(self) -> str:
        try:
            geometry = config.geometry[Path(__file__).stem]
            width = int(geometry.split("x")[0])
            return DEFAULT_GEOMETRY if width < 10 else geometry
        except tk.TclError:
            return DEFAULT_GEOMETRY

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)

        row = 0
        clipboard_frame = self._clipboard_frame(frame)
        clipboard_frame.grid(
            row=row, column=0, columnspan=2, sticky=tk.EW, padx=PAD
        )

        row += 1
        names_frame = self._names_frame(frame)
        names_frame.grid(row=row, column=0, sticky=tk.NW, padx=PAD)

        row += 1
        frame.rowconfigure(row, weight=1)
        notebooks = self._notebook_frames(frame)
        notebooks.grid(
            row=row, column=0, columnspan=2, sticky=tk.NSEW, padx=PAD
        )
        return frame

    def _clipboard_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text="Clipboard")
        label.grid(row=0, column=0, sticky=tk.E, padx=PAD)

        self.clipboard_entry = ttk.Entry(frame, textvariable=self.clipboard)
        self.clipboard_entry.grid(
            row=0, column=1, columnspan=1, sticky=tk.EW, padx=0, pady=PAD
        )
        self.clipboard_entry.bind("<KeyRelease>", self.copy_to_clipboard)

        button = IconButton(
            frame, "Copy", "copy_clipboard", self.copy_to_clipboard
        )
        button.grid(row=0, column=2, padx=PAD)

        return frame

    def _names_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)

        identity_frame = self._identity_frame(frame)
        identity_frame.grid(row=0, column=0, sticky=tk.NW, padx=PAD)

        opponents_frame = self._opponents_frame(frame)
        opponents_frame.grid(row=0, column=1, sticky=tk.W, padx=PAD)

        return frame

    def _identity_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)

        label = ttk.Label(frame, text="My name")
        label.grid(row=1, column=0, sticky=tk.E)

        entry = ttk.Entry(
            frame, textvariable=self.my_name_text, state="readonly"
        )
        entry.grid(row=1, column=1, sticky=tk.W, padx=PAD)

        label = ttk.Label(frame, text="Partner")
        label.grid(row=2, column=0, sticky=tk.E, pady=PAD)

        entry = ttk.Entry(
            frame, textvariable=self.partners_username, state="readonly"
        )
        entry.grid(row=2, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        return frame

    def _opponents_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text="Opponents")
        label.grid(row=1, column=2)

        entry = ttk.Entry(frame, textvariable=self.username_1)
        entry.grid(row=1, column=3, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.name_1)
        entry.grid(row=2, column=3, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.username_2)
        entry.grid(row=1, column=4, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.name_2)
        entry.grid(row=2, column=4, pady=PAD)

        self.save_button = IconButton(
            frame, txt.SAVE, "save", self._save_names, True
        )
        self.save_button.grid(row=1, column=5, padx=PAD, sticky=tk.EW)

        self.delete_button = IconButton(
            frame, txt.DELETE, "delete", self._delete_pair, True
        )
        self.delete_button.grid(row=2, column=5, padx=PAD, pady=PAD)

        check_button = ttk.Checkbutton(
            frame, text="Randomize opp's names order", variable=self.randomize
        )
        check_button.grid(row=1, column=6, rowspan=2, sticky=tk.W)

        return frame

    def _notebook_frames(self, master: ttk.Frame) -> ttk.Notebook:
        notebook = ttk.Notebook(master, style="master.TNotebook")

        self.master_tab = MasterFrame(self, notebook)
        notebook.add(self.master_tab.master_frame, text="Master")

        partners_tab = PartnerFrame(self, notebook)
        notebook.add(partners_tab.partners_frame, text="Partners")

        self.notes_tab = NotesFrame(self, notebook)
        notebook.add(self.notes_tab.notes_frame, text="Notes")

        self.tournament_tab = TournamentFrame(self, notebook)
        notebook.add(self.tournament_tab.notes_frame, text="Tournament")

        return notebook

    def _button_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("close", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _greeting(self, *args) -> None:
        self.mode = ChatMode.GREETINGS
        self.update_clipboard()

    def _valediction(self, *args) -> None:
        self.mode = ChatMode.VALEDICTION
        self.update_clipboard()

    def _chat(self, *args) -> None:
        self.mode = ChatMode.CHAT
        self.update_clipboard()

    def _get_my_name(self) -> None:
        if dlg := simpledialog.askstring(
            "Your name",
            "Enter the name that you wish to be known by",
            parent=self.root,
        ):
            self.my_name = dlg
            self.my_name_text.set(dlg)
            data_store.my_name = dlg
            data_store.save()

    def _on_config_change(self, *args):
        self.randomize.set(config.randomize_name_order)
        self._set_clipboard_colour()

    def _set_clipboard_colour(self):
        colour = config.colours[self.mode.name]
        entry_style = ttk.Style()
        entry_style.configure(
            "clipboard_entry.TEntry",
            fieldbackground=colour,
        )
        with contextlib.suppress(tk.TclError):
            self.clipboard_entry.configure(style="clipboard_entry.TEntry")

    def _update_clipboard(self, *args) -> None:
        self.update_clipboard()

    def update_clipboard(
        self, message: str = "", mode: int = None, *args
    ) -> None:
        if mode is not None:
            self.last_mode_text[mode] = message
            self.mode = mode
        self._set_clipboard_colour()

        if not message:
            if mode is None:
                message = self.last_mode_text[ChatMode.GREETINGS]
            else:
                message = self.last_mode_text[mode]

        self._create_message(message)

    def _create_message(self, message: str) -> None:
        if self.partner:
            names = f"{self.partner.name} and {self.my_name}"
            system = self.partner.system
        else:
            names = f"{self.my_name}"
            system = ""

        opps = self._get_opps()
        message = message.replace("<opps>", opps)
        message = message.replace("<names>", names)
        message = message.replace("<system>", system)
        self.clipboard.set(message)
        self.copy_to_clipboard()

    def copy_to_clipboard(self, *args) -> None:
        text = self.clipboard.get()
        emoji_re = r":.*:"

        found = True
        while found:
            match = re.search(emoji_re, text)
            if not match:
                break
            emoji_text = match.group()
            emoji_ = emoji.emojize(emoji_text)
            text = text.replace(emoji_text, emoji_)
            if emoji_text == emoji_:
                found = False
        clipboard.copy(text)

    def _get_opps(self) -> str:
        opp_1, opp_2 = self.name_1.get(), self.name_2.get()
        if self.randomize.get():
            opps = [opp_1, opp_2]
            choice = random.choice([0, 1])
            opp_1 = opps[choice]
            choice = (choice + 1) % 2
            opp_2 = opps[choice]

        if opp_1.lower() == "robot":
            opp_1, opp_2 = opp_2, opp_1
        if opp_2.lower() == "robot":
            opp_2 = ""

        if opp_1:
            return f"{opp_1} and {opp_2}" if opp_2 else opp_1
        return opp_2

    def _save_names(self, *args) -> None:
        name_1 = self.name_1.get()
        name_2 = self.name_2.get()
        username_1 = self.username_1.get()
        username_2 = self.username_2.get()

        pair = Pair(username_1, username_2)
        data_store.players[username_1] = Player(name_1, username_1)
        data_store.players[username_2] = Player(name_2, username_2)
        if pair not in data_store.pairs:
            data_store.pairs.append(Pair(username_1, username_2))

        self.save()
        # self.search.set("")
        self.pair_tree.delete(*self.pair_tree.get_children())
        # self.search.set(self.username_1.get())
        self.search_entry.focus_set()
        self.master_tab.opponents_frame.name_search()
        self.update_clipboard()

    def _delete_pair(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_PAIR):
            return

        pair = Pair(self.username_1.get(), self.username_2.get())
        data_store.pairs.remove(pair)
        self.save()

        self.name_1.set("")
        self.name_2.set("")
        self.username_1.set("")
        self.username_2.set("")
        self._pair_username_change()
        # self.search.set("")
        self.pair_tree.delete(*self.pair_tree.get_children())
        # self.search.set(self.username_1.get())
        self.search_entry.focus_set()

    def save(self, *args) -> None:
        data_store.save()
        self.enable_buttons(False)

    def _pair_username_change(self, *args) -> None:
        username_1 = self.username_1.get().lower()
        username_2 = self.username_2.get().lower()
        self.username_1.set(self.username_1.get().lower())
        self.username_2.set(self.username_2.get().lower())

        if username_1 in data_store.players:
            self.name_1.set(data_store.players[username_1].name)

        if username_2 in data_store.players:
            self.name_2.set(data_store.players[username_2].name)

        self.save_button.widget.state(["disabled"])
        self.delete_button.widget.state(["disabled"])
        if username_1 or username_2:
            self.save_button.widget.state(["!disabled"])
            self.delete_button.widget.state(["!disabled"])

    def enable_buttons(self, enable: bool = True) -> None:
        if not enable:
            self.button_frame.enable(False)
            return

        self.button_frame.enable(True)

    def _save_sashes(self) -> None:
        vertical_sashes = [
            self.master_tab.master_frame.sash_coord(index)
            for index in range(VERTICAL_FRAME_COUNT)
        ]
        horizontal_sashes = [
            self.master_tab.chat_panel.sash_coord(index)
            for index in range(HORIZONTAL_FRAME_COUNT)
        ]
        notes_sashes = [
            self.tournament_tab.notes_panel.sash_coord(index)
            for index in range(NOTES_FRAME_COUNT)
        ]

        config = get_config()
        config.update("vertical_sashes", vertical_sashes)
        config.update("horizontal_sashes", horizontal_sashes)
        config.update("notes_sashes", notes_sashes)
        config.save()

    def _on_data_change(self) -> None:
        self.name_1.set(data_store.name_1)
        self.name_2.set(data_store.name_2)
        self.username_1.set(data_store.username_1)
        self.username_2.set(data_store.username_2)

    def _dismiss(self, *args) -> None:
        self._save_sashes()
        self.root.destroy()
