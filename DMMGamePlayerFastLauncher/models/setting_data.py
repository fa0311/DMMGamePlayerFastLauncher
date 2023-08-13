from dataclasses import dataclass, field
from tkinter import DoubleVar, StringVar

from component.var import PathVar
from component.variable_base import VariableBase


@dataclass
class SettingData(VariableBase):
    lang: StringVar = field(default_factory=StringVar)
    theme: StringVar = field(default_factory=StringVar)
    appearance_mode: StringVar = field(default_factory=StringVar)
    window_scaling: DoubleVar = field(default_factory=DoubleVar)
    dmm_game_player_folder: PathVar = field(default_factory=PathVar)
