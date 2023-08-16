from dataclasses import dataclass, field
from tkinter import StringVar

from component.var import PathVar
from component.variable_base import VariableBase


@dataclass
class ShortcutData(VariableBase):
    product_id: StringVar = field(default_factory=StringVar)
    account_path: PathVar = field(default_factory=PathVar)
    game_args: StringVar = field(default_factory=StringVar)


@dataclass
class ShortcutDataRaw:
    product_id: str = field(default_factory=str)
    account_path: str = field(default_factory=str)
    game_args: str = field(default_factory=str)
