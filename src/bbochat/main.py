"""Main procedure for BBOChat."""

import sys
import tkinter as tk

from psiutils.utilities import display_icon
from psiutils.widgets import get_styles

from bbochat import __app_name__, __version__
from bbochat.constants import APP_TITLE, ICON_FILE
from bbochat.forms.frm_main import AppFrame
from bbochat.module_caller import ModuleCaller

PARSER_ARGS = (
    ("module", "Module to load"),
    ("primary", "Primary argument"),
    ("secondary", "Secondary argument"),
)


def main():
    """Call the GUI loop."""

    root = tk.Tk()
    root.title(APP_TITLE)
    display_icon(root, ICON_FILE, ignore_error=True)

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    get_styles()

    if PARSER_ARGS:
        args = ModuleCaller.create_parser(PARSER_ARGS)
        if args.module:
            try:
                ModuleCaller(root, args)
            except Exception:
                root.destroy()
        else:
            AppFrame(root)

    root.mainloop()


if __name__ == "__main__":
    if "--version" in sys.argv:
        print(f"{__app_name__}. Version: {__version__}")
        sys.exit(0)
    main()
