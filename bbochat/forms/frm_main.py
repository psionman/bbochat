
"""MainFrame for BBO Chat."""
import tkinter as tk
from tkinter import ttk, messagebox
import random
import clipboard

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button, HORIZONTAL
from psiutils.widgets import display_icon

from constants import ICON_FILE
import text

from data import DataStore, Pair, Player
from config import config
from constants import MODES, MODE_COLOURS

from main_menu import MainMenu
from forms.frm_master import MasterFrame
from forms.frm_partners import PartnerFrame

GEOMETRY = '1300x800'
FRAME_TITLE = 'BBO Chat'


class MainFrame():
    def __init__(self, parent):
        self.root = parent.root
        self.parent = parent
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

        self.partners_names = sorted([name for name in self.partners.keys()])
        self.search_pairs = []
        self.pair = []
        self.partner = self.partners[config.last_partner]

        # tk variables
        self.clipboard = tk.StringVar()

        # Main
        self.pairs_list = tk.StringVar()
        self.search = tk.StringVar()
        self.username_1 = tk.StringVar()
        self.username_2 = tk.StringVar()
        self.name_1 = tk.StringVar()
        self.name_2 = tk.StringVar()
        self.username_1.trace_add('write', self._pair_username_change)
        self.username_2.trace_add('write', self._pair_username_change)

        self.greetings_list = tk.StringVar(value=self.greetings)
        self.greeting = tk.StringVar(value=config.last_greeting)
        self.valedictions_list = tk.StringVar(value=self.valedictions)
        self.valediction = tk.StringVar(value=config.last_valediction)
        self.chat_list = tk.StringVar(value=self.chat)
        self.system = tk.StringVar()
        self.chat_line = tk.StringVar()

        # Partners
        self.partners_list = tk.StringVar(value=self.partners_names)
        self.selected_partner = tk.StringVar(value=config.last_partner)
        self.partners_username = tk.StringVar()

        self.button_frame = None
        self.show()

        self._update_mode_colour()
        self._pair_username_change()

    def show(self):
        root = self.root
        root.geometry(GEOMETRY)
        root.title(FRAME_TITLE)
        display_icon(root, ICON_FILE)
        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-g>', self._greeting)
        root.bind('<Control-v>', self._valediction)
        root.bind('<Control-c>', self._chat)
        root.bind('<Control-s>', self._save)

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(3, weight=1)  # Notebook row
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

        notebook = self._get_notebook(frame)
        notebook.grid(row=3, column=0, columnspan=9,
                      sticky=tk.NSEW, padx=PAD, pady=PAD)
        return frame

    def _get_notebook(self, master: tk.Frame) -> ttk.Notebook:
        notebook = ttk.Notebook(master)

        master = MasterFrame(self, notebook)
        self.pair_tree = master.pair_tree
        self.search_entry = master.search_entry
        notebook.add(master.master_frame, text='Master')

        partners = PartnerFrame(self, notebook)
        notebook.add(partners.partners_frame, text='Partners')

        # tab = self._get_partner_tab(notebook)
        # notebook.add(tab, text='Systems')

        # tab = self._get_partner_tab(notebook)
        # notebook.add(tab, text='Maintenance')

        return notebook

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        buttons = [
            Button('Greeting', self._greeting, underline=0),
            Button('Valediction', self._valediction, underline=0),
            Button('Chat', self._chat, underline=0),
            Button(text.SAVE, self._save, underline=0, dimmable=True),
            Button(text.EXIT, self.dismiss, tk.E, underline=1),
        ]
        frame = ButtonFrame(master, buttons, HORIZONTAL)
        frame.enable(False)
        return frame

    def _greeting(self, event: object = None) -> None:
        self.mode = MODES['greeting']
        self.update_clipboard()

    def _valediction(self, event: object = None) -> None:
        self.mode = MODES['valediction']
        self.update_clipboard()

    def _chat(self, event: object = None) -> None:
        self.mode = MODES['chat']
        self.update_clipboard()

    def _save(self, event: object = None) -> None:
        self.data_store.partners = self.partners
        self.data_store.players = self.players
        self.data_store.pairs = self.pairs
        self.data_store.greetings = self.greetings
        self.data_store.valedictions = self.valedictions
        self.data_store.chat = self.chat
        self.data_store.my_name = self.my_name
        # data = {
        #     'partners': self.partners,
        #     'players': self.players,
        #     'pairs': self.pairs,
        #     'greetings': self.greetings,
        #     'valedictions': self.valedictions,
        #     'my_name': self.my_name,
        #     'chat': self.chat,
        # }
        # save_data(data)
        self.data_store.save()
        self.enable_buttons(False)

    def _update_mode_colour(self) -> None:
        colour = MODE_COLOURS[self.mode]
        entry_style = ttk.Style()
        entry_style.configure(
            'style.TEntry',
            fieldbackground=colour,
            )
        self.clipboard_entry.configure(style='style.TEntry')

    def update_clipboard(self, event: object = None) -> None:
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

    def copy_to_clipboard(self, event: object = None) -> None:
        clipboard.copy(self.clipboard.get())

    def _get_opps(self) -> str:
        opps = [self.name_1.get(), self.name_2.get()]
        choice = random.choice([0, 1])
        opp_1 = opps[choice]
        choice = (choice + 1) % 2
        opp_2 = opps[choice]
        if opp_1 and opp_2:
            return f'{opp_1} and {opp_2}'
        if opp_1:
            return opp_1
        return opp_2

    def _save_names(self, event: object = None) -> None:
        name_1 = self.name_1.get()
        name_2 = self.name_2.get()
        username_1 = self.username_1.get()
        username_2 = self.username_2.get()

        pair = Pair(username_1, username_2)
        self.players[username_1] = Player(name_1, username_1)
        self.players[username_2] = Player(name_2, username_2)
        if pair not in self.pairs:
            self.pairs.append(Pair(username_1, username_2))

        self._save()
        self.search.set('')
        self.pair_tree.delete(*self.pair_tree.get_children())
        self.search_entry.focus_set()

    def _delete_pair(self, event: object = None) -> None:
        response = messagebox.askyesno(
            'Delete pair',
            'Are you sure you wish to delete this pair?',
            parent=self.root,
        )
        if not response:
            return

        pair = Pair(self.username_1.get(), self.username_2.get())
        self.pairs.remove(pair)
        self._save()

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
        if enable is False:
            self.button_frame.enable(False)
            return

        if self.button_frame.enabled is True:
            return
        self.button_frame.enable(True)

    def dismiss(self, event: object = None) -> None:
        self.root.destroy()
