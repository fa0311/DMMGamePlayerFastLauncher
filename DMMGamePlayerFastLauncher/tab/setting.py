from tkinter import StringVar

from config import PathConf
from customtkinter import CTkBaseClass, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm
from lib.component import DirectoryPathComponent

import i18n


class SettingTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])

    def create(self):
        path = PathConf.DMMGAMEPLAYER.joinpath("dmmgameplayer5")
        DirectoryPathComponent(
            self,
            text=i18n.t("app.detail.setting.dmm_game_player_folder"),
            var=StringVar(value=str(path)),
        ).create()
        return self
