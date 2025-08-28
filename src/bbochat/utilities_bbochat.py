""" Common utility functions for BBO Chat."""

import re
from pathlib import Path
from tkinterweb import HtmlFrame
import markdown

from bbochat.constants import USER_DATA_DIR

SUIT_CONVERSION = {
    'S': ('&spades;', 'black'),
    'H': ('&hearts;', 'red'),
    'D': ('&diams;', 'red'),
    'C': ('&clubs;', 'black'),
}

def build_text_list(data: list[str]) -> list[str]:
    return [f'{item}' for item in data if item and item[0] != '#']


def display_html(html_frame: HtmlFrame, text: str, css: dict = None) -> None:
    if not css:
        css = {}
    css_str = _css_from_dict(css)
    html = markdown.markdown(text)
    html = _parse_suit(html)
    page = f"""
        <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <style>{css_str}</style>
                </head>
                <body>
                    <h1>{html}</h1>
                </body>
            </html>"""

    _write_html_file(html_frame, 'dummy.html', '')
    _write_html_file(html_frame, 'temp.html', page)
    return page


def _write_html_file(html_frame: HtmlFrame, file: str, text: str) -> None:
    temp_path = Path(USER_DATA_DIR, file)
    path = str(temp_path)
    with open(path, 'w', encoding='utf-8') as f_html:
        f_html.write(text)
    html_frame.load_file(path)


def _parse_suit(suit_text: str) -> str:
    for suit in 'shdcSHDC':
        match = re.findall(f'[!][{suit}]', suit_text)
        for item in match:
            if item[1].upper() in SUIT_CONVERSION:
                conversion = SUIT_CONVERSION[item[1].upper()]
                suit_text = suit_text.replace(
                    item,
                    (f'<span style="color:{conversion[1]}">'
                        f'{conversion[0]}</span>'))
    return suit_text


def _css_from_dict(css: dict) -> str:
    css_str = ''
    for element, item in css.items():
        css_str = f'{css_str}{element}{{'
        for attribute, value in item.items():
            if attribute == 'font-size':
                value = f'{value}px'
            css_str = f'{css_str}{attribute}:{value};'
        css_str = f'{css_str}}}'
    return css_str
