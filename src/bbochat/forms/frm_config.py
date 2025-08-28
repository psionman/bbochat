
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.colorchooser import askcolor
from tkinterweb import HtmlFrame

from psiutils.buttons import ButtonFrame, IconButton
from psiutils.widgets import separator_frame
from psiutils.constants import PAD, PADT, Pad, DIALOG_STATUS
from psiutils.utilities import window_resize
from psiutils import messagebox

from bbochat.config import get_config
from bbochat.utilities_bbochat import display_html
from bbochat.constants import HTML_TEST
import bbochat.text as txt

from bbochat.forms.frm_config_css import ConfigCssFrame


class ConfigFrame():
    """ConfigFrame for BBO Chat."""
    def __init__(self, parent):
        # pylint: disable=no-member)
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = get_config()
        self.colours = dict(self.config.colours)
        self.css = self.config.css
        self.css_element = None

        self.button_frame = None
        self.greeting_entry = None
        self.valediction_entry = None
        self.chat_entry = None
        self.html_frame = None

        # tk variables
        self.data_directory = tk.StringVar(value=self.config.data_directory)
        self.randomize_name_order = tk.BooleanVar(
            value=self.config.randomize_name_order)
        self.show_tooltips = tk.BooleanVar(value=self.config.show_tooltips)
        self.tournament_notes_directory = tk.StringVar(
            value=self.config.tournament_notes_directory)

        self.data_directory.trace_add('write', self._check_value_changed)
        self.tournament_notes_directory.trace_add(
            'write', self._check_value_changed)
        self.randomize_name_order.trace_add('write', self._check_value_changed)
        self.show_tooltips.trace_add('write', self._check_value_changed)

        self._show()

        self.colour_entries = {
            'greeting': self.greeting_entry,
            'valediction': self.valediction_entry,
            'chat': self.chat_entry,
        }
        self._update_mode_colours()

        self.display_html()

    def _show(self) -> None:
        # pylint: disable=no-member)
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(txt.CONFIG)
        root.transient(self.parent.root)

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-s>', self._save_config)
        root.bind('<Configure>',
                  lambda e: window_resize(self, __file__))

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, padx=0, sticky=tk.NSEW)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        main_frame = self._main_frame(frame)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(frame)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(3, weight=1)

        row = 0
        separator = separator_frame(frame, 'Options')
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        check_button = ttk.Checkbutton(
            frame, text='Randomize opp\'s name order',
            variable=self.randomize_name_order)
        check_button.grid(row=row, column=1, sticky=tk.W)

        row += 1
        check_button = ttk.Checkbutton(
            frame, text='Show tootips',
            variable=self.show_tooltips)
        check_button.grid(row=row, column=1, sticky=tk.W)

        row += 1
        separator = separator_frame(frame, 'Colours')
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Greeting')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)
        self.greeting_entry = ttk.Entry(frame)
        self.greeting_entry.grid(row=row, column=1,
                                 sticky=tk.EW, padx=PAD, pady=PAD)
        button = ttk.Button(frame, text=txt.ELLIPSIS)
        button.grid(row=row, column=2, padx=Pad.W)
        button.bind('<Button-1>',
                    lambda e: self._ask_colour('greeting'))

        row += 1
        label = ttk.Label(frame, text='Valediction')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)
        self.valediction_entry = ttk.Entry(frame)
        self.valediction_entry.grid(row=row, column=1,
                                    sticky=tk.EW, padx=PAD, pady=PAD)

        button = ttk.Button(frame, text=txt.ELLIPSIS)
        button.grid(row=row, column=2, padx=Pad.W)
        button.bind('<Button-1>',
                    lambda e: self._ask_colour('valediction'))

        row += 1
        label = ttk.Label(frame, text='Chat')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)
        self.chat_entry = ttk.Entry(frame)
        self.chat_entry.grid(row=row, column=1,
                             sticky=tk.EW, padx=PAD, pady=PAD)
        button = ttk.Button(frame, text=txt.ELLIPSIS)
        button.grid(row=row, column=2, padx=Pad.W)

        button = ttk.Button(frame, text=txt.ELLIPSIS)
        button.grid(row=row, column=2, padx=Pad.W)
        button.bind('<Button-1>',
                    lambda e: self._ask_colour('chat'))

        row += 1
        separator = separator_frame(frame, 'css')
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        self.html_frame = HtmlFrame(frame, messages_enabled=False, height=200)
        self.html_frame.grid(row=row, column=1, columnspan=3, sticky=tk.EW)
        self.html_frame.grid_propagate(0)

        button = IconButton(frame, txt.EDIT, 'edit', False, self._css_edit)
        button.grid(row=row, column=4, sticky=tk.N, padx=PAD)

        row += 1
        separator = separator_frame(frame, 'File locations')
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Data directory')
        label.grid(row=row, column=0, sticky=tk.E, pady=PADT)

        entry = ttk.Entry(frame, textvariable=self.data_directory)
        entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=PADT)
        # self.root.after(1, lambda: entry.focus_force())

        button = ttk.Button(frame, text='...',
                            command=self._get_data_directory)
        button.grid(row=row, column=4, padx=PAD, pady=PADT)

        row += 1
        label = ttk.Label(frame, text='Tournament notes directory')
        label.grid(row=row, column=0, sticky=tk.E, pady=PADT)

        entry = ttk.Entry(frame, textvariable=self.tournament_notes_directory)
        entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=PADT)

        button = ttk.Button(frame, text='...',
                            command=self._get_partner_notes_directory)
        button.grid(row=row, column=4, padx=PAD, pady=PADT)

        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('save', True, self._save_config),
            frame.icon_button('revert', True, self._restore_defaults),
            frame.icon_button('exit', False, self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _get_data_directory(self) -> str:
        """Return a directory."""
        original_directory = self.data_directory.get()
        directory = filedialog.askdirectory(
            initialdir=original_directory,
            parent=self.root,
        )
        self.data_directory.set(directory)
        return directory

    def _get_partner_notes_directory(self) -> str:
        """Return a directory."""
        original_directory = self.tournament_notes_directory.get()
        directory = filedialog.askdirectory(
            initialdir=original_directory,
            parent=self.root,
        )
        self.tournament_notes_directory.set(directory)
        return directory

    def _value_changed(self) -> bool:
        # pylint: disable=no-member)
        name_order = self.config.randomize_name_order
        notes_directory = self.config.tournament_notes_directory
        return (
            self.data_directory.get() != self.config.data_directory
            or self.tournament_notes_directory.get() != notes_directory
            or self.randomize_name_order.get() != name_order
            or self.show_tooltips.get() != self.config.show_tooltips
            or self.colours != self.config.colours
            or self.css != self.config.css
        )

    def _ask_colour(self, mode: str) -> None:
        colour = askcolor(
            initialcolor=self.colours[mode],
            title=f'{mode.capitalize()} colour',)
        if colour[1]:
            self.colours[mode] = colour[1]
            self._update_mode_colours()
            self._check_value_changed()

    def _update_mode_colours(self) -> None:
        for mode, entry in self.colour_entries.items():
            self._update_mode_colour(mode, entry)

    def _update_mode_colour(self, mode: str, entry: ttk.Entry) -> None:
        colour = self.colours[mode]
        entry_style = ttk.Style()
        entry_style.configure(
            f'style_{mode}.TEntry',
            fieldbackground=colour,
            )
        entry.configure(style=f'style_{mode}.TEntry')

    def _check_value_changed(self, *args) -> None:
        enable = bool(self._value_changed())
        self.button_frame.enable(enable)

    def _save_config(self, *args) -> None:
        name_order = self.randomize_name_order.get()
        self.config.update('data_directory', self.data_directory.get())
        self.config.update(
            'tournament_notes_directory', self.tournament_notes_directory.get())
        self.config.update('randomize_name_order', name_order)
        self.config.update('show_tooltips', self.show_tooltips.get())
        self.config.update('colours', dict(self.colours))
        self.config.update('css', dict(self.css))
        self.config.save()
        self.config = get_config()
        self._dismiss()

    def display_html(self) -> None:
        display_html(self.html_frame, HTML_TEST, self.css)

    def _css_edit(self) -> None:
        dlg = ConfigCssFrame(self)
        self.root.wait_window(dlg.root)
        if dlg.status != DIALOG_STATUS['ok']:
            return

        self.css_element = dlg.element.get()
        self.css = dlg.css
        self.display_html()
        self._check_value_changed()

    def _restore_defaults(self, *args) -> None:
        # pylint: disable=no-member)
        message = ' Restore defaults (cannot undo)?'
        if messagebox.askyesno(
                self, title='Restore defaults', message=message):
            self.config = get_config(restore_defaults=True)
        self.colours = dict(self.config.colours)
        self.css = self.config.css

        self.data_directory.set(self.config.data_directory)
        self.randomize_name_order.set(self.config.randomize_name_order)
        self.show_tooltips.set(self.config.show_tooltips)
        self.tournament_notes_directory.set(
            self.config.tournament_notes_directory)

        self._update_mode_colours()
        self.display_html()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
