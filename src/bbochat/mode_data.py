# mode_data.py

"""Handle data management for BBO Chat."""

import uuid

from bidict import bidict


class ModeData:
    """
    This class holds data for the specific mode (e.g. 'chat')
    The data server holds data for the whole application (see data.py).
    """

    def __init__(
        self,
        data_server: dict,
        source_data: list | dict = None,
        has_master: bool = False,
        slave=None,
    ):

        self.data_server = data_server
        self.has_master = has_master
        self.slave = slave
        self.text_register = {}
        self.key_register = bidict()  # key <-> uid

        # slave (has slave) => self.data_items is a dict of text items,
        # otherwise a list of text
        if not source_data:
            source_data = {} if slave else []
        self.data_items = source_data

        # self.display_list_raw is a list of the data items
        # might be set in self._item_selected if it's a slave frame
        self.display_list_raw = list(source_data)

        # self.display_list is a cleaned version of the list in display_list_raw.
        # might be set in self._item_selected is it's a slave frame
        # Used to display items in the relevant listbox.

        # build registers used to handle edit_all for master frames

        # text_register is a dict of text items (a list) keyed on uuids
        # key_register is a  bidict of uuids and the keys (text) to
        # the text items list
        (self.text_register, self.key_register) = self._build_registers()

    @property
    def display_list(self) -> str:
        return self._remove_commented_items()

    def add(self, frame, text) -> None:
        self.display_list_raw.append(text)

        if self.slave:
            self.data_items[text] = []
        elif self.has_master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text].append(text)
        else:
            self.data_items.append(text)

        self.save(frame.mode.name)

    def amend(self, frame, old_value: str, new_value: str) -> None:
        print(f"amend: {self.display_list_raw[0]=}")
        print(f"amend: {self.display_list[0]=}")
        print(f"old_value: {old_value} new_value: {new_value}")
        self._update_display_list(self.display_list_raw, old_value, new_value)

        if self.slave:
            self.data_items[new_value] = self.data_items[old_value]
            self.data_items.pop(old_value)
        elif self.has_master:
            data = frame.master_frame.mode_data.data_items
            self._update_display_list(
                data[frame.master_frame.selected_text], old_value, new_value
            )
        else:
            self.data_items = self.display_list_raw

        self.save(frame.mode.name)

    def delete(self, frame) -> None:
        self.display_list_raw.remove(frame.selected_text)

        if self.slave:
            self.data_items.pop(frame.selected_text)
            self._delete_slave_data(frame.slave_frame)
        elif self.has_master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text].remove(frame.selected_text)
        else:
            self.data_items.remove(frame.selected_text)
        self.save(frame.mode.name)

    def edit_all(self, frame, display_list_raw: list[str]) -> None:
        self.display_list_raw = display_list_raw

        if self.slave:
            pass
        elif self.has_master:
            data = frame.master_frame.mode_data.data_items
            data[frame.master_frame.selected_text] = self.display_list_raw
        else:
            data = ""  # ,!!!!!!!!!!!!!!!!!!
            self.data_items = data
            print("data wierd")
        self.save(frame.mode.name)

    def update_slave_data(self, slave, selected_text: str) -> None:
        """
        Updates the slave data.

        Args:
            slave: The slave frame.
            selected_text: The selected text.
        """
        if selected_text not in self.data_items:
            self.data_items[selected_text] = []
        # !! DON'T CHANGE THIS NEXT LINE, without it direct edit does not work
        # self.display_list_raw = self.data_items[selected_text]
        data = self.data_items[selected_text]
        slave.mode_data.text_data = data
        slave.mode_data.display_list_raw = list(data)
        # slave.mode_data.display_list:
        #       a list of strings to appear in the slave panel
        slave.mode_data.display_list_raw = self._build_display_list(
            slave.mode_data.display_list_raw
        )
        # print(f"{slave.mode_data.display_list=}")
        slave.populate_text_items()

    def _delete_slave_data(self, slave) -> None:
        """
        Deletes the slave data.

        Args:
            slave: The slave frame.
        """
        slave.mode_data.text_data = []
        slave.mode_data.display_list_raw = []
        slave.mode_data.display_list = []

        slave.populate_text_items()

    def _update_display_list(
        self, display_list_raw: list[str], old_value: str, new_value: str
    ) -> None:
        """
        Updates the display list by replacing an old value with a new value.

        Args:
            display_list_raw: The list to update
            old_value: The value to replace
            new_value: The new value to insert
        """
        index = display_list_raw.index(old_value)
        display_list_raw.remove(old_value)
        display_list_raw.insert(index, new_value)

    def save(self, mode: str, *args) -> None:
        """
        Saves data to the data store based on the frame mode.

        Args:
            mode: The chat mode as string.
            *args: Additional arguments.
            *args: Additional arguments.

        Returns:
            None
        """

        # if not self.has_master:
        self.data_server.data_sets[mode] = self.data_items

        self.data_server.save()

    def _build_registers(self) -> dict:
        if not self.slave:
            return {}, bidict()

        # text_register is a dict of text items (a list) keyed on uuids
        # key_register is a  bidict of uuids and the keys (text) to
        # the text items list
        text_register = {}
        key_register = bidict()

        for key in self.data_items.keys():
            uid = str(uuid.uuid4())
            text_register[uid] = self.data_items[key]
            key_register[key] = uid

        # print("-" * 50)
        # for key, value in key_register.items():
        #     print(f"{key}: {value}")
        # for key, value in key_register.inverse.items():
        #     print(f"{key}: {value}")
        return text_register, key_register

    def _build_display_list(
        self, display_list_raw: list[str] = None
    ) -> list[str]:
        if not display_list_raw:
            return []
        return display_list_raw

    def _remove_commented_items(self) -> list[str]:
        return [
            item for item in self.display_list_raw if item and item[0] != "#"
        ]
