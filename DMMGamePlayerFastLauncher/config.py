from pathlib import Path


class Config:
    DATA_PATH = Path("data")
    ACCOUNT_PATH = DATA_PATH.joinpath("account")
