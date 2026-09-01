import tkinter as tk
import webbrowser

from psiutils import messagebox
from psiutils.menus import Menu, MenuItem

from bbochat import (
    __app_name__,
    __author__,
    __summary__,
    __version__,
)
from bbochat.config import config
from bbochat.constants import HELP_URI
from bbochat.forms.frm_config import ConfigFrame
from bbochat.text import Text
from bbochat.utilities import get_my_name

txt = Text()
SPACES = 30
SEPARATOR = "-" * 50


class MainMenu:
    def __init__(self, parent):
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
        get_my_name()

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
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
        directory = f"Data directory: {config.data_directory} {' ' * SPACES}"
        messagebox.showinfo(self, title="Data directory", message=directory)

    def _show_about(self):
        about = (
            f"{__summary__}\n"
            f"{SEPARATOR}\n"
            f"{txt.VERSION}: {__version__}\n"
            f"{SEPARATOR}\n"
            f"{txt.AUTHOR}: {__author__:<{SPACES}}"
        )
        messagebox.showinfo(
            self, title=f"{txt.ABOUT} {__app_name__}", message=about
        )

    def _dismiss(self, *args):
        self.root.destroy()
