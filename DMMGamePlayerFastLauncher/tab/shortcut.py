import glob
import json
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import Frame, StringVar

import customtkinter as ctk
import i18n
from component.component import EntryComponent, FilePathComponent, LabelComponent, OptionMenuComponent
from component.tab_menu import TabMenuComponent
from component.var import PathVar
from component.variable_base import VariableBase
from customtkinter import CTkBaseClass, CTkButton, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu, CTkScrollableFrame
from lib.DGPSessionV2 import DgpSessionV2
from lib.toast import ToastController, error_toast
from static.config import PathConfig
from utils.utils import children_destroy, file_create


@dataclass
class ShortcutData(VariableBase):
    product_id: StringVar = field(default_factory=StringVar)
    game_path: PathVar = field(default_factory=PathVar)
    game_args: StringVar = field(default_factory=StringVar)


# ===== Shortcut Sub Menu =====


class ShortcutTab(CTkFrame):
    tab: TabMenuComponent

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.tab = TabMenuComponent(self)

    def create(self):
        self.tab.create()
        self.tab.add(text=i18n.t("app.tab.create"), callback=self.create_callback)
        self.tab.add(text=i18n.t("app.tab.edit"), callback=self.edit_callback)
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
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.data = ShortcutData()
        self.filename = StringVar()
        self.product_ids = [x["productId"] for x in DgpSessionV2().get_config()["contents"]]

    @error_toast
    def create(self):
        if not self.winfo_children():
            CTkLabel(self, text=i18n.t("app.shortcut.add")).pack(anchor=ctk.W)
        OptionMenuComponent(self, text=i18n.t("app.shortcut.product_id"), values=self.product_ids, variable=self.data.product_id).create()

        LabelComponent(self, text=i18n.t("app.shortcut.filename"), required=True).create()
        CTkEntry(self, textvariable=self.filename).pack(fill=ctk.X)
        FilePathComponent(self, text=i18n.t("app.shortcut.game_path"), variable=self.data.game_path).create()
        EntryComponent(self, text=i18n.t("app.shortcut.game_args"), variable=self.data.game_args).create()
        CTkButton(self, text=i18n.t("app.shortcut.save"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self, exists=False):
        if self.data.product_id.get() == "":
            raise Exception(i18n.t("app.shortcut.product_id_not_entered"))
        if self.filename.get() == "":
            raise Exception(i18n.t("app.shortcut.filename_not_entered"))

        path = PathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        if not exists:
            file_create(path, name=i18n.t("app.shortcut.filename"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data.to_dict()))
        self.toast.info(i18n.t("app.shortcut.save_success"))


class ShortcutEdit(ShortcutCreate):
    selected: StringVar
    values: list[str]

    def __init__(self, master: Frame):
        super().__init__(master)
        self.values = [x.stem for x in PathConfig.SHORTCUT.iterdir() if x.suffix == ".json"]
        self.selected = StringVar()

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.shortcut.edit")).pack(anchor=ctk.W)

        LabelComponent(self, text=i18n.t("app.shortcut.file_select")).create()
        CTkOptionMenu(self, values=self.values, variable=self.selected, command=self.option_callback).pack(fill=ctk.X)

        if self.selected.get() in self.values:
            self.data = self.read()
            super().create()
            self.filename.set(self.selected.get())
            CTkButton(self, text=i18n.t("app.shortcut.delete"), command=self.delete_callback).pack(fill=ctk.X)

        return self

    @error_toast
    def callback(self):
        path = PathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        selected = PathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
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
        path = PathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
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
        path = PathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        with open(path, "r", encoding="utf-8") as f:
            return ShortcutData.from_dict(json.load(f))
