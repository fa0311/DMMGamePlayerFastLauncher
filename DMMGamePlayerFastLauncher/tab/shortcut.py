import glob
import json
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import Frame, StringVar

import customtkinter as ctk
from config import PathConf
from customtkinter import CTkBaseClass, CTkButton, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm
from lib.component import EntryComponent, FilePathComponent, TabMenuComponent, VariableBase, children_destroy, file_create
from lib.DGPSessionV2 import DgpSessionV2
from lib.toast import ToastController, error_toast

import i18n


@dataclass
class ShortcutData(VariableBase):
    product_id: StringVar = field(default_factory=StringVar)
    game_path: StringVar = field(default_factory=StringVar)
    game_args: StringVar = field(default_factory=StringVar)


# ===== Shortcut Sub Menu =====


class ShortcutTab(CTkFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])

    def create(self):
        tab = TabMenuComponent(self)
        tab.add(text=i18n.t("app.word.create"), callback=self.create_callback)
        tab.add(text=i18n.t("app.word.edit"), callback=self.edit_callback)
        return self

    def create_callback(self, master: CTkBaseClass):
        ShortcutCreate(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        ShortcutEdit(master).create().pack(expand=True, fill=ctk.BOTH)


# ===== Shortcut Body =====


class ShortcutCreate(CTkScrollableFrame):
    toast: ToastController
    data: ShortcutData
    filename: StringVar
    product_ids: list[str]

    def __init__(self, master: Frame):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.data = ShortcutData()
        self.filename = StringVar()
        self.product_ids = [x["productId"] for x in DgpSessionV2().get_config()["contents"]]

    @error_toast
    def create(self):
        if not self.winfo_children():
            CTkLabel(self, text=i18n.t("app.detail.shortcut.add")).pack(anchor=ctk.W)
        CTkLabel(self, text=i18n.t("app.description.select", name=i18n.t("app.word.product_id"))).pack(anchor=ctk.W)
        CTkOptionMenu(self, values=self.product_ids, variable=self.data.product_id).pack(fill=ctk.X)
        CTkLabel(self, text=i18n.t("app.word.filename")).pack(anchor=ctk.W)
        CTkEntry(self, textvariable=self.filename).pack(fill=ctk.X)
        FilePathComponent(self, text=i18n.t("app.word.game_path"), var=self.data.game_path).create()
        EntryComponent(self, text=i18n.t("app.word.game_args"), var=self.data.game_args).create()
        CTkButton(self, text=i18n.t("app.word.save"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self, exists=False):
        if self.data.product_id.get() == "":
            raise Exception(i18n.t("app.error.not_entered", name=i18n.t("app.word.product_id")))
        if self.filename.get() == "":
            raise Exception(i18n.t("app.error.not_entered", name=i18n.t("app.word.filename")))

        path = PathConf.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        if not exists:
            file_create(path, name=i18n.t("app.word.filename"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data.to_dict()))
        self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.save")))


class ShortcutEdit(ShortcutCreate):
    selected: StringVar
    values: list[str]

    def __init__(self, master: Frame):
        super().__init__(master)
        self.values = [Path(x).stem for x in glob.glob(str(PathConf.SHORTCUT.joinpath("*.json")))]
        self.selected = StringVar()

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.detail.shortcut.edit")).pack(anchor=ctk.W)
        CTkLabel(self, text=i18n.t("app.description.select", name=i18n.t("app.word.file"))).pack(anchor=ctk.W)
        CTkOptionMenu(self, values=self.values, variable=self.selected, command=self.option_callback).pack(fill=ctk.X)

        if self.selected.get() in self.values:
            self.data = self.read()
            super().create()
            self.filename.set(self.selected.get())
            CTkButton(self, text=i18n.t("app.word.delete"), command=self.delete_callback).pack(fill=ctk.X)

        return self

    @error_toast
    def callback(self):
        path = PathConf.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        selected = PathConf.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        if path == selected:
            super().callback(exists=True)
        else:
            super().callback()
            selected.unlink()
            self.values.remove(self.selected.get())
            self.values.append(self.filename.get())
            self.selected.set(self.filename.get())
            self.option_callback("_")

    @error_toast
    def delete_callback(self):
        path = PathConf.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        path.unlink()
        self.values.remove(self.selected.get())
        self.selected.set("")
        self.option_callback("_")

    @error_toast
    def option_callback(self, _: str):
        children_destroy(self)
        self.create()

    @error_toast
    def read(self) -> ShortcutData:
        path = PathConf.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        with open(path, "r", encoding="utf-8") as f:
            return ShortcutData.from_dict(json.load(f))
