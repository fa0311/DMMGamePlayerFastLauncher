import json
import logging
from pathlib import Path

from lib.version import Version
from models.setting_data import AppConfig, DeviceData, SettingData
from static.config import AssetsPathConfig, DataPathConfig
from static.env import Env
from utils.utils import get_supported_lang


def config_loder():
    if not DataPathConfig.DATA.exists():
        raise FileNotFoundError(f"{DataPathConfig.DATA} not found")
    if not AssetsPathConfig.PATH.exists():
        raise FileNotFoundError(f"{AssetsPathConfig.PATH} not found")

    if DataPathConfig.APP_CONFIG.exists():
        with open(DataPathConfig.APP_CONFIG, "r", encoding="utf-8") as f:
            AppConfig.DATA = SettingData.from_dict(json.load(f))
    else:
        AppConfig.DATA = SettingData()
        with open(DataPathConfig.APP_CONFIG, "w+", encoding="utf-8") as f:
            json.dump(AppConfig.DATA.to_dict(), f)

    if DataPathConfig.DEVICE.exists():
        with open(DataPathConfig.DEVICE, "r", encoding="utf-8") as f:
            AppConfig.DEVICE = DeviceData.from_dict(json.load(f))
    else:
        AppConfig.DEVICE = DeviceData()
        with open(DataPathConfig.DEVICE, "w+", encoding="utf-8") as f:
            json.dump(AppConfig.DEVICE.to_dict(), f)

    AppConfig.DATA.update()
    AppConfig.DEVICE.update()


def config_migrate():
    if AppConfig.DATA.last_version.get() != Env.VERSION:
        version = Version(AppConfig.DATA.last_version.get() or "v0.0.0")
        logging.info(f"Migration from {version} to {Env.VERSION}")

        if version < Version("v5.5.2"):
            logging.info("Migration from v5.5.0 to v5.5.1")
            Path(AssetsPathConfig.I18N).joinpath("app.ja.yml").unlink(missing_ok=True)
            Path(AssetsPathConfig.I18N).joinpath("app.en.yml").unlink(missing_ok=True)

            if AppConfig.DATA.lang.get() not in [x[0] for x in get_supported_lang()]:
                AppConfig.DATA.lang.set("en_US")

        AppConfig.DATA.last_version.set(Env.VERSION)
        with open(DataPathConfig.APP_CONFIG, "w+", encoding="utf-8") as f:
            json.dump(AppConfig.DATA.to_dict(), f)
