from pathlib import Path
from tkinter import StringVar
from typing import TypeVar

import customtkinter as ctk
import i18n
from component.component import EntryComponent, OptionMenuComponent
from component.tab_menu import TabMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkScrollableFrame
from lib.DGPSessionV2 import DgpSessionV2
from lib.toast import ToastController, error_toast
from static.config import DataPathConfig
from utils.utils import children_destroy, file_create

T = TypeVar("T")


# ===== Account Sub Menu =====


class AccountTab(CTkFrame):
    tab: TabMenuComponent

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.tab = TabMenuComponent(self)

    def create(self):
        self.tab.create()
        self.tab.add(text=i18n.t("app.tab.import"), callback=self.import_callback)
        self.tab.add(text=i18n.t("app.tab.edit"), callback=self.edit_callback)
        return self

    def import_callback(self, master: CTkBaseClass):
        AccountImport(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        AccountEdit(master).create().pack(expand=True, fill=ctk.BOTH)


# ===== Account Body =====


class AccountImport(CTkScrollableFrame):
    toast: ToastController
    name: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.name = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.account.import_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        filename_tooltip = i18n.t("app.account.filename_tooltip")
        EntryComponent(self, text=i18n.t("app.account.filename"), tooltip=filename_tooltip, required=True, variable=self.name).create()
        CTkButton(self, text=i18n.t("app.account.import"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self):
        path = DataPathConfig.ACCOUNT.joinpath(self.name.get()).with_suffix(".bytes")
        if self.name.get() == "":
            raise Exception(i18n.t("app.account.filename_not_entered"))
        if path.exists():
            raise Exception(i18n.t("app.account.filename_already_exists"))

        with DgpSessionV2() as session:
            session.read()
            if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                raise Exception(i18n.t("app.account.import_error"))
            session.write_bytes(str(path))
            session.cookies.clear()
            session.write()
            self.toast.info(i18n.t("app.account.import_success"))


class AccountEdit(CTkScrollableFrame):
    toast: ToastController
    values: list[str]
    filename: StringVar
    body: CTkFrame
    body_var: dict[str, StringVar]
    body_filename: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.values = [x.stem for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]
        self.filename = StringVar()
        self.body = CTkFrame(self, fg_color="transparent", height=0)
        self.body_var = {}
        self.body_filename = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.account.edit_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        OptionMenuComponent(self, text=i18n.t("app.account.file_select"), values=self.values, variable=self.filename, command=self.select_callback).create()
        self.body.pack(expand=True, fill=ctk.BOTH)
        return self

    @error_toast
    def select_callback(self, value: str):
        children_destroy(self.body)
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        self.body_filename.set(self.filename.get())
        EntryComponent(self.body, text=i18n.t("app.account.filename"), variable=self.body_filename).create()

        session = DgpSessionV2()
        session.read_bytes(str(Path(path)))
        for cookie in session.cookies:
            key = f"{cookie.name}{cookie.domain}"
            self.body_var[key] = StringVar(value=cookie.value)
            EntryComponent(self.body, text=cookie.name, variable=self.body_var[key]).create()
        CTkButton(self.body, text=i18n.t("app.account.save"), command=self.save_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self.body, text=i18n.t("app.account.delete"), command=self.delete_callback).pack(fill=ctk.X)

    @error_toast
    def save_callback(self):
        if self.body_filename.get() == "":
            raise Exception(i18n.t("app.account.filename_not_entered"))

        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        body_path = DataPathConfig.ACCOUNT.joinpath(self.body_filename.get()).with_suffix(".bytes")

        def write():
            session = DgpSessionV2()
            session.read_bytes(str(Path(path)))
            for cookie in session.cookies:
                key = f"{cookie.name}{cookie.domain}"
                if self.body_var[key]:
                    cookie.value = self.body_var[key].get()
            session.write_bytes(str(Path(body_path)))

        if path == body_path:
            write()
        else:
            file_create(body_path, name=i18n.t("app.account.filename"))
            write()
            path.unlink()
            self.values.remove(self.filename.get())
            self.values.append(self.body_filename.get())
            self.filename.set(self.body_filename.get())
            children_destroy(self)
            self.create()
            self.select_callback("_")

        self.toast.info(i18n.t("app.account.save_success"))

    @error_toast
    def delete_callback(self):
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        path.unlink()
        self.values.remove(self.filename.get())
        self.filename.set("")
        children_destroy(self)
        self.create()
