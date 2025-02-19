"""Utility functions for bbochat"""
import tkinter as tk
from pathlib import Path


def window_resize(master: tk.Tk, file: str, *args) -> None:
    match = master.root.geometry().split('+')
    window_geometry = (
        f'{master.root.winfo_width()}x{master.root.winfo_height()}+'
        f'{master.root.winfo_x()}+{match[2]}')
    geometry = master.config.geometry
    geometry[Path(file).stem] = window_geometry
    master.config.update('geometry', geometry)
    master.config.save()
