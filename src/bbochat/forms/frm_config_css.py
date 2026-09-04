"""ConfigCssFrame for BBO Chat."""

import tkinter as tk
from copy import deepcopy
from pathlib import Path
from tkinter import ttk
from tkinter.colorchooser import askcolor

from psiutils.constants import PAD, Pad, Status
from psiutils.utilities import window_resize
from psiutils.widgets import clickable_widget
from tkinterweb import HtmlFrame

from bbochat.buttons import ButtonFrame
from bbochat.constants import APP_TITLE, HTML_TEST
from bbochat.state import state
from bbochat.text import Text
from bbochat.utilities import display_html

txt = Text()
FRAME_TITLE = f"{APP_TITLE} - css  {txt.CONFIG}"

ELEMENTS = {
    "h1": "Heading 1",
    "h2": "Heading 2",
    "h3": "Heading 3",
    "p,ul": "Text",
}

COLOURS = ["color", "background-color"]


class ConfigCssFrame:
    def __init__(self, parent: tk.Frame) -> None:
        self.focus = False
        self.root = tk.Toplevel(parent.root)
        self.css = deepcopy(parent.css)
        self.status = Status.NULL

        self.colour_entry = None
        self.property_frame = None
        self.html_frame = None
        self.button_frame = None

        # tk variables
        self.element = tk.StringVar()
        self.font_size = tk.IntVar()
        self.colours = {colour: "" for colour in COLOURS}

        self.font_size.trace_add("write", self._font_size_changed)

        self._show()

        self.colour_entries = {
            "color": self.colour_entry,
        }
        self.display_html()
        if parent.css_element:
            self.element.set(parent.css_element)
            self.font_size.set(self.css[parent.css_element]["font-size"])
            self.element_css = self.css[self.element.get()]
            self._update_attribute_colours()
            self._enable_properties()

    def _show(self) -> None:
        root = self.root
        root.geometry(state.geometry[Path(__file__).stem])
        root.title(FRAME_TITLE)
        root.bind(
            "<Configure>",
            lambda event, arg=None: window_resize(self, __file__),
        )
        root.bind("<Control-x>", self._dismiss)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        elements = self._element_frame(frame)
        elements.grid(row=0, column=0, sticky=tk.N)

        self.property_frame = self._property_frame(frame)
        self.property_frame.grid(row=0, column=1, sticky=tk.N, padx=PAD)
        self._enable_properties(False)

        self.html_frame = HtmlFrame(frame, messages_enabled=False, height=200)
        self.html_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.html_frame.grid_propagate(0)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(
            row=2, column=0, columnspan=2, sticky=tk.EW, padx=PAD, pady=PAD
        )

        return frame

    def _element_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        for row, (value, text_) in enumerate(ELEMENTS.items()):
            button = ttk.Radiobutton(
                frame,
                text=text_,
                variable=self.element,
                value=value,
                command=self._element_selected,
            )
            button.grid(row=row, column=0, sticky=tk.W)

        return frame

    def _property_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)

        row = 0
        label = ttk.Label(frame, text="Font size")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)
        spinbox = ttk.Spinbox(
            frame,
            format="",
            from_=1,
            to=36,
            increment=1,
            textvariable=self.font_size,
        )
        spinbox.grid(row=row, column=1, sticky=tk.E, padx=PAD)
        clickable_widget(spinbox)

        row += 1
        label = ttk.Label(frame, text="Text colour")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)
        self.colour_entry = ttk.Entry(frame)
        self.colour_entry.grid(
            row=row, column=1, sticky=tk.EW, padx=PAD, pady=PAD
        )

        button = ttk.Button(frame, text=txt.ELLIPSIS)
        button.grid(row=row, column=2, padx=Pad.W)
        button.bind("<Button-1>", lambda e: self._ask_colour("color"))

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("use", self._ok, True),
            frame.icon_button("exit", self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _element_selected(self, *args) -> None:
        self.element_css = self.css[self.element.get()]
        self.font_size.set(self.element_css["font-size"])

        self.colours["color"] = "black"
        if "color" in self.element_css:
            self.colours["color"] = self.element_css["color"]

        self._update_attribute_colours()
        self._enable_properties()

    def _font_size_changed(self, *args) -> None:
        self.css[self.element.get()]["font-size"] = self.font_size.get()
        self._check_value_changed()

    def _ask_colour(self, attribute: str) -> None:
        colour = askcolor(
            initialcolor=self.colours[attribute],
            title=f"{attribute.capitalize()} colour",
        )
        if colour[1]:
            self.element_css[attribute] = colour[1]
            self.css[self.element.get()][attribute] = colour[1]
            self._update_attribute_colours()
            self._check_value_changed()

    def _update_attribute_colours(self) -> None:
        for attribute, entry in self.colour_entries.items():
            self._update_attribute_colour(attribute, entry)

    def _update_attribute_colour(
        self, attribute: str, entry: ttk.Entry
    ) -> None:
        colour = self.element_css[attribute]
        entry_style = ttk.Style()
        entry_style.configure(
            f"style_{attribute}.TEntry",
            fieldbackground=colour,
        )
        entry.configure(style=f"style_{attribute}.TEntry")

    def display_html(self) -> None:
        display_html(self.html_frame, HTML_TEST, self.css)

    def _enable_properties(self, enable: bool = True) -> None:
        state = "" if enable else "disable"
        for child in self.property_frame.winfo_children():
            child.configure(state=state)

    def _check_value_changed(self) -> None:
        self.button_frame.disable()
        if self.css != self.config.css:
            self.button_frame.enable()
        self.display_html()

    def _ok(self, *args) -> None:
        self.status = Status.OK
        # self.config.update('css', self.css)
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.focus = False
        self.root.destroy()
