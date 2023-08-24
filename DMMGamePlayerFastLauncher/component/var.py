from pathlib import Path
from tkinter import StringVar
from typing import Optional


class PathVar(StringVar):
    def __init__(self, master=None, value: Optional[Path] = None, name=None):
        super().__init__(master, str(value) if value else None, name)

    def get_path(self):
        return Path(super().get())

    def set_path(self, path: Path):
        super().set(str(path))
