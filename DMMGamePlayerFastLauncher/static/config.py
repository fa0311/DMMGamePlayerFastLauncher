from pathlib import Path


class DataPathConfig:
    DATA = Path("data")
    ACCOUNT = DATA.joinpath("account")
    SHORTCUT = DATA.joinpath("shortcut")
    APP_CONFIG = DATA.joinpath("config.json")
    SCHTASKS = DATA.joinpath("schtasks")


class AssetsPathConfig:
    PATH = Path("assets")
    I18N = PATH.joinpath("i18n")
    ICONS = PATH.joinpath("icons")
    LICENSE = PATH.joinpath("license").joinpath("LICENSE")
    TEMPLATE = PATH.joinpath("template")
    THEMES = PATH.joinpath("themes")

    ICON_MAIN = ICONS.joinpath("DMMGamePlayerFastLauncher.ico")

    SCHTASKS = TEMPLATE.joinpath("schtasks.xml")
    SHORTCUT = TEMPLATE.joinpath("shortcut.ps1")


class UrlConfig:
    CONTRIBUTION = "https://github.com/fa0311/DMMGamePlayerFastLauncher"
    RELEASE_API = "https://api.github.com/repos/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    RELEASE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    DONATE = "https://github.com/sponsors/fa0311"
    ISSUE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/issues/new"


class SchtasksConfig:
    FILE = "schtasks_v1_{0}_{1}"
    NAME = "\\Microsoft\\Windows\\DMMGamePlayerFastLauncher\\{0}"
