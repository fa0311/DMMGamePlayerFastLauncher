import argparse
import logging
import os

import customtkinter as ctk
import i18n
from app import App
from component.logger import TkinkerHandler, TkinkerLogger
from launch import GameLauncher, LanchLauncher
from static.config import AppConfig, AssetsPathConfig, DataPathConfig
from static.loder import config_loder


def loder(master: LanchLauncher):
    config_loder()
    i18n.load_path.append(str(AssetsPathConfig.I18N))
    i18n.set("locale", AppConfig.DATA.lang.get())

    if AppConfig.DATA.debug_window.get() and not logging.getLogger().hasHandlers():
        handler = TkinkerHandler(TkinkerLogger(master)).create()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    if AppConfig.DATA.proxy_http.get() != "":
        os.environ["HTTP_PROXY"] = AppConfig.DATA.proxy_http.get()
    if AppConfig.DATA.proxy_https.get() != "":
        os.environ["HTTPS_PROXY"] = AppConfig.DATA.proxy_https.get()

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
    lanch = LanchLauncher(loder).create()
    lanch.thread(id)
    lanch.mainloop()

elif type == "game":
    lanch = GameLauncher(loder).create()
    lanch.thread(id)
    lanch.mainloop()
else:
    raise Exception("type error")
