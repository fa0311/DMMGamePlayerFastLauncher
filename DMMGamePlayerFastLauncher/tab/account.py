import glob
from pathlib import Path
from tkinter import StringVar
from typing import TypeVar

import customtkinter as ctk
import i18n
from component.component import EntryComponent
from component.tab_menu import TabMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkOptionMenu, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm
from lib.DGPSessionV2 import DgpSessionV2
from lib.toast import ToastController, error_toast
from static.config import PathConfig
from utils.utils import children_destroy, file_create

T = TypeVar("T")


# ===== Account Sub Menu =====


class AccountTab(CTkFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])

    def create(self):
        tab = TabMenuComponent(self)
        tab.add(text=i18n.t("app.word.import"), callback=self.import_callback)
        tab.add(text=i18n.t("app.word.export"), callback=self.export_callback)
        tab.add(text=i18n.t("app.word.edit"), callback=self.edit_callback)
        tab.add(text=i18n.t("app.word.logout"), callback=self.logout_callback)
        return self

    def import_callback(self, master: CTkBaseClass):
        AccountImport(master).create().pack(expand=True, fill=ctk.BOTH)

    def export_callback(self, master: CTkBaseClass):
        AccountExport(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        AccountEdit(master).create().pack(expand=True, fill=ctk.BOTH)

    def logout_callback(self, master: CTkBaseClass):
        AccountLogout(master).create().pack(expand=True, fill=ctk.BOTH)


# ===== Account Body =====


class AccountImport(CTkScrollableFrame):
    toast: ToastController
    name: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.name = StringVar()

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.import")).pack(anchor=ctk.W)
        EntryComponent(self, text=i18n.t("app.word.filename"), var=self.name).create()
        CTkButton(self, text=i18n.t("app.word.import"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self):
        path = PathConfig.ACCOUNT.joinpath(self.name.get()).with_suffix(".bytes")
        if self.name.get() == "":
            raise Exception(i18n.t("app.error.not_entered", name=i18n.t("app.word.filename")))
        if path.exists():
            raise Exception(i18n.t("app.error.already_exists", name=i18n.t("app.word.filename")))

        with DgpSessionV2() as session:
            session.read()
            if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                raise Exception(i18n.t("app.error.not_exists", name="login_secure_id"))
            session.write_bytes(str(path))
            self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.import")))


class AccountExport(CTkScrollableFrame):
    toast: ToastController
    values: list[str]
    selected: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.values = [Path(x).stem for x in glob.glob(str(PathConfig.ACCOUNT.joinpath("*.bytes")))]
        self.selected = StringVar()

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.export")).pack(anchor=ctk.W)
        CTkLabel(self, text=i18n.t("app.word.select", name=i18n.t("app.word.file"))).pack(anchor=ctk.W)
        CTkOptionMenu(self, values=self.values, variable=self.selected).pack(anchor=ctk.W, fill=ctk.X)
        CTkButton(self, text=i18n.t("app.word.export"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self):
        path = PathConfig.ACCOUNT.joinpath(self.selected.get()).with_suffix(".bytes")
        if self.selected.get() == "":
            raise Exception(i18n.t("app.error.not_selected", name=i18n.t("app.word.file")))
        with DgpSessionV2() as session:
            session.read_bytes(str(Path(path)))
            if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                raise Exception(i18n.t("app.export.error", name="login_secure_id"))
            session.write()
            self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.export")))


class AccountEdit(CTkScrollableFrame):
    toast: ToastController
    values: list[str]
    filename: StringVar
    body: CTkFrame
    body_var: dict[str, StringVar]
    body_filename: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.values = [Path(x).stem for x in glob.glob(str(PathConfig.ACCOUNT.joinpath("*.bytes")))]
        self.filename = StringVar()
        self.body_var = {}
        self.body_filename = StringVar()

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.edit")).pack(anchor=ctk.W)
        CTkLabel(self, text=i18n.t("app.word.select", name=i18n.t("app.word.file"))).pack(anchor=ctk.W)
        CTkOptionMenu(self, values=self.values, variable=self.filename, command=self.select_callback).pack(anchor=ctk.W, fill=ctk.X)
        self.body = CTkFrame(self, fg_color=CTkm.theme["CTkToplevel"]["fg_color"], height=0)
        self.body.pack(expand=True, fill=ctk.BOTH)
        return self

    @error_toast
    def select_callback(self, value: str):
        children_destroy(self.body)
        path = PathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        self.body_filename.set(self.filename.get())
        EntryComponent(self.body, text=i18n.t("app.word.filename"), var=self.body_filename).create()

        session = DgpSessionV2()
        session.read_bytes(str(Path(path)))
        for cookie in session.cookies:
            key = f"{cookie.name}{cookie.domain}"
            self.body_var[key] = StringVar(value=cookie.value)
            EntryComponent(self.body, text=cookie.name, var=self.body_var[key]).create()
        CTkButton(self.body, text=i18n.t("app.word.save"), command=self.save_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self.body, text=i18n.t("app.word.delete"), command=self.delete_callback).pack(fill=ctk.X)

    @error_toast
    def save_callback(self):
        if self.body_filename.get() == "":
            raise Exception(i18n.t("app.error.not_entered", name=i18n.t("app.word.filename")))

        path = PathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        body_path = PathConfig.ACCOUNT.joinpath(self.body_filename.get()).with_suffix(".bytes")

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
            file_create(body_path, name=i18n.t("app.word.filename"))
            write()
            path.unlink()
            self.values.remove(self.filename.get())
            self.values.append(self.body_filename.get())
            self.filename.set(self.body_filename.get())
            children_destroy(self)
            self.create()
            self.select_callback("_")

        self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.save")))

    @error_toast
    def delete_callback(self):
        path = PathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        path.unlink()
        self.values.remove(self.filename.get())
        self.filename.set("")
        children_destroy(self)
        self.create()


class AccountLogout(CTkScrollableFrame):
    toast: ToastController

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.account.logout")).pack(anchor=ctk.W)
        CTkButton(self, text=i18n.t("app.word.logout"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self):
        with DgpSessionV2() as session:
            session.read()
            session.cookies.clear()
            session.write()
            self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.logout")))
