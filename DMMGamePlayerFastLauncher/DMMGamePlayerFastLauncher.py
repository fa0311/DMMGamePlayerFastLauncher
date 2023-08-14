import os

import customtkinter as ctk
import i18n
from app import App
from static.config import AppConfig, PathConfig
from static.loder import config_loder


def loder():
    config_loder()
    i18n.load_path.append(str(PathConfig.I18N))
    i18n.set("locale", AppConfig.DATA.lang.get())

    os.makedirs(PathConfig.ACCOUNT, exist_ok=True)
    os.makedirs(PathConfig.SHORTCUT, exist_ok=True)
    os.makedirs(PathConfig.SCHTASKS, exist_ok=True)

    ctk.set_default_color_theme(str(PathConfig.THEMES.joinpath(AppConfig.DATA.theme.get()).with_suffix(".json")))
    ctk.set_appearance_mode(AppConfig.DATA.appearance_mode.get())

    try:
        ctk.set_widget_scaling(AppConfig.DATA.window_scaling.get())
    except Exception:
        pass


App(loder).create().mainloop()
