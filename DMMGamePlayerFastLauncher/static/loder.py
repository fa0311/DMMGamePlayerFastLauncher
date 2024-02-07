import json
from pathlib import Path

from models.setting_data import AppConfig, DeviceData, SettingData
from static.config import AssetsPathConfig, DataPathConfig
from static.env import Env


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

    if AppConfig.DATA.last_version.get() != Env.VERSION:
        if AppConfig.DATA.last_version.get() == "v5.4.0":
            Path(AssetsPathConfig.I18N).joinpath("app.ja.yml").unlink(missing_ok=True)
            Path(AssetsPathConfig.I18N).joinpath("app.en.yml").unlink(missing_ok=True)
            AppConfig.DATA.lang.set("en_US")

        AppConfig.DATA.last_version.set(Env.VERSION)

    AppConfig.DATA.update()
    AppConfig.DEVICE.update()
