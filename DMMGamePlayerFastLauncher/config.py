import os
from pathlib import Path


class PathConfig:
    DATA = Path("data")
    ACCOUNT = DATA.joinpath("account")
    SHORTCUT = DATA.joinpath("shortcut")

    APPDATA = Path(os.getenv("APPDATA", default=""))
    DMMGAMEPLAYER = APPDATA.joinpath("dmmgameplayer5")

    ASSETS = Path("assets")
    I18N = ASSETS.joinpath("i18n")
    ICONS = ASSETS.joinpath("icons")
    TEXT = ASSETS.joinpath("text")

    LICENSE = TEXT.joinpath("LICENSE")


class UrlConfig:
    CONTRIBUTION = "https://github.com/fa0311/DMMGamePlayerFastLauncher"
    RELEASE = "https://api.github.com/repos/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    DONATE = "https://github.com/sponsors/fa0311"
    ISSUE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/issues/new"
