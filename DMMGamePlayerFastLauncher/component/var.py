from pathlib import Path
from tkinter import StringVar
from typing import Optional


class PathVar(StringVar):
    def __init__(self, master=None, value: Optional[Path] = None, name=None):
        super().__init__(master, str(value), name)

    def path(self):
        return Path(super().get())
