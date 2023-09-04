import json

from models.setting_data import AppConfig, SettingData
from static.config import DataPathConfig


def config_loder():
    if DataPathConfig.APP_CONFIG.exists():
        with open(DataPathConfig.APP_CONFIG, "r", encoding="utf-8") as f:
            AppConfig.DATA = SettingData.from_dict(json.load(f))
    else:
        AppConfig.DATA = SettingData()
