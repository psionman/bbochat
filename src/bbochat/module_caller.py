from bbochat.data import DataStore
from bbochat.forms.frm_config import ConfigFrame
from bbochat.forms.frm_edit_select import EditSelectFrame


class ModuleCaller:
    def __init__(self, root, module) -> None:
        modules = {
            "config": self._config,
            "edit": self._edit,
        }

        self.invalid = False
        if module == "-h":
            for key in sorted(list(modules.keys()) + ["main"]):
                print(key)
            self.invalid = True
            return

        if module not in modules:
            if module != "main":
                print(f"Invalid function name: {module}")
            self.invalid = True
            return

        self.root = root
        modules[module]()
        self.root.destroy()
        return

    def _config(self) -> None:
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _edit(self) -> None:
        self.data_store = DataStore()
        ds = self.data_store
        ds.read()
        dlg = EditSelectFrame(self, "greetings")
        self.root.wait_window(dlg.root)
