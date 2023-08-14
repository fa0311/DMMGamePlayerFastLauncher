from dataclasses import dataclass, field
from tkinter import StringVar

from component.var import PathVar
from component.variable_base import VariableBase


@dataclass
class ShortcutData(VariableBase):
    product_id: StringVar = field(default_factory=StringVar)
    game_path: PathVar = field(default_factory=PathVar)
    game_args: StringVar = field(default_factory=StringVar)
    uac_mode: StringVar = field(default_factory=lambda: StringVar(value="uac_usual"))
