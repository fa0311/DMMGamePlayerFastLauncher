import glob
from tkinter import StringVar
from typing import TypeVar
import i18n
from pathlib import Path

import customtkinter as ctk
from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkScrollableFrame,
    CTkBaseClass,
    CTkOptionMenu,
)
from customtkinter import ThemeManager as CTKM
from config import PathConf
from lib.Toast import ToastController

from lib.Component import (
    TabMenuComponent,
    EntryComponent,
)
from lib.DGPSessionV2 import DgpSessionV2

T = TypeVar("T")


class AccountTab(CTkFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])

    def create(self):
        tab = TabMenuComponent(self)
        tab.add(text=i18n.t("app.word.import"), callback=self.import_callback)
        tab.add(text=i18n.t("app.word.export"), callback=self.export_callback)
        tab.add(text=i18n.t("app.word.logout"), callback=self.logout_callback)
        return self

    def import_callback(self, master: CTkBaseClass):
        AccountImport(master).create().pack(expand=True, fill=ctk.BOTH)

    def export_callback(self, master: CTkBaseClass):
        AccountExport(master).create().pack(expand=True, fill=ctk.BOTH)

    def logout_callback(self, master: CTkBaseClass):
        AccountLogout(master).create().pack(expand=True, fill=ctk.BOTH)


class AccountImport(CTkScrollableFrame):
    toast: ToastController
    name: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.name = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.import")).pack(anchor=ctk.W)
        EntryComponent(self, text=i18n.t("app.description.save_file"), var=self.name).create()
        CTkButton(self, text=i18n.t("app.word.import"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    def callback(self):
        try:
            if self.name.get() == "":
                raise Exception(i18n.t("app.error.not_entered", name=i18n.t("app.description.save_file")))

            with DgpSessionV2() as session:
                session.read()
                if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                    raise Exception(i18n.t("app.error.not_exists", name="login_secure_id"))
                path = PathConf.ACCOUNT.joinpath(self.name.get()).with_suffix(".bytes")
                session.write_bytes(str(path))
                self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.import")))
        except Exception as e:
            self.toast.error(str(e))


class AccountExport(CTkScrollableFrame):
    toast: ToastController
    selected: StringVar
    values: list[str]

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)

        self.values = glob.glob(str(PathConf.ACCOUNT.joinpath("*.bytes")))
        self.selected = StringVar(value=self.values[0] if self.values else None)

    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.export")).pack(anchor=ctk.W)

        CTkLabel(self, text=i18n.t("app.description.select", name=i18n.t("app.word.file"))).pack(anchor=ctk.W)
        CTkOptionMenu(
            self,
            values=self.values,
            variable=self.selected,
        ).pack(anchor=ctk.W, fill=ctk.X)

        CTkButton(self, text=i18n.t("app.word.export"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    def callback(self):
        try:
            with DgpSessionV2() as session:
                session.read_bytes(str(Path(self.selected.get())))
                if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                    raise Exception(i18n.t("app.export.error", name="login_secure_id"))
                session.write()
                self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.export")))
        except Exception as e:
            self.toast.error(str(e))


class AccountLogout(CTkScrollableFrame):
    toast: ToastController

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)

    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.logout")).pack(anchor=ctk.W)
        CTkButton(self, text=i18n.t("app.word.logout"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    def callback(self):
        try:
            with DgpSessionV2() as session:
                session.read()
                session.cookies.clear()
                session.write()
                self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.logout")))
        except Exception as e:
            self.toast.error(str(e))
