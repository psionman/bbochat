"""MainFrame for BBO Chat."""

import contextlib
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import clipboard
from psiutils import messagebox
from psiutils.buttons import IconButton
from psiutils.constants import PAD
from psiutils.utilities import window_resize

from bbochat.buttons import ButtonFrame
from bbochat.config import config
from bbochat.constants import ChatMode
from bbochat.data_store import data_store
from bbochat.forms.frm_master import MasterFrame
from bbochat.forms.frm_notes import NotesFrame
from bbochat.forms.frm_partners import PartnerFrame
from bbochat.forms.frm_tournament import TournamentFrame
from bbochat.main_menu import MainMenu
from bbochat.message import message_store
from bbochat.pair import PairNew
from bbochat.player import Player
from bbochat.text import Text
from bbochat.utilities import get_my_name

txt = Text()
FRAME_TITLE = "BBO Chat"

DEFAULT_MODE = ChatMode.GREETINGS

VERTICAL_FRAME_COUNT = 4
HORIZONTAL_FRAME_COUNT = 1
NOTES_FRAME_COUNT = 1

# Handles cases when size gets corrupted, e.g. after stop on error
DEFAULT_GEOMETRY = "1250x700"


class AppFrame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = None  # Used to save sashes (see self._dismiss)
        config.subscribe(self._on_config_change)
        self.mode = ChatMode.GREETINGS

        data_store.subscribe(self._on_data_change)
        self.data_server = data_store
        message_store.my_name = data_store.my_name

        self.pair = []

        self.partner = None
        self.partners = data_store.partners
        self.partners_names = sorted(list(self.partners.keys()))

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
        message_store.randomize = config.randomize_name_order
        message_store.subscribe(self._chat_message_publish)
        self.last_message = ""

        if config.last_partner and config.last_partner in self.partners:
            self.partner = self.partners[config.last_partner]
            message_store.partner = self.partner
            message_store.selected_messages[ChatMode.GREETINGS] = (
                self.partner.greeting
            )

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
        # self.greetings_list = tk.StringVar(value=data_store.greetings)
        self.valediction = tk.StringVar(value=config.last_valediction)
        # self.chat_list = tk.StringVar(value=data_store.chat)
        self.system = tk.StringVar()
        self.chat_line = tk.StringVar()

        # Partners
        self.partners_list = tk.StringVar(value=self.partners_names)
        self.selected_partner = tk.StringVar(value=config.last_partner)
        self.my_name_text = tk.StringVar(value=data_store.my_name)
        self.partners_name = tk.StringVar(value="")
        self.partners_username = tk.StringVar()

    def _show(self):
        root = self.root
        root.protocol("WM_DELETE_WINDOW", self._dismiss)
        root.geometry(config.geometry[Path(__file__).stem])
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
        self._bind_window_events()
        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _bind_window_events(self):
        self.root.update_idletasks()
        root = self.root
        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-g>", self._greeting)
        root.bind("<Control-v>", self._valediction)
        root.bind("<Control-c>", self._chat)
        root.bind(
            "<Configure>", lambda e: window_resize(root, __file__, config)
        )

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
            frame,
            text="Randomize opp's names order",
            variable=self.randomize,
            command=self._on_randomize_change,
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
        get_my_name()

    def _on_config_change(self, *args):
        self.randomize.set(config.randomize_name_order)
        message_store.randomize = config.randomize_name_order
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

    def _chat_message_publish(self) -> None:
        self.my_name_text.set(message_store.my_name)
        self.partner = message_store.partner
        self.partners_username.set(
            f"{self.partner.username}, {self.partner.name}"
        )

        if message_store.pair:
            self.username_1.set(message_store.pair.player_1.username)
            self.username_2.set(message_store.pair.player_2.username)

        if self.last_message != message_store.message:
            # input(
            #     f"Message changed from {self.last_message} to {message_store.message}"
            # )
            message = message_store.output_message()
            self.update_clipboard(message, message_store.mode)
            self.clipboard.set(message)
        self.last_message = message_store.message

    def update_clipboard(
        self, message: str = "", mode: int = None, *args
    ) -> None:
        if mode is None:
            mode = DEFAULT_MODE
        self.mode = mode
        self._set_clipboard_colour()

    def copy_to_clipboard(self, *args) -> None:
        clipboard.copy(self.clipboard.get())

    def _save_names(self, *args) -> None:
        name_1 = self.name_1.get()
        name_2 = self.name_2.get()
        username_1 = self.username_1.get()
        username_2 = self.username_2.get()

        player_1 = Player(name_1, username_1)
        player_2 = Player(name_2, username_2)
        pair = PairNew(player_1, player_2)
        data_store.players[username_1] = player_1
        data_store.players[username_2] = player_2
        if pair not in data_store.pairs:
            data_store.pairs.append(pair)

        self.save()
        # self.search.set("")
        self.pair_tree.delete(*self.pair_tree.get_children())
        # self.search.set(self.username_1.get())
        self.search_entry.focus_set()
        self.master_tab.opponents_frame.name_search()
        message_store.pair = pair
        self.update_clipboard()

    def _delete_pair(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_PAIR):
            return

        pair = PairNew(
            data_store.players[self.username_1.get()],
            data_store.players[self.username_2.get()],
        )
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

    def _on_randomize_change(self) -> None:
        message_store.randomize = self.randomize.get()

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
        config.update("vertical_sashes", vertical_sashes)
        config.update("horizontal_sashes", horizontal_sashes)
        config.update("notes_sashes", notes_sashes)
        config.save()
        self.config = config

    def _on_data_change(self) -> None:
        # self.name_1.set(data_store.player_1.name)
        # self.name_2.set(data_store.player_2.name)
        # self.username_1.set(data_store.player_1.username)
        # self.username_2.set(data_store.player_2.username)
        pass

    def _dismiss(self, *args) -> None:
        # if self.tournament_tab.notes_changed():
        #     response = tk.messagebox.askyesno(
        #         "Save Notes",
        #         "Do you want to save the board notes?",
        #     )
        #     if response:
        #         self.tournament_tab.save_notes()
        self._save_sashes()
        self.root.destroy()
        # Need to do this because window_resize is called in close
        self.config.save()
