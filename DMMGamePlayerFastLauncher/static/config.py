import os
from pathlib import Path

from models.setting_data import SettingData


class PathConfig:
    DATA = Path("data")
    ACCOUNT = DATA.joinpath("account")
    SHORTCUT = DATA.joinpath("shortcut")

    APP_CONFIG = DATA.joinpath("config.json")

    APPDATA = Path(os.getenv("APPDATA", default=""))
    DEFAULT_DMM_GAME_PLAYER_FOLDER = APPDATA.joinpath("dmmgameplayer5")

    ASSETS = Path("assets")
    I18N = ASSETS.joinpath("i18n")
    ICONS = ASSETS.joinpath("icons")
    LICENSE = ASSETS.joinpath("license").joinpath("LICENSE")
    SCHTASKS_TEMPLATE = ASSETS.joinpath("schtasks").joinpath("template.xml")
    THEMES = ASSETS.joinpath("themes")

    ICON_MAIN = ICONS.joinpath("DMMGamePlayerFastLauncher.ico")

    SCHTASKS = DATA.joinpath("schtasks")


class UrlConfig:
    CONTRIBUTION = "https://github.com/fa0311/DMMGamePlayerFastLauncher"
    RELEASE = "https://api.github.com/repos/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    DONATE = "https://github.com/sponsors/fa0311"
    ISSUE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/issues/new"


class SchtasksConfig:
    PATH = "schtasks.exe"
    FILE = "schtasks_v1_{0}"
    NAME = "\\Microsoft\\Windows\\DMMGamePlayerFastLauncher\\{0}"


class AppConfig:
    DATA: SettingData
