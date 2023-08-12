from ast import List
import os
from tkinter import Entry, StringVar, filedialog
import i18n
from pathlib import Path

import customtkinter as ctk
from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    CTkScrollbar,
    CTkScrollableFrame,
    CTkBaseClass,
)
from customtkinter import ThemeManager as CTKM

from lib.Component import FilePathComponent, TabMenuComponent


class SettingTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.create()

    def create(self):
        appdata: Path = Path(os.getenv("APPDATA", default=""))
        FilePathComponent(
            self,
            title="DMMGamePlayerのパス",
            defaultPath=appdata.joinpath("dmmgameplayer5"),
        )
        FilePathComponent(
            self,
            title="DMMGamePlayerFastLauncherのパス",
            defaultPath=appdata.joinpath("dmmgameplayer5"),
        )
