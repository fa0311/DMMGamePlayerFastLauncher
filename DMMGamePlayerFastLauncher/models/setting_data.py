from dataclasses import dataclass, field
from tkinter import DoubleVar, StringVar

from component.var import PathVar
from component.variable_base import VariableBase
from static.env import Env


@dataclass
class SettingData(VariableBase):
    lang: StringVar = field(default_factory=lambda: StringVar(value="ja"))
    theme: StringVar = field(default_factory=lambda: StringVar(value="blue"))
    appearance_mode: StringVar = field(default_factory=lambda: StringVar(value="dark"))
    window_scaling: DoubleVar = field(default_factory=lambda: DoubleVar(value=1.0))
    dmm_game_player_program_folder: PathVar = field(default_factory=lambda: PathVar(value=Env.DEFAULT_DMM_GAME_PLAYER_PROGURAM_FOLDER))
    dmm_game_player_data_folder: PathVar = field(default_factory=lambda: PathVar(value=Env.DEFAULT_DMM_GAME_PLAYER_DATA_FOLDER))
