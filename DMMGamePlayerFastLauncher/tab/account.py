from ast import List
import glob
import os
from tkinter import Entry, StringVar, filedialog
from typing import TypeVar
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
    CTkToplevel,
    CTkSegmentedButton,
    CTkOptionMenu,
)
from customtkinter import ThemeManager as CTKM
from config import Config
from lib.Toast import ToastController

from lib.Component import (
    FilePathComponent,
    TabMenuComponent,
    EntryComponent,
)
from lib.DGPSessionV2 import DgpSessionV2

T = TypeVar("T")


class AccountTab(CTkFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.create()

    def create(self):
        tab = TabMenuComponent(self)
        tab.add(text=i18n.t("app.word.import"), callback=self.import_callback)
        tab.add(text=i18n.t("app.word.export"), callback=self.export_callback)
        tab.add(text=i18n.t("app.word.logout"), callback=self.logout_callback)

    def import_callback(self, master: CTkBaseClass):
        AccountImport(master).pack(expand=True, fill=ctk.BOTH)

    def export_callback(self, master: CTkBaseClass):
        AccountExport(master).pack(expand=True, fill=ctk.BOTH)

    def logout_callback(self, master: CTkBaseClass):
        AccountLogout(master).pack(expand=True, fill=ctk.BOTH)


# class ToplevelWindow(CTkToplevel):
#     def __init__(self, master, **kwargs):
#         super().__init__(master, **kwargs)
#         self.geometry("400x300")
#         self.focus()

#         self.label = CTkLabel(self, text="ToplevelWindow")
#         self.label.pack(padx=20, pady=20)


class AccountImport(CTkScrollableFrame):
    toast: ToastController
    name: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.name = StringVar()
        self.create()

    def create(self):
        CTkLabel(self, text=i18n.t("app.description.import")).pack(anchor=ctk.W)
        EntryComponent(self, title=i18n.t("app.description.save_file"), var=self.name)
        CTkButton(self, text=i18n.t("app.word.import"), command=self.callback).pack(
            fill=ctk.X, pady=10
        )

    def callback(self):
        try:
            with DgpSessionV2() as session:
                session.read()
                id = session.cookies.get("login_secure_id", **session.cookies_kwargs)
                if id is None:
                    raise Exception("login_secure_id is None")
                session.write_bytes(
                    str(Config.ACCOUNT_PATH.joinpath(self.name.get() + ".bytes"))
                )
                text = i18n.t("app.message.success", name=i18n.t("app.word.import"))
                self.toast.info(text)
        except Exception as e:
            self.toast.error(str(e))


class AccountExport(CTkScrollableFrame):
    toast: ToastController
    selected: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.selected = StringVar()
        self.create()

    def create(self):
        CTkLabel(self, text=i18n.t("app.description.export")).pack(anchor=ctk.W)

        values = glob.glob(str(Config.ACCOUNT_PATH.joinpath("*.bytes")))

        CTkOptionMenu(
            self,
            values=values,
            command=self.selected.set,
        ).pack(anchor=ctk.W, fill=ctk.X)

        CTkButton(self, text=i18n.t("app.word.export"), command=self.callback).pack(
            fill=ctk.X, pady=10
        )

    def callback(self):
        try:
            with DgpSessionV2() as session:
                session.read_bytes(str(Path(self.selected.get())))
                session.write()
                id = session.cookies.get("login_secure_id", **session.cookies_kwargs)
                if id is None:
                    raise Exception(i18n.t("app.export.error", name="login_secure_id"))
                text = i18n.t("app.message.success", name=i18n.t("app.word.export"))
                self.toast.info(text)
        except Exception as e:
            self.toast.error(str(e))


class AccountLogout(CTkScrollableFrame):
    toast: ToastController

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.create()

    def create(self):
        CTkLabel(self, text=i18n.t("app.description.logout")).pack(anchor=ctk.W)
        CTkButton(self, text=i18n.t("app.word.logout"), command=self.callback).pack(
            fill=ctk.X, pady=10
        )

    def callback(self):
        try:
            with DgpSessionV2() as session:
                session.logout()
                text = i18n.t("app.message.success", name=i18n.t("app.word.logout"))
                self.toast.info(text)
        except Exception as e:
            self.toast.error(str(e))
