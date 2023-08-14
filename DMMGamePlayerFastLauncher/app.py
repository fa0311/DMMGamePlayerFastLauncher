import sys
from typing import Callable

import customtkinter as ctk
import i18n
from component.tab_menu import TabMenuComponent
from customtkinter import CTk, CTkFrame
from static.config import PathConfig
from tab.account import AccountTab
from tab.help import HelpTab
from tab.home import HomeTab
from tab.setting import SettingTab
from tab.shortcut import ShortcutTab


class App(CTk):
    loder: Callable
    tab: TabMenuComponent

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.iconbitmap(default=str(PathConfig.MAIN_ICON))
        self.loder = loder
        self.tab = TabMenuComponent(self)
        loder()

    def create(self):
        self.tab.create()
        self.tab.add(text=i18n.t("app.tab.home"), callback=self.home_callback)
        self.tab.add(text=i18n.t("app.tab.shortcut"), callback=self.shortcut_callback)
        self.tab.add(text=i18n.t("app.tab.account"), callback=self.account_callback)
        self.tab.add(text=i18n.t("app.tab.setting"), callback=self.setting_callback)
        self.tab.add(text=i18n.t("app.tab.help"), callback=self.help_callback)
        return self

    def home_callback(self, master: CTkFrame):
        HomeTab(master).create().pack(expand=True, fill=ctk.BOTH)

    def shortcut_callback(self, master: CTkFrame):
        ShortcutTab(master).create().pack(expand=True, fill=ctk.BOTH)

    def account_callback(self, master: CTkFrame):
        AccountTab(master).create().pack(expand=True, fill=ctk.BOTH)

    def setting_callback(self, master):
        SettingTab(master).create().pack(expand=True, fill=ctk.BOTH)

    def help_callback(self, master):
        HelpTab(master).create().pack(expand=True, fill=ctk.BOTH)
