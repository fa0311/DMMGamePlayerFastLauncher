import os
from pathlib import Path


class Env:
    DEVELOP: bool = os.environ.get("ENV") == "DEVELOP"
    APPDATA: Path = Path(os.getenv("APPDATA", default=""))
    DEFAULT_DMM_GAME_PLAYER_FOLDER: Path = APPDATA.joinpath("dmmgameplayer5")
