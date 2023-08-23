import argparse
import os

import customtkinter as ctk
import i18n
from app import App
from launch import GameLauncher, LanchLauncher
from static.config import AppConfig, AssetsPathConfig, DataPathConfig
from static.loder import config_loder


def loder():
    config_loder()
    i18n.load_path.append(str(AssetsPathConfig.I18N))
    i18n.set("locale", AppConfig.DATA.lang.get())

    os.makedirs(DataPathConfig.ACCOUNT, exist_ok=True)
    os.makedirs(DataPathConfig.SHORTCUT, exist_ok=True)
    os.makedirs(DataPathConfig.SCHTASKS, exist_ok=True)

    ctk.set_default_color_theme(str(AssetsPathConfig.THEMES.joinpath(AppConfig.DATA.theme.get()).with_suffix(".json")))
    ctk.set_appearance_mode(AppConfig.DATA.appearance_mode.get())

    try:
        ctk.set_widget_scaling(AppConfig.DATA.window_scaling.get())
    except Exception:
        pass


argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)
argpar.add_argument("id", default=None, nargs="?")
argpar.add_argument("--type", default="game")


try:
    arg = argpar.parse_args()
    id = arg.id
    type = arg.type
except Exception:
    exit(0)

if id is None:
    App(loder).create().mainloop()

elif type == "launcher":
    LanchLauncher(loder).create(id)

elif type == "game":
    GameLauncher(loder).create(id)
else:
    print("Unknown type")
