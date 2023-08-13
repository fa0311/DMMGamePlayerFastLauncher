import json
from tkinter import StringVar

import customtkinter as ctk
import i18n
from component.component import DirectoryPathComponent, OptionMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm
from models.setting_data import SettingData
from static.config import AppConfig, PathConfig


class SettingTab(CTkScrollableFrame):
    data: SettingData
    lang: list[tuple[str, str]]
    lang_var: StringVar
    theme: list[str]

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.data = AppConfig.DATA
        self.lang = [(y, i18n.t("app.language", locale=y)) for y in [x.name.split(".")[1] for x in PathConfig.I18N.iterdir()]]
        self.lang_var = StringVar(value=dict(self.lang)[self.data.lang.get()])

        self.theme = [x.stem for x in PathConfig.THEMES.iterdir()]

    def create(self):
        DirectoryPathComponent(self, text=i18n.t("app.detail.setting.dmm_game_player_folder"), variable=self.data.dmm_game_player_folder).create()
        OptionMenuComponent(self, text="言語", values=[x[1] for x in self.lang], variable=self.lang_var).create()
        OptionMenuComponent(self, text="テーマ", values=self.theme, variable=self.data.theme).create()

        OptionMenuComponent(self, text="外観", values=["light", "dark", "system"], variable=self.data.appearance_mode).create()

        CTkButton(self, text=i18n.t("app.word.save"), command=self.save_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text=i18n.t("app.word.reload"), command=self.reload_callback).pack(fill=ctk.X, pady=10)

        return self

    def save_callback(self):
        self.data.lang.set([x[0] for x in self.lang if x[1] == self.lang_var.get()][0])
        with open(PathConfig.APP_CONFIG, "w+", encoding="utf-8") as f:
            json.dump(self.data.to_dict(), f)

    def reload_callback(self):
        self.winfo_toplevel().destroy()
