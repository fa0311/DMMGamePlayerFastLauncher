import os
from pathlib import Path

import requests
from static.config import UrlConfig
from windows_pathlib import WindowsPathlib


class Env:
    VERSION = "v5.0.1"
    RELEASE_VERSION = requests.get(UrlConfig.RELEASE_API).json()["tag_name"]

    DEVELOP: bool = os.environ.get("ENV") == "DEVELOP"
    APPDATA: Path = Path(os.getenv("APPDATA", default=""))
    PROGURAM_FILES: Path = Path(os.getenv("PROGRAMFILES", default=""))
    DESKTOP: Path = WindowsPathlib.desktop()

    DEFAULT_DMM_GAME_PLAYER_PROGURAM_FOLDER: Path = PROGURAM_FILES.joinpath("DMMGamePlayer")
    DEFAULT_DMM_GAME_PLAYER_DATA_FOLDER: Path = APPDATA.joinpath("dmmgameplayer5")

    SYSTEM_ROOT = Path(os.getenv("SYSTEMROOT", default=""))
    SYSTEM32 = SYSTEM_ROOT.joinpath("System32")
    SCHTASKS = SYSTEM32.joinpath("schtasks.exe")
