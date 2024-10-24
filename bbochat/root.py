
"""
Tkinter root for BBO Chat.
"""

import tkinter as tk

from psiutils.widgets import get_styles, display_icon

from constants import ICON_FILE
from forms.frm_main import MainFrame


class Root():
    def __init__(self) -> None:
        """Create the app's root and loop."""
        self.root = tk.Tk()
        root = self.root
        root.option_add('*tearOff', False)
        display_icon(root, ICON_FILE)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        get_styles()

        MainFrame(self)
        root.mainloop()
