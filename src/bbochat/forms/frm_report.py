"""ReportFrame for BBO Chat."""

from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame
from psiutils.utilities import window_resize

from bbochat.constants import APP_TITLE
from bbochat.config import get_config
from bbochat.utilities_bbochat import display_html

FRAME_TITLE = f"{APP_TITLE} - Report"


class ReportFrame:
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.partner = parent.partner
        self.date = parent.report_date
        self.config = get_config()
        self.path = parent.path.get()

        self.html_frame = None

        # tk variables

        self._show()

        self.report = self._create_report()

    def _show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )

        root.bind("<Control-x>", self._dismiss)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, padx=0, sticky=tk.NSEW)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        main_frame = self._main_frame(frame)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(frame)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.html_frame = HtmlFrame(
            frame, horizontal_scrollbar="auto", messages_enabled=False
        )
        self.html_frame.grid(row=0, column=0, sticky=tk.NSEW)
        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _create_report(self) -> str:
        notes = self.parent.get_notes_content()
        output = "# Tournament report"
        output = f"{output}\n\n Date: {self.date.strftime('%d %B %Y')}"
        output = (
            f"{output}\n\n Partner: "
            f"{self.partner.name} ({self.partner.username})"
        )

        if "board_notes" in notes and notes["board_notes"]:
            output = f"{output}\n\n <h2>Board notes</h2>"
            output = f"{output}\n\n{self._parse_md(notes['board_notes'])}"

        if "general_notes" in notes and notes["general_notes"]:
            output = f"{output}\n\n <h2>General notes</h2>"
            output = f"{output}\n\n{self._parse_md(notes['general_notes'])}"

        html = display_html(self.html_frame, output, self.config.css)
        self._save_html(html)
        return html

    def _parse_md(self, text: str) -> str:
        match = re.findall(r"[b][0-9]{1,}[.]", text)
        for item in match:
            text = text.replace(item, f"**Board {item[1:-1]}.**")
        return text

    def _save_html(self, html) -> None:
        path = self.path.replace(".txt", ".html")
        with open(path, "w", encoding="utf-8") as f_html:
            f_html.write(html)

    def _dismiss(self, *args) -> None:
        self.root.destroy()
