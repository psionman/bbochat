from forms.frm_config import ConfigFrame
from forms.frm_edit import EditFrameTree
from data import DataStore


class ModuleCaller():
    def __init__(self, root, module) -> None:
        modules = {
            'config': self._config,
            'edit': self._edit,
            }

        self.invalid = False
        if module == '-h':
            for key in sorted(list(modules.keys())+['main']):
                print(key)
            self.invalid = True
            return

        if module not in modules:
            if module != 'main':
                print(f'Invalid function name: {module}')
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
        # self.partners = ds.partners
        # self.players = ds.players
        # self.pairs = ds.pairs
        # self.greetings = ds.greetings
        dlg = EditFrameTree(self, ds.greetings)
        self.root.wait_window(dlg.root)
