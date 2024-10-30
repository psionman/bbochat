
import tkinter as tk
from tkinter import ttk, filedialog

from psiutils.buttons import ButtonFrame, Button, HORIZONTAL, enable_buttons
from psiutils.constants import PAD, PADT

from constants import ICON_FILE
from config import get_config, save_config
import text

GEOMETRY = '700x300'

# DEFAULT_CONFIG = {
#     'data_directory': USER_DATA_DIR,
#     'last_partner': 'eirikr',
#     'last_greeting': 'Hi <opps>: <names>: <system>',
#     'last_valediction': 'Thanks both',
#     'randomize_name_order': True,
# }


class ConfigFrame():
    """ConfigFrame for <application>."""
    def __init__(self, parent):
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = get_config()

        # tk variables
        self.data_directory = tk.StringVar(value=self.config.data_directory)
        self.randomize_name_order = tk.BooleanVar(
            value=self.config.randomize_name_order)
        self.notes_path = tk.StringVar(value=self.config.notes_path)

        self.data_directory.trace_add('write', self._check_value_changed)
        self.notes_path.trace_add('write', self._check_value_changed)
        self.randomize_name_order.trace_add('write', self._check_value_changed)

        self.show()

    def show(self) -> None:
        root = self.root
        root.geometry(GEOMETRY)
        root.title(text.CONFIG)
        root.iconphoto(False, tk.PhotoImage(file=ICON_FILE))
        root.wait_visibility()
        root.grab_set()
        root.transient(self.parent.root)

        root.rowconfigure(1, weight=1)
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
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        label = ttk.Label(frame, text='Data directory')
        label.grid(row=0, column=0, sticky=tk.E, pady=PADT)

        entry = ttk.Entry(frame, textvariable=self.data_directory)
        entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=PADT)
        self.root.after(1, lambda: entry.focus_force())

        button = ttk.Button(frame, text='...',
                            command=self._get_data_directory)
        button.grid(row=0, column=3, padx=PAD, pady=PADT)

        label = ttk.Label(frame, text='Notes directory')
        label.grid(row=1, column=0, sticky=tk.E, pady=PADT)

        entry = ttk.Entry(frame, textvariable=self.notes_path)
        entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=PADT)

        button = ttk.Button(frame, text='...',
                            command=self._get_notes_directory)
        button.grid(row=1, column=3, padx=PAD, pady=PADT)

        check_button = tk.Checkbutton(frame, text='Randomize opp\'s names',
                                      variable=self.randomize_name_order)
        check_button.grid(row=2, column=1, sticky=tk.W)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        self.buttons = [
            Button([text.SAVE], self._save_config, underline=0, dimmable=True),
            Button(text.EXIT, self.dismiss, tk.E, underline=1),
        ]
        frame = ButtonFrame(master, self.buttons, HORIZONTAL)
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

    def _get_notes_directory(self) -> str:
        """Return a directory."""
        original_directory = self.notes_path.get()
        directory = filedialog.askdirectory(
            initialdir=original_directory,
            parent=self.root,
        )
        self.notes_path.set(directory)
        return directory

    def _value_changed(self) -> bool:
        name_order = self.config.randomize_name_order
        return (
            self.data_directory.get() != self.config.data_directory
            or self.notes_path.get() != self.config.notes_path
            or self.randomize_name_order.get() != name_order
        )

    def _check_value_changed(self, *args) -> None:
        enable = False
        if self._value_changed():
            enable = True
        enable_buttons(self.buttons, enable)

    def _save_config(self, *args) -> None:
        name_order = self.randomize_name_order.get()
        self.config.config['data_directory'] = self.data_directory.get()
        self.config.config['notes_path'] = self.notes_path.get()
        self.config.config['randomize_name_order'] = name_order
        save_config(self.config)
        self.dismiss()

    def dismiss(self, *args) -> None:
        self.root.destroy()
