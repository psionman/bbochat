
"""MainFrame for BBO Chat."""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import random
import clipboard

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button
from psiutils.utilities import window_resize

import text

from data import DataStore, Pair, Player
from config import get_config
from constants import MODES

from main_menu import MainMenu
from forms.frm_master import MasterFrame
from forms.frm_partners import PartnerFrame
from forms.frm_notes import NotesFrame

FRAME_TITLE = 'BBO Chat'


class MainFrame():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = get_config()
        self.mode = MODES['greeting']

        self.data_store = DataStore()
        ds = self.data_store
        ds.read()
        self.partners = ds.partners
        self.players = ds.players
        self.pairs = ds.pairs
        self.greetings = ds.greetings
        self.valedictions = ds.valedictions
        self.chat = ds.chat
        self.my_name = ds.my_name

        self.partners_names = sorted(list(self.partners.keys()))
        self.search_pairs = []
        self.pair = []
        self.partner = ''
        if self.config.last_partner:
            self.partner = self.partners[self.config.last_partner]

        # tk variables
        self._create_tk_variables()
        self.username_1.trace_add('write', self._pair_username_change)
        self.username_2.trace_add('write', self._pair_username_change)

        self.button_frame = None
        self.show()

        self.pair_tree = self.master_tab.pair_tree
        self.search_entry = self.master_tab.search_entry

        self._update_mode_colour()
        self._pair_username_change()

    def _create_tk_variables(self) -> None:
        self.clipboard = tk.StringVar()

        # Main
        self.pairs_list = tk.StringVar()
        self.search = tk.StringVar()
        self.username_1 = tk.StringVar()
        self.username_2 = tk.StringVar()
        self.name_1 = tk.StringVar()
        self.name_2 = tk.StringVar()
        self.randomize = tk.BooleanVar(value=self.config.randomize_name_order)

        greeting = self.partner.greeting if self.config.last_partner else ''
        self.greetings_list = tk.StringVar(value=self.greetings)
        self.greeting = tk.StringVar(value=greeting)
        self.valediction = tk.StringVar(value=self.config.last_valediction)
        self.chat_list = tk.StringVar(value=self.chat)
        self.system = tk.StringVar()
        self.chat_line = tk.StringVar()

        # Partners
        self.partners_list = tk.StringVar(value=self.partners_names)
        self.selected_partner = tk.StringVar(value=self.config.last_partner)
        self.partners_name = tk.StringVar(value='')
        self.partners_username = tk.StringVar()

    def show(self):
        root = self.root
        root.protocol("WM_DELETE_WINDOW", self.dismiss)
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(FRAME_TITLE)
        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-g>', self._greeting)
        root.bind('<Control-v>', self._valediction)
        root.bind('<Control-c>', self._chat)
        root.bind('<Control-s>', self.save)
        root.bind('<Configure>',
                  lambda e: window_resize(self, __file__))

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=3,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(4, weight=1)  # Notebook row
        frame.columnconfigure(6, weight=1)

        label = ttk.Label(frame, text='Clipboard')
        label.grid(row=0, column=0, sticky=tk.E)

        self.clipboard_entry = ttk.Entry(frame, textvariable=self.clipboard)
        self.clipboard_entry.grid(row=0, column=1, columnspan=6,
                                  sticky=tk.EW, padx=PAD, pady=PAD)
        self.clipboard_entry.bind('<KeyRelease>', self.copy_to_clipboard)

        button = ttk.Button(frame, text='Copy',
                            command=self.copy_to_clipboard)
        button.grid(row=0, column=7)

        label = ttk.Label(frame, text='Partner')
        label.grid(row=1, column=0, sticky=tk.E)

        entry = ttk.Entry(frame, textvariable=self.partners_username,
                          state='readonly')
        entry.grid(row=1, column=1, sticky=tk.W, padx=PAD)

        label = ttk.Label(frame, text='Opponents')
        label.grid(row=1, column=2)

        entry = ttk.Entry(frame, textvariable=self.username_1)
        entry.grid(row=1, column=3, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.name_1)
        entry.grid(row=2, column=3, pady=PAD)
        entry.bind('<KeyRelease>', self.update_clipboard)

        entry = ttk.Entry(frame, textvariable=self.username_2)
        entry.grid(row=1, column=4, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.name_2)
        entry.grid(row=2, column=4, pady=PAD)
        entry.bind('<KeyRelease>', self.update_clipboard)

        self.save_button = ttk.Button(frame, text=text.SAVE,
                                      command=self._save_names)
        self.save_button.grid(row=1, column=5, padx=PAD)

        self.delete_button = ttk.Button(frame, text=text.DELETE,
                                        command=self._delete_pair)
        self.delete_button.grid(row=2, column=5, padx=PAD)

        check_button = tk.Checkbutton(
            frame,
            text='Randomize opp\'s names order',
            variable=self.randomize)
        check_button.grid(row=1, column=6, rowspan=2, sticky=tk.W)

        notebook = self._get_notebook(frame)
        notebook.grid(row=4, column=0, columnspan=9,
                      sticky=tk.NSEW, padx=PAD)
        return frame

    def _get_notebook(self, master: tk.Frame) -> ttk.Notebook:
        notebook = ttk.Notebook(master)

        self.master_tab = MasterFrame(self, notebook)
        notebook.add(self.master_tab.master_frame, text='Master')

        partners_tab = PartnerFrame(self, notebook)
        notebook.add(partners_tab.partners_frame, text='Partners')

        self.notes_tab = NotesFrame(self, notebook)
        notebook.add(self.notes_tab.notes_frame, text='Notes')

        return notebook

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        style = ttk.Style()
        style.configure('greeting.TButton',
                        background=self.config.colours['greeting'])
        style.configure('valediction.TButton',
                        background=self.config.colours['valediction'])
        style.configure('chat.TButton', background=self.config.colours['chat'])

        frame = ButtonFrame(master, tk.HORIZONTAL)
        buttons = [
            Button(
                frame,
                text=text.EXIT,
                command=self.dismiss,
                sticky=tk.E,
                underline=1),
        ]
        frame.buttons = buttons
        frame.enable(False)
        return frame

    def _greeting(self, *args) -> None:
        self.mode = MODES['greeting']
        self.update_clipboard()

    def _valediction(self, *args) -> None:
        self.mode = MODES['valediction']
        self.update_clipboard()

    def _chat(self, *args) -> None:
        self.mode = MODES['chat']
        self.update_clipboard()

    def save(self, *args) -> None:
        self.data_store.partners = self.partners
        self.data_store.players = self.players
        self.data_store.pairs = self.pairs
        self.data_store.greetings = self.greetings
        self.data_store.valedictions = self.valedictions
        self.data_store.chat = self.chat
        self.data_store.my_name = self.my_name
        self.data_store.save()
        self.enable_buttons(False)

    def _update_mode_colour(self) -> None:
        colour = self.config.colours[MODES[self.mode]]
        entry_style = ttk.Style()
        entry_style.configure(
            'style.TEntry',
            fieldbackground=colour,
            )
        self.clipboard_entry.configure(style='style.TEntry')

    def update_clipboard(self, *args) -> None:
        if not self.partner:
            return

        self._update_mode_colour()
        opps = self._get_opps()
        names = f'{self.partner.name} and {self.my_name}'

        if self.mode == MODES['greeting']:
            message = self.greeting.get()
        elif self.mode == MODES['valediction']:
            message = self.valediction.get()
        elif self.mode == MODES['chat']:
            message = self.chat_line.get()

        message = message.replace('<opps>', opps)
        message = message.replace('<names>', names)
        message = message.replace('<system>', self.partner.system)
        self.clipboard.set(message)
        self.copy_to_clipboard()

    def copy_to_clipboard(self, *args) -> None:
        clipboard.copy(self.clipboard.get())

    def _get_opps(self) -> str:
        opp_1, opp_2 = self.name_1.get(), self.name_2.get()
        if self.randomize.get():
            opps = [self.name_1.get(), self.name_2.get()]
            choice = random.choice([0, 1])
            opp_1 = opps[choice]
            choice = (choice + 1) % 2
            opp_2 = opps[choice]
        if opp_1:
            return f'{opp_1} and {opp_2}' if opp_2 else opp_1
        return opp_2

    def _save_names(self, *args) -> None:
        name_1 = self.name_1.get()
        name_2 = self.name_2.get()
        username_1 = self.username_1.get()
        username_2 = self.username_2.get()

        pair = Pair(username_1, username_2)
        self.players[username_1] = Player(name_1, username_1)
        self.players[username_2] = Player(name_2, username_2)
        if pair not in self.pairs:
            self.pairs.append(Pair(username_1, username_2))

        self.save()
        self.search.set('')
        self.pair_tree.delete(*self.pair_tree.get_children())
        self.search.set(self.username_1.get())
        self.master_tab.name_search()
        self.search_entry.focus_set()
        self.update_clipboard()

    def _delete_pair(self, *args) -> None:
        response = messagebox.askyesno(
            'Delete pair',
            'Are you sure you wish to delete this pair?',
            parent=self.root,
        )
        if not response:
            return

        pair = Pair(self.username_1.get(), self.username_2.get())
        self.pairs.remove(pair)
        self.save()

        self.name_1.set('')
        self.name_2.set('')
        self.username_1.set('')
        self.username_2.set('')
        self._pair_username_change()
        self.search.set('')
        self.pair_tree.delete(*self.pair_tree.get_children())
        self.search_entry.focus_set()

    def _pair_username_change(self, *args) -> None:
        username_1 = self.username_1.get().lower()
        username_2 = self.username_2.get().lower()
        self.username_1.set(username_1)
        self.username_2.set(username_2)

        if username_1 in self.players:
            self.name_1.set(self.players[username_1].name)

        if username_2 in self.players:
            self.name_2.set(self.players[username_2].name)

        self.save_button.state(['disabled'])
        self.delete_button.state(['disabled'])
        if username_1 or username_2:
            self.save_button.state(['!disabled'])
            self.delete_button.state(['!disabled'])

    def enable_buttons(self, enable: bool = True) -> None:
        if not self.button_frame:
            return
        if not enable:
            self.button_frame.enable(False)
            return

        if self.button_frame.enabled is True:
            return
        self.button_frame.enable(True)

    def _save_sashes(self) -> None:
        vertical_sashes = [self.master_tab.master_frame.sash_coord(index)
                           for index in range(3)]
        horizontal_sashes = [
            self.master_tab.chat_panel.sash_coord(index)
            for index in range(1)]

        self.config.update('vertical_sashes', vertical_sashes)
        self.config.update('horizontal_sashes', horizontal_sashes)
        self.config.save()

    def dismiss(self, *args) -> None:
        self._save_sashes()
        self.root.destroy()
