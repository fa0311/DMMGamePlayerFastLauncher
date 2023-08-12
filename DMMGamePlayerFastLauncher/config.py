import os
from pathlib import Path


class PathConfig:
    DATA = Path("data")
    ACCOUNT = DATA.joinpath("account")
    SHORTCUT = DATA.joinpath("shortcut")

    APPDATA = Path(os.getenv("APPDATA", default=""))
    DMMGAMEPLAYER = APPDATA.joinpath("dmmgameplayer5")


class UrlConfig:
    CONTRIBUTION = "https://github.com/fa0311/DMMGamePlayerFastLauncher"
    RELEASE = "https://api.github.com/repos/fa0311/DMMGamePlayerFastLauncher/releases/latest"
    DONATE = "https://github.com/sponsors/fa0311"
    ISSUE = "https://github.com/fa0311/DMMGamePlayerFastLauncher/issues/new"
