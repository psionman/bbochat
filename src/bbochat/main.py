"""Main procedure for BBOChat."""

import argparse
import sys
import tkinter as tk

from psiutils.utilities import display_icon
from psiutils.widgets import get_styles

from bbochat import __app_name__, __version__, logger
from bbochat.constants import APP_TITLE, ICON_FILE
from bbochat.forms.frm_main import AppFrame
from bbochat.module_caller import ModuleCaller


def main():
    """Call the GUI loop."""
    logger.info("Application started")

    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument(
        "module", nargs="?", default=None, help="Module to load"
    )
    parser.add_argument(
        "primary", nargs="?", default=None, help="Primary argument"
    )
    parser.add_argument(
        "secondary", nargs="?", default=None, help="Secondary argument"
    )
    args = parser.parse_args()

    root = tk.Tk()
    root.title(APP_TITLE)
    display_icon(root, ICON_FILE, ignore_error=True)

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    get_styles()

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
