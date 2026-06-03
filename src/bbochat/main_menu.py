import tkinter as tk
import webbrowser
from tkinter import simpledialog

from psiutils import messagebox
from psiutils.menus import Menu, MenuItem

from bbochat._version import __version__
from bbochat.config import config
from bbochat.constants import APP_TITLE, AUTHOR, HELP_URI
from bbochat.data_server import DataServer
from bbochat.forms.frm_config import ConfigFrame
from bbochat.text import Text

txt = Text()
SPACES = " " * 20


class MainMenu:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root

    def create(self):
        menubar = tk.Menu()
        self.root["menu"] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label="File")

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label="Help")

    def _file_menu_items(self) -> list:
        return [
            MenuItem(f"My name{txt.ELLIPSIS}", self._get_my_name),
            MenuItem(f"{txt.CONFIG}{txt.ELLIPSIS}", self._show_config_frame),
            MenuItem(txt.EXIT, self._dismiss),
        ]

    def _get_my_name(self) -> None:
        data_server = DataServer()
        data_server.read()
        if dlg := simpledialog.askstring(
            f"{APP_TITLE} - Your name",
            "Enter the name that you wish to be known by",
            parent=self.root,
            initialvalue=data_server.my_name,
        ):
            data_server.my_name = dlg
            data_server.save()
            self.parent.my_name_text.set(dlg)

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f"On line help{txt.ELLIPSIS}", self._show_help),
            MenuItem(
                f"Data directory location{txt.ELLIPSIS}",
                self._show_data_directory,
            ),
            MenuItem(f"About{txt.ELLIPSIS}", self._show_about),
        ]

    def _show_help(self):
        webbrowser.open(HELP_URI)

    def _show_data_directory(self):
        directory = f"Data directory: {config.data_directory} {SPACES}"
        messagebox.showinfo(self, title="Data directory", message=directory)

    def _show_about(self):
        about = (
            f"{APP_TITLE}\nVersion: {__version__}\nAuthor: {AUTHOR} {SPACES}"
        )
        messagebox.showinfo(self, title=f"About {APP_TITLE}", message=about)

    def _dismiss(self, *args):
        self.root.destroy()
