import json

from models.setting_data import AppConfig, DeviceData, SettingData
from static.config import DataPathConfig
from utils.utils import get_supported_lang


def config_loder():
    if DataPathConfig.APP_CONFIG.exists():
        with open(DataPathConfig.APP_CONFIG, "r", encoding="utf-8") as f:
            AppConfig.DATA = SettingData.from_dict(json.load(f))
    else:
        AppConfig.DATA = SettingData()

    if DataPathConfig.DEVICE.exists():
        with open(DataPathConfig.DEVICE, "r", encoding="utf-8") as f:
            AppConfig.DEVICE = DeviceData.from_dict(json.load(f))
    else:
        AppConfig.DEVICE = DeviceData()
        with open(DataPathConfig.DEVICE, "w+", encoding="utf-8") as f:
            json.dump(AppConfig.DEVICE.to_dict(), f)

    if AppConfig.DATA.lang.get() not in [x[0] for x in get_supported_lang()]:
        AppConfig.DATA.lang.set("en_US")

    AppConfig.DATA.update()
    AppConfig.DEVICE.update()
