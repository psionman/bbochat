
"""
Tkinter root for BBO Chat.
"""
import sys
import tkinter as tk
from pathlib import Path

from psiutils.widgets import get_styles
from psiutils.utilities import display_icon

from bbochat.constants import ICON_FILE, USER_DATA_DIR
from bbochat.module_caller import ModuleCaller

from bbochat.forms.frm_main import MainFrame


class Root():
    def __init__(self) -> None:
        """Create the app's root and loop."""
        self.root = tk.Tk()
        root = self.root
        root.option_add('*tearOff', False)
        display_icon(root, ICON_FILE)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        get_styles()

        dlg = None
        if len(sys.argv) > 1:
            module = sys.argv[1]
            dlg = ModuleCaller(root, module)
        if not dlg or dlg.invalid:
            MainFrame(root)

        root.mainloop()
