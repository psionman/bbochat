"""Handle data management for BBO Chat."""
import uuid

from constants import MODES, META_CODES


class DataManager():
    def __init__(
            self,
            data_store: dict,
            data: list | dict = None,
            master=None,
            slave=None
            ):

        self.data_store = data_store
        self.master = master
        self.slave = slave

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

        # build a meta dict used to handle edit_all for master frames
        self.meta_dict = self._meta_dict()

    def add(self, frame, text) -> None:
        self.text_list.append(text)
        self.display_list = self._build_display_list()

        if self.slave:
            self.data[text] = []
        elif self.master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text].append(text)
        else:
            self.data.append(text)

        self.save(frame)

    def amend(self, frame, old_value: str, new_value: str) -> None:
        self._update_text_list(
            self.text_list, old_value, new_value)
        self.display_list = self._build_display_list()

        if self.slave:
            self.data[new_value] = self.data[old_value]
            self.data.pop(old_value)
        elif self.master:
            data = frame.master_frame.data.data
            self._update_text_list(
                data[frame.master_frame.selected_text], old_value, new_value)
        else:
            self.data = self.text_list

        self.save(frame)

    def delete(self, frame) -> None:
        self.text_list.remove(frame.selected_text)
        self.display_list = self._build_display_list()

        if self.slave:
            self.data.pop(frame.selected_text)
            self._delete_slave_data(frame.slave_frame)
        elif self.master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text].remove(frame.selected_text)
        else:
            self.data.remove(frame.selected_text)
        self.save(frame)

    def edit_all(self, frame, data: list[str], meta_dict: dict) -> None:
        self.text_list = data
        self.display_list = self._build_display_list()

        if self.slave:
            # This is a master frame: it has a slave frame
            self._rebuild_dict(meta_dict)
        elif self.master:
            data = frame.master_frame.data.data
            data[frame.master_frame.selected_text] = self.text_list
        else:
            self.data = data
        self.save(frame)

    def update_slave_data(self, slave, selected_text: str) -> None:
        data = self.data[selected_text]
        slave.data.text_data = data
        slave.data.text_list = list(data)
        slave.data.display_list = self._build_display_list(
            slave.data.text_list)

        slave.populate_text_items()

    def _delete_slave_data(self, slave) -> None:
        slave.data.text_data = []
        slave.data.text_list = []
        slave.data.display_list = []

        slave.populate_text_items()

    def _update_text_list(
            self,
            text_list: list[str],
            old_value: str,
            new_value: str) -> None:
        index = text_list.index(old_value)
        text_list.remove(old_value)
        text_list.insert(index, new_value)

    def save(self, frame, *args) -> None:
        if not self.master:
            self.data_store.data_sets[MODES[frame.mode]] = self.data

        self.data_store.save()
        if self.slave:
            self.meta_dict = self._meta_dict()

    def _rebuild_dict(self, new_meta_dict: dict) -> None:
        old_meta_dict = self._meta_dict()
        new_data = {}
        keys_to_sort = []
        for item in new_meta_dict.values():
            if item[0] == META_CODES['uuid']:
                data_key = item[1]
                keys_to_sort.append(data_key)

                # New item
                new_data[data_key] = []
                if data_key in old_meta_dict:
                    new_data[data_key] = self.data[data_key]

        for uuid_key, item in old_meta_dict.items():
            if item[0] == META_CODES['uuid'] and uuid_key in old_meta_dict:
                old_text_key = old_meta_dict[uuid_key][1]
                new_data[data_key] = self.data[old_text_key]

        # Ensure the items a re sorted according to the order in frm_edit
        sort_dict = {new_meta_dict[key][2]: key for key in keys_to_sort}
        self.data = {sort_dict[index]: new_data[sort_dict[index]]
                     for index in range(len(sort_dict))}

        self.text_list = list(self.data)
        self.display_list = self._build_display_list()

    # def _print_meta_dict(self, meta_dict) -> None:
    #     for key in sorted(list(meta_dict)):
    #         if meta_dict[key][0] == META_CODES['uuid']:
    #             print(key, meta_dict[key])
    #     for key in sorted(list(meta_dict)):
    #         if meta_dict[key][0] == META_CODES['text']:
    #             print(key, meta_dict[key])

    def _meta_dict(self) -> dict:
        if not self.slave:
            return {}

        meta_dict = {}
        for key in self.data.keys():
            uid = str(uuid.uuid4())
            meta_dict[uid] = (META_CODES['uuid'], key)
            meta_dict[key] = (META_CODES['text'], uid)
        return meta_dict

    def _build_display_list(self, text_list: list[str] = None) -> list[str]:
        if not text_list:
            text_list = self.text_list
        return [u'{unicodes_value}'.format(unicodes_value=item)
                for item in text_list if item and item[0] != '#']
