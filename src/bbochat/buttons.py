# buttons.py
from functools import partial

from psiutils.buttons import ButtonFrame as ButtonFrameBase
from psiutils.buttons import IconButton as IconButtonBase

from .constants import BUTTON_CONFIG_PATH, BUTTON_ICON_PATH

ButtonFrame = partial(
    ButtonFrameBase,
    button_config_path=BUTTON_CONFIG_PATH,
    icon_path=BUTTON_ICON_PATH,
)

IconButton = partial(IconButtonBase, icon_path=BUTTON_ICON_PATH)
# class IconButton(IconButtonBase):
# master: tk.Frame,
# text: str,
# icon: str,
# command: Callable | None = None,
# dimmable: bool = False,
# *,
# sticky: str = "",
# icon_path: str = BUTTON_ICON_PATH,
# icon_colour: str | tuple[int] = "",
# text_colour: str | tuple[int] = "",
# tag: str = "",
