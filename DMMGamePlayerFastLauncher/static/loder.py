import json

from models.setting_data import AppConfig, DeviceData, SettingData
from static.config import DataPathConfig


def config_loder():
    if DataPathConfig.APP_CONFIG.exists():
        with open(DataPathConfig.APP_CONFIG, "r", encoding="utf-8") as f:
            AppConfig.DATA = SettingData.from_dict(json.load(f))
    else:
        AppConfig.DATA = SettingData()

    if DataPathConfig.DEVICE.exists():
        with open(DataPathConfig.DEVICE, "r", encoding="utf-8") as f:
            AppConfig.DEVICE = DeviceData.from_dict(json.load(f))
        AppConfig.DEVICE.update()
    else:
        AppConfig.DEVICE = DeviceData()
        AppConfig.DEVICE.update()
        with open(DataPathConfig.DEVICE, "w+", encoding="utf-8") as f:
            json.dump(AppConfig.DEVICE.to_dict(), f)
