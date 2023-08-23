from dataclasses import dataclass, field
from tkinter import BooleanVar, StringVar

from component.var import PathVar
from component.variable_base import VariableBase


@dataclass
class ShortcutData(VariableBase):
    product_id: StringVar = field(default_factory=StringVar)
    account_path: PathVar = field(default_factory=PathVar)
    game_args: StringVar = field(default_factory=StringVar)
    auto_update: BooleanVar = field(default_factory=BooleanVar)
