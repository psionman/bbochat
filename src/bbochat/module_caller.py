from psiutils.module_caller import ModuleCaller as ModuleCallerBase

from bbochat.constants import ChatMode
from bbochat.data_store import data_store
from bbochat.forms.frm_config import ConfigFrame
from bbochat.forms.frm_edit_select import EditSelectFrame
from bbochat.mode_data import ModeData


class ModuleCaller(ModuleCallerBase):
    def __init__(self, root, parsed_args: dict) -> None:
        self.modules = {
            "config": (self._config, None),
            "edit": (
                self._edit,
                "Params: mode to edit, text to select (optional)",
            ),
        }
        super().__init__(root, parsed_args)

    def _config(self) -> None:
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _edit(self) -> None:
        ds = data_store
        ds.read()
        self.selected_text = self.args.secondary or ""
        if self.args.primary:
            self.mode = self.chat_mode_from_string(self.args.primary)
        else:
            self.mode = ChatMode.GREETINGS
        self.mode_data = ModeData(
            source_data=data_store.data_sets[self.mode.name.lower()]
        )
        dlg = EditSelectFrame(self)
        self.root.wait_window(dlg.root)

    def chat_mode_from_string(self, name: str) -> ChatMode:
        try:
            return ChatMode[name.upper()]
        except KeyError:
            raise ValueError(f"Unknown chat mode: {name!r}") from None
