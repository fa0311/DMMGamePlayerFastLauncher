import os
from pathlib import Path


class Env:
    DEVELOP: bool = os.environ.get("ENV") == "DEVELOP"
    APPDATA: Path = Path(os.getenv("APPDATA", default=""))
    PROGURAM_FILES: Path = Path(os.getenv("PROGRAMFILES", default=""))
    DEFAULT_DMM_GAME_PLAYER_PROGURAM_FOLDER: Path = PROGURAM_FILES.joinpath("DMMGamePlayer")
    DEFAULT_DMM_GAME_PLAYER_DATA_FOLDER: Path = APPDATA.joinpath("dmmgameplayer5")

    SYSTEM_ROOT = Path(os.getenv("SYSTEMROOT", default=""))
    SYSTEM32 = SYSTEM_ROOT.joinpath("System32")
    SCHTASKS = SYSTEM32.joinpath("schtasks.exe")
