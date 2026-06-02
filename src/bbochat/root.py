"""
Tkinter root for BBO Chat.
"""

import sys
import tkinter as tk
from tkinter import ttk

from psiutils.utilities import display_icon
from psiutils.widgets import get_styles

from bbochat.config import get_config
from bbochat.constants import ICON_FILE
from bbochat.forms.frm_main import MainFrame
from bbochat.module_caller import ModuleCaller


class Root:
    def __init__(self) -> None:
        """Create the app's root and loop."""
        self.config = get_config()
        self.root = tk.Tk()
        root = self.root
        root.option_add("*tearOff", False)
        display_icon(root, ICON_FILE)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        get_styles()
        self._set_styles()

        dlg = None
        if len(sys.argv) > 1:
            module = sys.argv[1]
            dlg = ModuleCaller(root, module)
        if not dlg or dlg.invalid:
            MainFrame(root)

        root.mainloop()

    def _set_styles(self) -> None:
        """Set the style of the app."""
        style = ttk.Style()
        # style.theme_use('clam')
        style.configure(
            "greeting.TButton", background=self.config.colours["GREETINGS"]
        )
        style.configure(
            "valediction.TButton",
            background=self.config.colours["VALEDICTION"],
        )
        style.configure("chat.TButton", background=self.config.colours["CHAT"])
        style.configure(
            "greeting.TFrame", background=self.config.colours["GREETINGS"]
        )
        style.configure(
            "valediction.TFrame", background=self.config.colours["VALEDICTION"]
        )
        style.configure("chat.TFrame", background=self.config.colours["CHAT"])
