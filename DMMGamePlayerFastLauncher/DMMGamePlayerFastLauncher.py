import argparse
import logging
import os
import sys
import time
from tkinter import font

import customtkinter as ctk
import i18n
from app import App
from coloredlogs import ColoredFormatter
from component.logger import LoggingHandlerMask, StyleScheme, TkinkerLogger
from customtkinter import ThemeManager
from launch import GameLauncher, GameLauncherUac, LanchLauncher
from lib.DGPSessionV2 import DgpSessionV2
from models.setting_data import AppConfig
from static.config import AssetsPathConfig, DataPathConfig, SchtasksConfig, UrlConfig
from static.env import Env
from static.loder import config_loder, config_migrate
from tkinter_colored_logging_handlers.main import LoggingHandler


def loder(master: LanchLauncher):
    DataPathConfig.ACCOUNT.mkdir(exist_ok=True, parents=True)
    DataPathConfig.ACCOUNT_SHORTCUT.mkdir(exist_ok=True, parents=True)
    DataPathConfig.SHORTCUT.mkdir(exist_ok=True, parents=True)
    DataPathConfig.SCHTASKS.mkdir(exist_ok=True, parents=True)
    DataPathConfig.BROWSER_PROFILE.mkdir(exist_ok=True, parents=True)
    DataPathConfig.BROWSER_CONFIG.mkdir(exist_ok=True, parents=True)

    config_loder()
    i18n.load_path.append(str(AssetsPathConfig.I18N))
    i18n.set("locale", AppConfig.DATA.lang.get())

    handlers = []

    if AppConfig.DATA.output_logfile.get() and not any([isinstance(x, logging.FileHandler) for x in logging.getLogger().handlers]):
        DataPathConfig.LOG.mkdir(exist_ok=True, parents=True)
        handler = logging.FileHandler(DataPathConfig.LOG.joinpath(f"{time.strftime('%Y%m%d%H%M%S')}.log"), encoding="utf-8")
        handlers.append(handler)

    if AppConfig.DATA.debug_window.get() and not any([isinstance(x, LoggingHandler) for x in logging.getLogger().handlers]):
        handle = LoggingHandlerMask if AppConfig.DATA.mask_token.get() else LoggingHandler
        handler = handle(TkinkerLogger(master).create().box, scheme=StyleScheme)
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

    config_migrate()

    if AppConfig.DATA.proxy_all.get() != "":
        os.environ["ALL_PROXY"] = AppConfig.DATA.proxy_all.get()
    if AppConfig.DATA.dmm_proxy_all.get() != "":
        DgpSessionV2.PROXY["http"] = AppConfig.DATA.dmm_proxy_all.get()
        DgpSessionV2.PROXY["https"] = AppConfig.DATA.dmm_proxy_all.get()

    ctk.set_default_color_theme(str(AssetsPathConfig.THEMES.joinpath(AppConfig.DATA.theme.get()).with_suffix(".json")))

    additional_theme = {
        "MenuComponent": {"text_color": ["#000000", "#ffffff"]},
        "LabelComponent": {"fg_color": ["#F9F9FA", "#343638"], "required_color": ["red", "red"]},
        "CheckBoxComponent": {"checkbox_width": 16, "checkbox_height": 16, "border_width": 2},
    }
    for key, value in additional_theme.items():
        ThemeManager.theme[key] = value

    if AppConfig.DATA.theme_font.get() == "i18n":
        i18n_font = i18n.t("app.font.main")
        if i18n_font not in font.families():
            logging.warning(f"Font {i18n_font} not found")
        ThemeManager.theme["CTkFont"]["family"] = i18n_font
    elif AppConfig.DATA.theme_font.get() == "os":
        os_default_font = font.nametofont("TkDefaultFont").config()
        if os_default_font is None:
            logging.warning(f"Font {os_default_font} not found")
        else:
            ThemeManager.theme["CTkFont"]["family"] = os_default_font["family"]

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

elif type == "force-user-game":
    GameLauncherUac.wait([id, "--type", "kill-game"])
    lanch = GameLauncher(loder).create()
    lanch.thread(id, force_non_uac=True)
    lanch.mainloop()

elif type == "kill-game":
    lanch = GameLauncher(loder).create()
    lanch.thread(id, kill=True)
    lanch.mainloop()

else:
    raise Exception("type error")
