import json
from tkinter import DoubleVar, StringVar

from component.var import PathVar
from models.setting_data import SettingData
from static.config import AppConfig, PathConfig

APP_CONFIG: SettingData


def config_loder():
    if PathConfig.APP_CONFIG.exists():
        with open(PathConfig.APP_CONFIG, "r", encoding="utf-8") as f:
            AppConfig.DATA = SettingData.from_dict(json.load(f))
    else:
        AppConfig.DATA = SettingData(
            theme=StringVar(value="assets/themes/green.json"),
            appearance=StringVar(value="system"),
            window_scaling=DoubleVar(value=1.0),
            dmm_game_player_folder=PathVar(value=PathConfig.DEFAULT_DMM_GAME_PLAYER_FOLDER),
        )
