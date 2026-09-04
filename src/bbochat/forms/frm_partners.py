"""Partners tab for BBO Chat."""

import tkinter as tk
from tkinter import ttk

from psiutils import messagebox
from psiutils.constants import PAD, PADT, Mode, Status
from psiutils.menus import Menu, MenuItem
from psiutils.widgets import HAND, PsiText

from bbochat.buttons import ButtonFrame
from bbochat.data_store import Partner, data_store
from bbochat.forms.frm_partner_edit import PartnerEditFrame
from bbochat.message_store import message_store
from bbochat.state import state
from bbochat.text import Text

txt = Text()


class PartnerFrame:
    def __init__(self, parent, master: ttk.Notebook):
        self.root = parent.root
        self.partner = parent.partner
        self.greetings = data_store.greetings
        self.partners_names = sorted(list(data_store.partners.keys()))
        self.last_partner = state.session.get("last_partner")

        # tk variables
        self.partners_list = tk.StringVar(value=sorted(self.partners_names))
        self.partners_name = tk.StringVar()
        self.system = tk.StringVar()
        self.greeting = tk.StringVar()

        self.partners_frame = self._get_partners_frame(master)
        self.partners_frame.grid(row=0, column=0, sticky=tk.EW)

        self.system.trace_add("write", self._partner_changed)
        self.partners_name.trace_add("write", self._partner_changed)
        self.notes_text.bind("<<TextModified>>", self._partner_changed)

        self.context_menu = self._context_menu()

        if self.partner:
            self.button_frame.enable()
            self.context_menu.enable()
        message_store.subscribe(self._chat_message_publish)

    def _chat_message_publish(self):
        self.partner = message_store.partner
        self._update_partner_values()

    def _get_partners_frame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        partners_list = self._partners_list(frame)
        partners_list.grid(row=0, column=0, sticky=tk.NS, padx=PAD, pady=PAD)

        partners_details = self._partners_details(frame)
        partners_details.grid(row=0, column=1, sticky=tk.NSEW)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(
            row=0, column=2, rowspan=4, sticky=tk.N, padx=PAD, pady=PAD
        )

        return frame

    def _partners_list(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)

        label = ttk.Label(frame, text="Partners")
        label.grid(row=0, column=0)

        self.listbox = tk.Listbox(
            frame,
            listvariable=self.partners_list,
            selectmode=tk.BROWSE,
            cursor=HAND,
        )
        self.listbox.grid(row=1, column=0, sticky=tk.NSEW)
        if self.last_partner and self.last_partner in self.partners_names:
            index = self.partners_names.index(self.last_partner)
            self.listbox.select_set(index)
        self.listbox.bind("<<ListboxSelect>>", self._partner_selected)
        self.listbox.bind("<Button-3>", self._show_context_menu)

        return frame

    def _partners_details(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="Name")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD)

        entry = ttk.Entry(
            frame, width=30, textvariable=self.partners_name, state="readonly"
        )
        entry.grid(row=row, column=1, sticky=tk.EW, pady=PADT)

        row += 1
        label = ttk.Label(frame, text="System")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD)

        entry = ttk.Entry(
            frame, width=80, textvariable=self.system, state="readonly"
        )
        entry.grid(row=row, column=1, sticky=tk.EW, pady=PADT)

        row += 1
        label = ttk.Label(frame, text="Greeting")
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD)

        entry = ttk.Entry(
            frame, width=80, textvariable=self.greeting, state="readonly"
        )
        entry.grid(row=row, column=1, sticky=tk.EW, pady=PADT)

        row += 1
        frame.rowconfigure(row, weight=1)
        self.notes_text = PsiText(frame)
        self.notes_text.grid(
            row=row, column=0, columnspan=2, sticky=tk.NSEW, padx=PAD, pady=PAD
        )
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

    def _partner_selected(self, event: object = None) -> None:
        # TODO What happens if a tournament file is open?
        selected_index = event.widget.curselection()
        if not selected_index:
            return
        partners_names = sorted(list(data_store.partners))
        user_name = partners_names[selected_index[0]]

        self.partner = data_store.partners[user_name]
        # TODO: Update the tournament tab with the new partner
        # self.parent.tournament_tab.change_partner(self.partner)
        self._update_partner_values()
        state.session["last_partner"] = self.partner.username
        state.save()
        message_store.partner = self.partner

    def _update_partner_values(self) -> None:
        if not self.partner:
            return

        self.greeting.set(self.partner.greeting)
        self.partners_name.set(self.partner.name)
        self.system.set(self.partner.system)
        self.notes_text.delete("0.0", tk.END)
        self.notes_text.insert("0.0", self.partner.notes)

    def _partner_changed(self, *args) -> None:
        self.button_frame.enable(False)
        notes = self.notes_text.get("0.0", tk.END)
        if (
            self.system.get() != self.partner.system
            or self.partners_name.get() != self.partner.system
            or notes != self.partner.notes
        ):
            self.button_frame.enable()
            self.context_menu.enable()

    def _item_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return

        self.partner = data_store.partners[selection[0]]
        self.context_menu.enable()

    def _new(self, *args) -> None:
        dlg = PartnerEditFrame(self, Mode.NEW)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.status != Status.OK:
            return
        self.partner = dlg.partner
        data_store.partners[self.partner.username] = self.partner
        partners_names = sorted(list(data_store.partners))
        self.partners_list.set(partners_names)

        if selection := self.listbox.curselection():
            self.listbox.select_clear(selection[0])
        index = partners_names.index(self.partner.username)
        self.listbox.select_set(index)
        self.listbox.event_generate("<<ListboxSelect>>")
        self.partner = dlg.partner
        self._update_partner_values()

    def _edit(self, *args) -> None:
        dlg = PartnerEditFrame(self, Mode.EDIT, partner=self.partner)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)
        if dlg.status != Status.OK:
            return
        self.partner = dlg.partner
        self._update_partner_values()

    def _delete(self, *args) -> None:
        if not messagebox.askyesno(self, txt.DELETE_TITLE, txt.DELETE_ITEM):
            return
        data_store.partners.pop(self.partner.username)
        if data_store.partners:
            self.partner = data_store.partners[
                sorted(list(data_store.partners))[0]
            ]
        else:
            self.partner = Partner()
        self._update_partner_values()
        self.partners_list.set(sorted(list(data_store.partners)))
        data_store.save()

    def _save(self, *args) -> None:
        self.partner.name = self.partners_name.get()
        self.partner.system = self.system.get()
        self.partner.greeting = self.greeting.get()
        self.partner.notes = self.notes_text.get(0.0, tk.END)
        data_store.partners[self.partner.username] = self.partner
        self._update_partner_values()
        data_store.save()
        messagebox.showinfo(self, "", "Partner saved")

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
