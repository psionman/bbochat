"""ReportFrame for BBO Chat."""
import tkinter as tk
from tkinter import ttk
from tkinterhtml import HtmlFrame
from pathlib import Path
import re
import markdown

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button
from psiutils.utilities import window_resize

from constants import APP_TITLE
from config import get_config
import text

FRAME_TITLE = f'{APP_TITLE} - Report'

SUIT_CONVERSION = {
    'S': ('&spades;', 'black'),
    'H': ('&hearts;', 'red'),
    'D': ('&diams;', 'red'),
    'C': ('&clubs;', 'black'),
}


class ReportFrame():
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.partner = parent.partner
        self.date = parent.report_date
        self.config = get_config()
        self.path = parent.path.get()

        # tk variables

        self.show()

        self.report = self._create_report()

    def show(self) -> None:
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.bind('<Control-x>', self.dismiss)

        root.rowconfigure(0, weight=1)
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
        frame.columnconfigure(0, weight=1)

        self.html_frame = HtmlFrame(frame, horizontal_scrollbar='auto')
        self.html_frame.grid(row=0, column=0, sticky=tk.NSEW)
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            # Button(
            #     frame,
            #     text=text.SAVE_PDF,
            #     command=self._create_pdf,
            #     underline=0,
            #     dimmable=True),
            Button(
                frame,
                text=text.EXIT,
                command=self.dismiss,
                sticky=tk.E,
                underline=1),
        ]
        frame.enable(False)
        return frame

    def _create_report(self) -> str:
        notes = self.parent.get_notes_content()
        output = '# Tournament report'
        output = f'{output}\n\n Date: {self.date.strftime('%d %B %Y')}'
        output = (f'{output}\n\n Partner: '
                  f'{self.partner.name} ({self.partner.username})')

        if notes['board_notes']:
            output = f'{output}\n\n <h2>Board notes</h2>'
            output = f'{output}\n\n{self ._parse_md(notes['board_notes'])}'

        if notes['general_notes']:
            output = f'{output}\n\n <h2>General notes</h2>'
            output = f'{output}\n\n{self ._parse_md(notes['general_notes'])}'

        html = markdown.markdown(output)
        self.html_frame.set_content(html)
        self._save_html(html)
        return html

    def _parse_md(self, text: str) -> str:
        text = self._parse_board_number(text)
        text = self._parse_suit(text)
        return text

    def _parse_board_number(self, text: str) -> str:
        match = re.findall(r'[b][0-9]{1,}[.]', text)
        for item in match:
            text = text.replace(item, f'**Board {item[1: -1]}.**')
        return text

    def _parse_suit(self, text: str) -> str:
        for suit in 'shdcSHDC':
            match = re.findall(f'[!][{suit}]', text)
            for item in match:
                if item[1].upper() in SUIT_CONVERSION:
                    conversion = SUIT_CONVERSION[item[1].upper()]
                    text = text.replace(
                        item,
                        (f'<span style="color:{conversion[1]}">'
                         f'{conversion[0]}</span>'))
        return text

    def _save_html(self, html) -> None:
        with open(self.path.replace('.txt', '.html'), 'w') as f_html:
            f_html.write(html)

    def dismiss(self, *args) -> None:
        self.root.destroy()
