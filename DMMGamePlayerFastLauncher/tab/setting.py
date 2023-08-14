import json
from tkinter import StringVar

import customtkinter as ctk
import i18n
from component.component import ConfirmWindow, DirectoryPathComponent, OptionMenuComponent, PaddingComponent
from component.tab_menu import TabMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkScrollableFrame
from lib.process_manager import Schtasks
from lib.toast import ToastController, error_toast
from models.setting_data import SettingData
from static.config import AppConfig, PathConfig


class SettingTab(CTkFrame):
    tab: TabMenuComponent

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.tab = TabMenuComponent(self)

    def create(self):
        self.tab.create()
        self.tab.add(text=i18n.t("app.tab.edit"), callback=self.edit_callback)
        self.tab.add(text=i18n.t("app.tab.uac"), callback=self.uac_callback)
        return self

    def edit_callback(self, master: CTkBaseClass):
        SettingEditTab(master).create().pack(expand=True, fill=ctk.BOTH)

    def uac_callback(self, master: CTkBaseClass):
        SettingUacTab(master).create().pack(expand=True, fill=ctk.BOTH)


class SettingEditTab(CTkScrollableFrame):
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

    @error_toast
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


class SettingUacTab(CTkScrollableFrame):
    toast: ToastController

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.setting.uac_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        CTkButton(self, text=i18n.t("app.setting.check_schedule"), command=self.check_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text=i18n.t("app.setting.set_schedule"), command=self.elevation_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text=i18n.t("app.setting.delete_schedule"), command=self.delete_callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def check_callback(self):
        if Schtasks().check():
            self.toast.info(i18n.t("app.setting.uac_already_elevated"))
        else:
            self.toast.info(i18n.t("app.setting.uac_not_elevated"))

    @error_toast
    def elevation_callback(self):
        Schtasks().set()
        self.toast.info(i18n.t("app.setting.uac_elevated"))

    @error_toast
    def delete_callback(self):
        Schtasks().delete()
        self.toast.info(i18n.t("app.setting.uac_deleted"))
