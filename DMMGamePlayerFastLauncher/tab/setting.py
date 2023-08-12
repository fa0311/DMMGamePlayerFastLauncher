from tkinter import StringVar

from customtkinter import (
    CTkScrollableFrame,
    CTkBaseClass,
)
from customtkinter import ThemeManager as CTKM
from config import PathConf

from lib.Component import DirectoryPathComponent


class SettingTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])

    def create(self):
        path = PathConf.DMMGAMEPLAYER.joinpath("dmmgameplayer5")
        DirectoryPathComponent(
            self,
            text="DMMGamePlayerのフォルダ",
            var=StringVar(value=str(path)),
        ).create()
        return self
