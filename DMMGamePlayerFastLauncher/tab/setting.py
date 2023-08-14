import json
from tkinter import StringVar

import customtkinter as ctk
import i18n
from component.component import ConfirmWindow, DirectoryPathComponent, OptionMenuComponent, PaddingComponent
from customtkinter import CTkBaseClass, CTkButton, CTkScrollableFrame
from lib.toast import ToastController, error_toast
from models.setting_data import SettingData
from static.config import AppConfig, PathConfig


class SettingTab(CTkScrollableFrame):
    toast: ToastController
    data: SettingData
    lang: list[tuple[str, str]]
    lang_var: StringVar
    theme: list[str]

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.data = AppConfig.DATA
        self.lang = [(y, i18n.t("app.language", locale=y)) for y in [x.name.split(".")[1] for x in PathConfig.I18N.iterdir()]]
        self.lang_var = StringVar(value=dict(self.lang)[self.data.lang.get()])

        self.theme = [x.stem for x in PathConfig.THEMES.iterdir()]

    def create(self):
        DirectoryPathComponent(self, text=i18n.t("app.setting.dmm_game_player_folder"), variable=self.data.dmm_game_player_folder).create()
        OptionMenuComponent(self, text=i18n.t("app.setting.lang"), values=[x[1] for x in self.lang], variable=self.lang_var).create()
        OptionMenuComponent(self, text=i18n.t("app.setting.theme"), values=self.theme, variable=self.data.theme).create()
        OptionMenuComponent(self, text=i18n.t("app.setting.appearance"), values=["light", "dark", "system"], variable=self.data.appearance_mode).create()

        PaddingComponent(self, height=10).create()
        CTkButton(self, text=i18n.t("app.setting.save"), command=self.save_callback).pack(fill=ctk.X, pady=10)

        command = lambda: ConfirmWindow(self, command=self.delete_callback, text=i18n.t("app.setting.confirm_reset")).create()
        CTkButton(self, text=i18n.t("app.setting.reset_all_settings"), command=command).pack(fill=ctk.X, pady=10)

        return self

    @error_toast
    def save_callback(self):
        self.data.lang.set([x[0] for x in self.lang if x[1] == self.lang_var.get()][0])
        with open(PathConfig.APP_CONFIG, "w+", encoding="utf-8") as f:
            json.dump(self.data.to_dict(), f)
        self.reload_callback()

    @error_toast
    def reload_callback(self):
        from app import App

        app = self.winfo_toplevel()
        assert isinstance(app, App)
        app.loder()
        app.create()
        self.toast.info(i18n.t("app.setting.save_success"))

    @error_toast
    def delete_callback(self):
        PathConfig.APP_CONFIG.unlink()
        self.reload_callback()
