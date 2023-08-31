from dataclasses import dataclass, field
from tkinter import BooleanVar, DoubleVar, StringVar

from component.var import PathVar
from component.variable_base import VariableBase
from static.env import Env


@dataclass
class SettingData(VariableBase):
    dmm_game_player_program_folder: PathVar = field(default_factory=lambda: PathVar(value=Env.DEFAULT_DMM_GAME_PLAYER_PROGURAM_FOLDER))
    dmm_game_player_data_folder: PathVar = field(default_factory=lambda: PathVar(value=Env.DEFAULT_DMM_GAME_PLAYER_DATA_FOLDER))
    proxy_http: StringVar = field(default_factory=lambda: StringVar(value=""))
    proxy_https: StringVar = field(default_factory=lambda: StringVar(value=""))
    lang: StringVar = field(default_factory=lambda: StringVar(value="ja"))
    theme: StringVar = field(default_factory=lambda: StringVar(value="blue"))
    appearance_mode: StringVar = field(default_factory=lambda: StringVar(value="dark"))
    window_scaling: DoubleVar = field(default_factory=lambda: DoubleVar(value=1.0))
    debug_window: BooleanVar = field(default_factory=lambda: BooleanVar(value=False))


class AppConfig:
    DATA: SettingData
