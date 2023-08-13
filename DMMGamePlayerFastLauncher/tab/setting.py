import i18n
from component.component import DirectoryPathComponent
from customtkinter import CTkBaseClass, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm
from models.setting_data import SettingData
from static.config import AppConfig


class SettingTab(CTkScrollableFrame):
    data: SettingData

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.data = AppConfig.DATA

    def create(self):
        DirectoryPathComponent(self, text=i18n.t("app.detail.setting.dmm_game_player_folder"), var=self.data.dmm_game_player_folder).create()
        return self
