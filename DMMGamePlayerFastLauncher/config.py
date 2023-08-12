import os
from pathlib import Path


class PathConf:
    DATA = Path("data")
    ACCOUNT = DATA.joinpath("account")
    SHORTCUT = DATA.joinpath("shortcut")

    APPDATA = Path(os.getenv("APPDATA", default=""))
    DMMGAMEPLAYER = APPDATA.joinpath("dmmgameplayer5")
