import json
from tkinter import DoubleVar, StringVar

from component.var import PathVar
from models.setting_data import SettingData
from static.config import AppConfig, DataPathConfig, PathConfig


def config_loder():
    if DataPathConfig.APP_CONFIG.exists():
        with open(DataPathConfig.APP_CONFIG, "r", encoding="utf-8") as f:
            AppConfig.DATA = SettingData.from_dict(json.load(f))
    else:
        AppConfig.DATA = SettingData(
            lang=StringVar(value="ja"),
            theme=StringVar(value="blue"),
            appearance_mode=StringVar(value="dark"),
            window_scaling=DoubleVar(value=1.0),
            dmm_game_player_folder=PathVar(value=PathConfig.DEFAULT_DMM_GAME_PLAYER_FOLDER),
        )
