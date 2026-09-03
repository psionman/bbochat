import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from tkinter.colorchooser import askcolor

from psiutils import messagebox
from psiutils.buttons import IconButton
from psiutils.constants import PAD, PADT, Status
from psiutils.utilities import window_resize
from psiutils.widgets import separator_frame
from tkinterweb import HtmlFrame

from bbochat.buttons import ButtonFrame
from bbochat.config import config, get_config
from bbochat.constants import HTML_TEST, ICON_DIR, ChatMode
from bbochat.forms.frm_config_css import ConfigCssFrame
from bbochat.text import Text
from bbochat.utilities import display_html

txt = Text()


class ColourLabel(ttk.Label):
    def __init__(self, *args, **kwargs):
        self.colour = ""
        if "colour" in kwargs:
            self.colour = kwargs["colour"]
            kwargs.pop("colour")
        super().__init__(*args, **kwargs)


class ConfigFrame:
    """ConfigFrame for BBO Chat."""

    def __init__(self, parent) -> None:
        self.root = tk.Toplevel(parent.root)
        self.colours = dict(config.colours)
        self.css = config.css
        self.css_element = None
        self.style = ttk.Style()

        self.button_frame = None
        self.greeting_entry = None
        self.valediction_entry = None
        self.chat_entry = None
        self.html_frame = None

        # tk variables
        self.data_directory = tk.StringVar(value=config.data_directory)
        self.confirm_history_delete = tk.BooleanVar(
            value=config.confirm_history_delete
        )
        self.randomize_name_order = tk.BooleanVar(
            value=config.randomize_name_order
        )
        self.show_tooltips = tk.BooleanVar(value=config.show_tooltips)
        self.tournament_notes_directory = tk.StringVar(
            value=config.tournament_notes_directory
        )

        # Colour items
        for chat_mode in ChatMode.__members__.values():
            colour = config.colours.get(str(chat_mode.value), "#000000")
            setattr(self, chat_mode.name, tk.StringVar(value=colour))
            setattr(self, f"{chat_mode.name}_original", colour)

        self.data_directory.trace_add("write", self._check_value_changed)
        self.tournament_notes_directory.trace_add(
            "write", self._check_value_changed
        )
        self.randomize_name_order.trace_add("write", self._check_value_changed)
        self.confirm_history_delete.trace_add(
            "write", self._check_value_changed
        )
        self.show_tooltips.trace_add("write", self._check_value_changed)

        self.colour_entries = {}
        self._show()
        self._update_mode_colours()

        self.display_html()

    def _show(self) -> None:
        root = self.root
        root.geometry(config.geometry[Path(__file__).stem])
        root.title(txt.CONFIG)

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-s>", self._save_config)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

        self.root.update_idletasks()
        root.bind(
            "<Configure>", lambda e: window_resize(root, __file__, config)
        )

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(3, weight=1)

        row = 0
        separator = separator_frame(frame, "Options")
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        check_button = ttk.Checkbutton(
            frame,
            text="Confirm history delete",
            variable=self.confirm_history_delete,
        )
        check_button.grid(row=row, column=1, columnspan=4, sticky=tk.W)

        row += 1
        check_button = ttk.Checkbutton(
            frame,
            text="Randomize opp's name order",
            variable=self.randomize_name_order,
        )
        check_button.grid(row=row, column=1, columnspan=4, sticky=tk.W)

        row += 1
        check_button = ttk.Checkbutton(
            frame, text="Show tootips", variable=self.show_tooltips
        )
        check_button.grid(row=row, column=1, sticky=tk.W)

        row += 1
        separator = separator_frame(frame, "Colours")
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        for mode in ChatMode:
            self._add_colour_widgets(frame, row, mode)
            row += 1

        row += 1
        separator = separator_frame(frame, "css")
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        self.html_frame = HtmlFrame(frame, messages_enabled=False, height=200)
        self.html_frame.grid(row=row, column=1, columnspan=3, sticky=tk.EW)
        # self.html_frame.grid_propagate(0)

        button = IconButton(frame, txt.EDIT, "edit", self._css_edit)
        button.grid(row=row, column=4, sticky=tk.N, padx=PAD)

        row += 1
        separator = separator_frame(frame, "File locations")
        separator.grid(row=row, column=0, columnspan=5, sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text="Data directory")
        label.grid(row=row, column=0, sticky=tk.E, pady=PADT)

        entry = ttk.Entry(frame, textvariable=self.data_directory)
        entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=PADT)

        button = ttk.Button(
            frame, text="...", command=self._get_data_directory
        )
        button.grid(row=row, column=4, padx=PAD, pady=PADT)

        row += 1
        label = ttk.Label(frame, text="Tournament notes directory")
        label.grid(row=row, column=0, sticky=tk.E, pady=PADT)

        entry = ttk.Entry(frame, textvariable=self.tournament_notes_directory)
        entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=PADT)

        button = ttk.Button(
            frame, text="...", command=self._get_partner_notes_directory
        )
        button.grid(row=row, column=4, padx=PAD, pady=PADT)

        return frame

    def _add_colour_widgets(
        self, frame: tk.Frame, row: int, mode: ChatMode
    ) -> None:
        colour_key = mode.name
        label = ttk.Label(frame, text=mode.name.capitalize())
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(
            frame, textvariable=getattr(self, colour_key), width=10
        )
        entry.grid(row=row, column=1, sticky=tk.EW)
        self.colour_entries[str(mode.value)] = entry

        colour = getattr(self, colour_key).get()
        self.style.configure(f"{colour}.TLabel", background=colour)

        button = IconButton(
            frame,
            txt.SELECT,
            "palette",
            lambda k=mode: self._get_color(k),
            icon_path=ICON_DIR,
        )
        button.grid(row=row, column=3, padx=PAD, pady=(0, 5), sticky=tk.W)

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = self._frame_buttons(frame)
        frame.enable(False)
        return frame

    def _frame_buttons(self, frame: ButtonFrame) -> tk.Frame:
        return [
            frame.icon_button("save", self._save_config, True),
            frame.icon_button("revert", self._restore_defaults, True),
            frame.icon_button("exit", self._dismiss),
        ]

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
        name_order = config.randomize_name_order
        notes_directory = config.tournament_notes_directory
        confirm_delete = config.confirm_history_delete
        return (
            self.data_directory.get() != config.data_directory
            or self.tournament_notes_directory.get() != notes_directory
            or self.confirm_history_delete.get() != confirm_delete
            or self.randomize_name_order.get() != name_order
            or self.show_tooltips.get() != config.show_tooltips
            or self.colours != config.colours
            or self.css != config.css
        )

    def _get_color(self, mode: str) -> None:
        colour = askcolor(
            parent=self.root,
            initialcolor=self.colours[str(mode.value)],
            title=f"{mode.name.capitalize()} colour",
        )
        if colour[1]:
            self.colours[mode.value] = colour[1]
            self._update_mode_colours()
            self._check_value_changed()

    def _update_mode_colours(self) -> None:
        for mode, entry in self.colour_entries.items():
            self._update_mode_colour(mode, entry)

    def _update_mode_colour(self, mode: int, entry: ttk.Entry) -> None:
        colour = self.colours[mode]
        key = ChatMode(int(mode)).name
        entry_style = ttk.Style(self.root)
        entry_style.configure(
            f"style_{key}.TEntry",
            fieldbackground=colour,
        )
        entry.configure(style=f"style_{key}.TEntry")

    def _check_value_changed(self, *args) -> None:
        enable = bool(self._value_changed())
        self.button_frame.enable(enable)

    def _save_config(self, *args) -> None:
        name_order = self.randomize_name_order.get()
        confirm_delete = self.confirm_history_delete.get()
        config.update("data_directory", self.data_directory.get())
        config.update(
            "tournament_notes_directory", self.tournament_notes_directory.get()
        )
        config.update("randomize_name_order", name_order)
        config.update("confirm_history_delete", confirm_delete)
        config.update("show_tooltips", self.show_tooltips.get())
        config.update("colours", dict(self.colours))
        config.update("css", dict(self.css))
        config.save()
        # config = get_config()
        self._dismiss()

    def display_html(self) -> None:
        display_html(self.html_frame, HTML_TEST, self.css)

    def _css_edit(self) -> None:
        dlg = ConfigCssFrame(self)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.status != Status.OK:
            return

        self.css_element = dlg.element.get()
        self.css = dlg.css
        self.display_html()
        self._check_value_changed()

    def _restore_defaults(self, *args) -> None:
        message = " Restore defaults (cannot undo)?"
        # TODO implement this
        if messagebox.askyesno(
            self, title="Restore defaults", message=message
        ):
            config = get_config(restore_defaults=True)
        self.colours = dict(config.colours)
        self.css = config.css

        self.data_directory.set(config.data_directory)
        self.randomize_name_order.set(config.randomize_name_order)
        self.show_tooltips.set(config.show_tooltips)
        self.tournament_notes_directory.set(config.tournament_notes_directory)
        self.confirm_history_delete.set(config.confirm_history_delete)

        self._update_mode_colours()
        # self.display_html()

    def _dismiss(self, *args) -> None:
        self.root.grab_release()
        self.root.destroy()
