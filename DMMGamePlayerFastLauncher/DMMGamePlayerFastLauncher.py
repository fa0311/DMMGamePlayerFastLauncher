import argparse
import logging
import os
import sys
import time

import customtkinter as ctk
import i18n
from app import App
from coloredlogs import ColoredFormatter
from component.logger import StyleScheme, TkinkerLogger
from launch import GameLauncher, LanchLauncher
from models.setting_data import AppConfig
from static.config import AssetsPathConfig, DataPathConfig, SchtasksConfig, UrlConfig
from static.env import Env
from static.loder import config_loder
from tkinter_colored_logging_handlers import LoggingHandler


def loder(master: LanchLauncher):
    DataPathConfig.ACCOUNT.mkdir(exist_ok=True, parents=True)
    DataPathConfig.ACCOUNT_SHORTCUT.mkdir(exist_ok=True, parents=True)
    DataPathConfig.SHORTCUT.mkdir(exist_ok=True, parents=True)
    DataPathConfig.SCHTASKS.mkdir(exist_ok=True, parents=True)

    config_loder()
    i18n.load_path.append(str(AssetsPathConfig.I18N))
    i18n.set("locale", AppConfig.DATA.lang.get())

    handlers = []

    if AppConfig.DATA.output_logfile.get() and not any([isinstance(x, logging.FileHandler) for x in logging.getLogger().handlers]):
        DataPathConfig.LOG.mkdir(exist_ok=True, parents=True)
        handler = logging.FileHandler(DataPathConfig.LOG.joinpath(f"{time.strftime('%Y%m%d%H%M%S')}.log"), encoding="utf-8")
        handlers.append(handler)

    if AppConfig.DATA.debug_window.get() and not any([isinstance(x, LoggingHandler) for x in logging.getLogger().handlers]):
        handler = LoggingHandler(TkinkerLogger(master).create().box, scheme=StyleScheme)
        handler.setFormatter(ColoredFormatter("[%(levelname)s] [%(asctime)s] %(message)s"))
        handlers.append(handler)

    if not any([isinstance(x, logging.StreamHandler) for x in logging.getLogger().handlers]):
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter("[%(levelname)s] [%(asctime)s] %(message)s"))
        handlers.append(handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)

    logging.debug("==================================================")
    logging.debug("===== DMMGamePlayerFastLauncher Environment =====")
    logging.debug("==================================================")
    logging.debug(Env.dump())
    logging.debug(AppConfig.DATA.to_dict())
    logging.debug(AppConfig.DEVICE.to_dict())
    logging.debug(DataPathConfig.dump())
    logging.debug(AssetsPathConfig.dump())
    logging.debug(UrlConfig.dump())
    logging.debug(SchtasksConfig.dump())
    logging.debug(sys.argv)
    logging.debug("==================================================")
    logging.debug("==================================================")
    logging.debug("==================================================")

    if AppConfig.DATA.proxy_http.get() != "":
        os.environ["HTTP_PROXY"] = AppConfig.DATA.proxy_http.get()
    if AppConfig.DATA.proxy_https.get() != "":
        os.environ["HTTPS_PROXY"] = AppConfig.DATA.proxy_https.get()

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
