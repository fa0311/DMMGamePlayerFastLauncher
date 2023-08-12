from dataclasses import dataclass, field
import glob
from pathlib import Path
from tkinter import Frame, StringVar
import i18n

import customtkinter as ctk
from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    CTkScrollableFrame,
    CTkBaseClass,
    CTkOptionMenu,
)
from customtkinter import ThemeManager as CTKM
from config import PathConf
from lib.Toast import ToastController

from lib.Component import (
    FilePathComponent,
    TabMenuComponent,
    EntryComponent,
)
from lib.DGPSessionV2 import DgpSessionV2

import json


@dataclass
class ShortcutData:
    product_id: StringVar = field(default_factory=StringVar)
    game_path: StringVar = field(default_factory=StringVar)
    game_args: StringVar = field(default_factory=StringVar)

    def to_dict(self) -> dict[str, str]:
        return {
            "product_id": self.product_id.get(),
            "game_path": self.game_path.get(),
            "game_args": self.game_args.get(),
        }

    @staticmethod
    def from_dict(obj: dict[str, str]) -> "ShortcutData":
        item = {k: StringVar(value=v) for k, v in obj.items()}
        return ShortcutData(**item)


class ShortcutTab(CTkFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])

    def create(self):
        tab = TabMenuComponent(self)
        tab.add(text=i18n.t("app.word.create"), callback=self.create_callback)
        tab.add(text=i18n.t("app.word.edit"), callback=self.edit_callback)
        return self

    def create_callback(self, master: CTkBaseClass):
        ShortcutAdd(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        ShortcutEdit(master).create().pack(expand=True, fill=ctk.BOTH)


class ShortcutAdd(CTkScrollableFrame):
    toast: ToastController
    data: ShortcutData
    filename: StringVar
    product_ids: list[str]

    def __init__(self, master: Frame):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.toast = ToastController(self)
        self.data = ShortcutData()
        self.filename = StringVar(value="main")
        self.product_ids = [x["productId"] for x in DgpSessionV2().get_config()["contents"]]
        self.data.product_id.set(self.product_ids[0])

    def create(self):
        CTkLabel(self, text="productIdの選択").pack(anchor=ctk.W)
        CTkOptionMenu(self, values=self.product_ids, variable=self.data.product_id).pack(fill=ctk.X)
        CTkLabel(self, text=i18n.t("app.word.filename")).pack(anchor=ctk.W)
        CTkEntry(self, textvariable=self.filename).pack(fill=ctk.X)
        FilePathComponent(self, text=i18n.t("app.word.game_path"), var=self.data.game_path).create()
        EntryComponent(self, text=i18n.t("app.word.game_args"), var=self.data.game_args).create()
        CTkButton(self, text=i18n.t("app.word.save"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    def callback(self):
        try:
            path = PathConf.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
            open(path, "a+").close()
            with open(path, "w") as f:
                f.write(json.dumps(self.data.to_dict()))
            self.toast.info(i18n.t("app.message.success", name=i18n.t("app.word.save")))

        except Exception as e:
            self.toast.error(str(e))


class ShortcutEdit(ShortcutAdd):
    selected: StringVar
    values: list[str]

    def __init__(self, master: Frame):
        super().__init__(master)
        values = glob.glob(str(PathConf.SHORTCUT.joinpath("*.json")))
        self.values = [Path(x).stem for x in values]
        self.selected = StringVar(value=self.values[0] if self.values else None)

    def create(self):
        if self.selected.get() in self.values:
            self.data = self.read()

        CTkLabel(self, text="ファイルの選択").pack(anchor=ctk.W)
        CTkOptionMenu(self, values=self.values, variable=self.selected, command=self.callback).pack(fill=ctk.X)

        if self.selected.get() in self.values:
            super().create()
            self.filename.set(self.selected.get())

        return self

    def callback(self, value: str):
        for child in self.winfo_children():
            child.destroy()

        self.selected.set(value)
        self.create()

    def read(self) -> ShortcutData:
        try:
            path = PathConf.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
            with open(path, "r") as f:
                return ShortcutData.from_dict(json.load(f))
        except Exception as e:
            self.toast.error(str(e))
            raise
