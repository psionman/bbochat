"""Notes tab for BBO Chat notebook"""

import json
import re
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

from dateutil.parser import parse  # type: ignore
from psiutils import messagebox
from psiutils.buttons import IconButton
from psiutils.constants import PAD
from psiutils.widgets import PsiText, Tooltip

from bbochat.buttons import ButtonFrame
from bbochat.config import config
from bbochat.constants import (
    DATA_DIR,
    FRAME_WIDTH,
    ICON_DIR,
    TXT_FILE_TYPES,
    YYYYMMDD,
)
from bbochat.data_store import Partner
from bbochat.forms.frm_report import ReportFrame
from bbochat.text import Text
from bbochat.utilities import get_notes_content

txt = Text()


class TournamentFrame:
    def __init__(self, parent, master):
        self.root = parent.root
        self.partner = parent.partner
        self.report_date = datetime.now()
        self.report_button = None
        self.board_notes = None
        self.original_notes = {}
        self.general_notes = None

        # Tk variables
        path = Path(DATA_DIR)
        if self.partner:
            path = Path(DATA_DIR, self.partner.username)
        date = datetime.now().strftime(YYYYMMDD)
        path = Path(path, f"{date}.txt")

        self.notes_path = tk.StringVar()
        self.set_path()
        self.tooltip_text = tk.StringVar(value=txt.REPORT_HELP)

        self.notes_frame = self._get_notes_frame(master)

        if config.notes_sashes:
            for index, sash in enumerate(config.notes_sashes):
                self.notes_panel.sash_place(index, sash[0], 0)

        self.change_partner(self.partner)

    def set_path(self) -> None:
        path = Path(DATA_DIR)
        if self.partner:
            path = Path(DATA_DIR, self.partner.username)
        date = datetime.now().strftime(YYYYMMDD)
        path = Path(path, f"{date}.txt")
        self.notes_path.set(path)
        self._get_date_from_path()

    def _get_notes_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.notes_panel = self._notes_panel(frame)
        self.notes_panel.grid(
            row=0, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD
        )

        label = ttk.Label(frame, text="Path")
        label.grid(row=1, column=0, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.notes_path)
        entry.grid(row=1, column=1, sticky=tk.EW)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=2, column=1, sticky=tk.W, pady=PAD)
        return frame

    def _button_frame(self, master: ttk.Frame) -> ttk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        self.report_button = IconButton(
            frame, txt.REPORT, "report", self._report, True
        )
        help_button = IconButton(frame, txt.HELP, "help", icon_path=ICON_DIR)

        help_button = ttk.Button(
            frame,
            text=txt.HELP,
        )
        help_button.tooltip = Tooltip(
            help_button,
            textvariable=self.tooltip_text,
            wrap_length=3500,
            vertical_offset=0,
        )
        open_todays = IconButton(
            frame, f"{txt.OPEN} today's", "open", self._open_todays_file
        )
        frame.buttons = [
            frame.icon_button("open", self._open_file),
            open_todays,
            frame.icon_button("save", self.save_notes, True),
            # help_button,
        ]

        # TODO sort out tooltip on IconButton
        help_button.grid(row=0, column=9, padx=PAD)

        frame.disable()
        return frame

    def _notes_panel(self, master: ttk.Frame) -> ttk.PanedWindow:
        frame = tk.PanedWindow(
            master,
            orient=tk.HORIZONTAL,
        )
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        board_frame = self._board_frame(frame)
        board_frame.grid(row=0, column=0, sticky=tk.NSEW)

        general_frame = self._general_frame(frame)
        general_frame.grid(row=0, column=0, sticky=tk.NSEW)

        frame.add(board_frame, width=FRAME_WIDTH)
        frame.add(general_frame, width=FRAME_WIDTH)

        return frame

    def _board_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text="Board notes")
        label.grid(row=0, column=0)

        self.board_notes = PsiText(frame, height=18)
        self.board_notes.grid(row=1, column=0, sticky=tk.NSEW)
        self.board_notes.bind("<KeyRelease>", self._value_changed)

        return frame

    def _general_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(frame, text="General notes")
        label.grid(row=0, column=0)

        self.general_notes = PsiText(frame, height=18)
        self.general_notes.grid(row=1, column=0, sticky=tk.NSEW)
        self.general_notes.bind("<KeyRelease>", self._value_changed)
        return frame

    def change_partner(self, partner: Partner) -> None:
        self.partner = partner
        self.set_path()
        self._notes_contents()
        self._value_changed()

    def notes_changed(self) -> bool:
        return self._get_current_notes() != self.original_notes

    def _get_current_notes(self) -> dict[str, str]:
        board_notes = self.board_notes.get("1.0", tk.END)
        general_notes = self.general_notes.get("1.0", tk.END)
        return {
            "board_notes": board_notes.strip("\n"),
            "general_notes": general_notes.strip("\n"),
        }

    def save_notes(self, *args) -> None:
        notes = self._get_current_notes()

        with open(self.notes_path.get(), "w", encoding="utf-8") as f_notes:
            json.dump(notes, f_notes)

        self._value_changed()

    def _open_file(self, *args) -> None:
        path = Path(self.notes_path.get()).parent
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        if path := filedialog.askopenfilename(
            initialdir=path,
            initialfile=self.notes_path.get(),
            parent=self.root,
            filetypes=TXT_FILE_TYPES,
        ):
            if Path(path).suffix != ".txt":
                messagebox.showerror(
                    self,
                    "Open file",
                    'Notes file must be a ".txt" file.',
                )
                return
            self.notes_path.set(path)
            self._notes_contents()
            self._get_date_from_path()
            self.button_frame.enable()

    def _open_todays_file(self, *args) -> None:
        self.set_path()
        self._notes_contents()
        self._get_date_from_path()
        self.button_frame.enable()

    def _get_date_from_path(self) -> datetime:
        if match := re.search(r"[0-9]" * 8, str(self.notes_path.get())):
            date = parse(match.group())

    def _get_notes_and_display(self) -> None:
        if not self.notes_path.get().is_file():
            return

    def _notes_contents(self) -> str:
        self.general_notes.delete("0.0", tk.END)
        self.board_notes.delete("0.0", tk.END)

        notes = get_notes_content(self.notes_path.get())
        self.original_notes = notes.copy()
        if "board_notes" in notes:
            self.board_notes.insert("1.0", notes["board_notes"])
        if "general_notes" in notes:
            self.general_notes.insert("1.0", notes["general_notes"])

    def _report(self, *args) -> None:
        dlg = ReportFrame(self)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)

    def _value_changed(self, *args):  # *args essential here to make it work
        board_notes = self.board_notes.get("1.0", tk.END)
        general_notes = self.general_notes.get("1.0", tk.END)
        self.button_frame.disable()
        if f"{board_notes}{general_notes}".replace("\n", ""):
            self.button_frame.enable()
        self.report_button.disable()
        if f"{board_notes}{general_notes}":
            self.report_button.enable()
