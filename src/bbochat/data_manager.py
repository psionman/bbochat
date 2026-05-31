# data_manager.py

"""Handle data management for BBO Chat."""

import uuid

from bbochat.constants import ItemRegistryFields


class DataManager:
    """
    The data manager holds data for the specific mode (e.g. 'chat')
    The data store holds data for the whole application (see data.py).
    """

    def __init__(
        self,
        data_store: dict,
        data: list | dict = None,
        has_master: bool = False,
        slave=None,
    ):

        self.data_store = data_store
        self.has_master = has_master
        self.slave = slave
        self.text_register = {}
        self.key_register = {}
        self.uuid_register = {}

        # slave => the data set is a dict of text items,
        # otherwise a list of text
        if not data:
            data = {} if slave else []
        self.data = data

        # self.text_list is text_data converted to  list
        # might be set in self._item_selected if it's a slave frame
        self.text_list = list(data)

        # self.display_list is a cleaned version of the list in text_list.
        # might be set in self._item_selected is it's a slave frame
        # Used to display items in the relevant listbox.
        self.display_list = self._build_display_list()

        # build a item_register used to handle edit_all for master frames

        # text_register is a dict of text items (a list) keyed on uuids
        # key_register is a dict of uuids keyed on the keys
        # uuid_register is a dict of keys keyed on uuids
        (
            # self.item_register,
            self.text_register,
            self.key_register,
            self.uuid_register,
        ) = self._build_registers()

    def add(self, frame, text) -> None:
        self.text_list.append(text)
        self.display_list = self._build_display_list()

        if self.slave:
            self.data[text] = []
        elif self.has_master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text].append(text)
        else:
            self.data.append(text)

        self.save(frame.mode.name)

    def amend(self, frame, old_value: str, new_value: str) -> None:
        self._update_text_list(self.text_list, old_value, new_value)
        self.display_list = self._build_display_list()

        if self.slave:
            self.data[new_value] = self.data[old_value]
            self.data.pop(old_value)
        elif self.has_master:
            data = frame.master_frame.data.data
            self._update_text_list(
                data[frame.master_frame.selected_text], old_value, new_value
            )
        else:
            self.data = self.text_list

        self.save(frame.mode.name)

    def delete(self, frame) -> None:
        self.text_list.remove(frame.selected_text)
        self.display_list = self._build_display_list()

        if self.slave:
            self.data.pop(frame.selected_text)
            self._delete_slave_data(frame.slave_frame)
        elif self.has_master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text].remove(frame.selected_text)
        else:
            self.data.remove(frame.selected_text)
        self.save(frame.mode.name)

    def edit_all(
        self, frame, text_list: list[str], item_register: dict
    ) -> None:
        print(f"{item_register=}")
        self.text_list = text_list
        self.display_list = self._build_display_list()

        if self.slave:
            # This is a master frame: it has a slave frame
            # self._rebuild_item_register(item_register)
            pass
        elif self.has_master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text] = self.text_list
        else:
            data = ""  # ,!!!!!!!!!!!!!!!!!!
            self.data = data
            print("data wierd")
        self.save(frame.mode.name)

    def update_slave_data(self, slave, selected_text: str) -> None:
        data = self.data[selected_text]
        slave.data.text_data = data
        slave.data.text_list = list(data)
        slave.data.display_list = self._build_display_list(
            slave.data.text_list
        )

        slave.populate_text_items()

    def _delete_slave_data(self, slave) -> None:
        slave.data.text_data = []
        slave.data.text_list = []
        slave.data.display_list = []

        slave.populate_text_items()

    def _update_text_list(
        self, text_list: list[str], old_value: str, new_value: str
    ) -> None:
        index = text_list.index(old_value)
        text_list.remove(old_value)
        text_list.insert(index, new_value)

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

        print("saving data:", mode, type(self.data))
        # if not self.has_master:
        self.data_store.data_sets[mode] = self.data

        self.data_store.save()
        # if self.slave:
        #     self.item_register = self._build_registers()

    def _rebuild_item_register(self, new_item_register: dict) -> None:
        old_item_register = self._build_registers()
        # self.xxx("o", old_item_register)
        # self.xxx("n", new_item_register)
        new_data = {}
        keys_to_sort = []
        for item in new_item_register.values():
            if item[0] == ItemRegistryFields.UUID:
                data_key = item[1]
                keys_to_sort.append(data_key)

                # New item
                new_data[data_key] = []
                if data_key in old_item_register:
                    new_data[data_key] = self.data[data_key]

        for uuid_key, item in old_item_register.items():
            if (
                item[0] == ItemRegistryFields.UUID
                and uuid_key in old_item_register
            ):
                old_text_key = old_item_register[uuid_key][1]
                new_data[data_key] = self.data[old_text_key]
                print(f"Copying {old_text_key} to {data_key}")

        # Ensure the items a re sorted according to the order in frm_edit_select
        sort_dict = {new_item_register[key][1]: key for key in keys_to_sort}
        self.data = {
            sort_dict[index]: new_data[sort_dict[index]]
            for index in range(len(sort_dict))
        }

        self.text_list = list(self.data)
        self.display_list = self._build_display_list()

    # def xxx(self, type: str, item_register: dict) -> None:
    #     print(type)
    #     for key in sorted(list(item_register)):
    #         if item_register[key][0] == ItemRegistryFields.UUID:
    #             print(key, item_register[key])
    # for key in sorted(list(item_register)):
    #     if item_register[key][0] == ItemRegistryFields.TEXT:
    #         print(key, item_register[key])

    # def _print_item_register(self, item_register) -> None:
    #     for key in sorted(list(item_register)):
    #         if item_register[key][0] == META_CODES['uuid']:
    #             print(key, item_register[key])
    #     for key in sorted(list(item_register)):
    #         if item_register[key][0] == META_CODES['text']:
    #             print(key, item_register[key])

    def _build_registers(self) -> dict:
        # if not isinstance(self.data, dict):
        #     return {}
        if not self.slave:
            return {}, {}, {}

        # item_register = {}
        key_register = {}
        uuid_register = {}
        text_register = {}
        for text in self.data.keys():
            uid = str(uuid.uuid4())
            # item_register[uid] = (ItemRegistryFields.UUID, text)
            # item_register[text] = (ItemRegistryFields.TEXT, uid)

            text_register[uid] = self.data[text]
            key_register[text] = uid
            uuid_register[uid] = text
        return text_register, key_register, uuid_register

    def _build_display_list(self, text_list: list[str] = None) -> list[str]:
        if not text_list:
            text_list = self.text_list
        return [
            "{unicodes_value}".format(unicodes_value=item)
            for item in text_list
            if item and item[0] != "#"
        ]
