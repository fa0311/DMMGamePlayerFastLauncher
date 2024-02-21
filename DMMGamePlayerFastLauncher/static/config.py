from pathlib import Path

from static.dump import Dump


class DataPathConfig(Dump):
    DATA = Path("data")
    ACCOUNT = DATA.joinpath("account")
    ACCOUNT_SHORTCUT = DATA.joinpath("account_shortcut")
    SHORTCUT = DATA.joinpath("shortcut")
    LOG = DATA.joinpath("log")
    APP_CONFIG = DATA.joinpath("config.json")
    SCHTASKS = DATA.joinpath("schtasks")
    DEVICE = DATA.joinpath("device.json")


class AssetsPathConfig(Dump):
    PATH = Path("assets")
    I18N = PATH.joinpath("i18n")
    ICONS = PATH.joinpath("icons")
    LICENSE = PATH.joinpath("license").joinpath("LICENSE")
    TEMPLATE = PATH.joinpath("template")
    THEMES = PATH.joinpath("themes")

    ICON_MAIN = ICONS.joinpath("DMMGamePlayerFastLauncher.ico")

    SCHTASKS = TEMPLATE.joinpath("schtasks.xml")
    SHORTCUT = TEMPLATE.joinpath("shortcut.ps1")


class UrlConfig(Dump):
    CONTRIBUTION = "https://github.com/fa0311/DMMGamePlayerFastLauncher"
    RELEASE_API = "https://api.github.com/repos/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    RELEASE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    DONATE = "https://github.com/sponsors/fa0311"
    ISSUE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/issues/new"


class SchtasksConfig(Dump):
    FILE = "schtasks_v1_{0}_{1}"
    NAME = "\\Microsoft\\Windows\\DMMGamePlayerFastLauncher\\{0}"


class DiscordConfig(Dump):
    CLIENT_ID = "1209708526889345075"
