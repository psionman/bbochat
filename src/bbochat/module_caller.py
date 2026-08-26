from psiutils.module_caller import ModuleCaller as ModuleCallerBase

from bbochat.data_store import data_store
from bbochat.forms.frm_config import ConfigFrame
from bbochat.forms.frm_edit_select import EditSelectFrame


class ModuleCaller(ModuleCallerBase):
    def __init__(self, root, parsed_args: dict) -> None:
        self.modules = {
            "config": (self._config, None),
            "edit": (self._edit, "Edit greetings"),
        }
        super().__init__(root, parsed_args)

    def _config(self) -> None:
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _edit(self) -> None:
        ds = data_store
        ds.read()
        dlg = EditSelectFrame(self)
        self.root.wait_window(dlg.root)
