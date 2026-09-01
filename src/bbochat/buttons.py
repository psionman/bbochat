# buttons.py
import os
import tkinter as tk

from dotenv import load_dotenv
from psiutils.buttons import ButtonFrame as ButtonFrameBase

load_dotenv()


class ButtonFrame(ButtonFrameBase):
    def __init__(
        self,
        master: tk.Frame,
        orientation: str = tk.HORIZONTAL,
        button_config_path: str = os.getenv("ICON_BUTTON_CONFIG_PATH"),
        icon_path: str = os.getenv("ICON_IMAGE_PATH"),
        **kwargs: dict,
    ):
        super().__init__(
            master,
            orientation,
            button_config_path,
            icon_path=icon_path,
            **kwargs,
        )
