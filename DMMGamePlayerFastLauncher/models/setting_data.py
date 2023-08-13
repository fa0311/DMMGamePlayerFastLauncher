from dataclasses import dataclass, field
from tkinter import DoubleVar, StringVar

from component.var import PathVar
from component.variable_base import VariableBase


@dataclass
class SettingData(VariableBase):
    theme: StringVar = field(default_factory=StringVar)
    appearance: StringVar = field(default_factory=StringVar)
    window_scaling: DoubleVar = field(default_factory=DoubleVar)
    dmm_game_player_folder: PathVar = field(default_factory=PathVar)
