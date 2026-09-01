"""Notes tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils import messagebox
from psiutils.constants import PAD, Mode, Status
from psiutils.menus import Menu, MenuItem
from psiutils.widgets import HAND
from tkhtmlview import HTMLText

from bbochat.buttons import ButtonFrame
from bbochat.data_store import data_store
from bbochat.forms.frm_notes_edit import NotesEditFrame
from bbochat.text import Text

txt = Text()


class NotesFrame:
    def __init__(self, parent, master):
        self.root = parent.root
        self.notes = data_store.notes
        self.category = ""

        # tk variables
        self.categories = tk.StringVar(value=sorted(list(self.notes)))

        self.notes_frame = self._get_notes_frame(master)

        self.context_menu = self._context_menu()

    def _get_notes_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        selection_frame = self._selection_frame(frame)
        selection_frame.grid(row=0, column=0, sticky=tk.NS)

        notes_frame = self._notes_frame(frame)
        notes_frame.grid(
            row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=PAD, pady=PAD
        )

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(
            row=0, column=2, rowspan=2, sticky=tk.N, padx=PAD, pady=PAD
        )

        return frame

    def _selection_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master)
        frame.rowconfigure(1, weight=1)

        label = ttk.Label(frame, text="Notes")
        label.grid(row=0, column=0)

        self.listbox = tk.Listbox(
            frame,
            listvariable=self.categories,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.listbox.grid(row=1, column=0, sticky=tk.NS, padx=PAD, pady=PAD)
        self.listbox.bind("<<ListboxSelect>>", self._category_selected)
        self.listbox.bind("<Button-3>", self._show_context_menu)

        return frame

    def _notes_frame(self, master: tk.Frame) -> tk.Frame:
        frame = tk.Frame(master, relief=tk.SUNKEN)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        self.notes_text = HTMLText(frame)
        self.notes_text.grid(row=0, column=0, sticky=tk.NSEW)

        return frame

    def _button_frame(self, master: ttk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.VERTICAL)
        frame.buttons = [
            frame.icon_button("new", self._new),
            frame.icon_button("edit", self._edit, True),
            frame.icon_button("delete", self._delete, True),
        ]
        frame.enable(False)
        return frame

    def _new(self, *args) -> None:
        dlg = NotesEditFrame(self, Mode.NEW)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.status != Status.UPDATED:
            return
        self._create_report(dlg.text)
        self.categories.set(sorted(list(self.notes)))

    def _edit(self, *args) -> None:
        dlg = NotesEditFrame(self, Mode.EDIT)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.status != Status.UPDATED:
            return
        self._create_report(dlg.text)

    def _delete(self, *args) -> None:
        if not self.category:
            return
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_ITEM):
            return
        self.notes.pop(self.category)

        data_store.save()
        self._create_report("")
        self.categories.set(sorted(list(self.notes)))
        self.category = ""
        self.listbox.selection_clear(0, tk.END)

    def _category_selected(self, event: object = None) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        categories = sorted(list(self.notes))
        self.category = categories[selection[0]]
        notes = self.notes[self.category]
        self.context_menu.enable()
        self.button_frame.enable()
        self._create_report(notes)

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(txt.NEW, self._new, dimmable=False),
            MenuItem(txt.EDIT, self._edit, dimmable=True),
            MenuItem(txt.DELETE, self._delete, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _show_context_menu(self, event: tk.Event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _create_report(self, report: str) -> str:
        self.notes_text.set_html(report.replace("\n", "<br>"))
