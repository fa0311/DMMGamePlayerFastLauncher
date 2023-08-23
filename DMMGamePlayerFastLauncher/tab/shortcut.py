import json
from pathlib import Path
from tkinter import Frame, StringVar

import customtkinter as ctk
import i18n
from component.component import EntryComponent, LabelComponent, OptionMenuComponent, PaddingComponent
from component.tab_menu import TabMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkOptionMenu, CTkScrollableFrame
from lib.DGPSessionV2 import DgpSessionV2
from lib.process_manager import Schtasks, Shortcut
from lib.toast import ToastController, error_toast
from models.shortcut_data import ShortcutData
from static.config import DataPathConfig
from static.env import Env
from utils.utils import children_destroy, file_create

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
        self.tab.add(text=i18n.t("app.tab.launch_create"), callback=self.launch_create_callback)
        return self

    def create_callback(self, master: CTkBaseClass):
        ShortcutCreate(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        ShortcutEdit(master).create().pack(expand=True, fill=ctk.BOTH)

    def launch_create_callback(self, master: CTkBaseClass):
        AccountShortcutCreate(master).create().pack(expand=True, fill=ctk.BOTH)


# ===== Shortcut Body =====


class ShortcutCreate(CTkScrollableFrame):
    toast: ToastController
    data: ShortcutData
    filename: StringVar
    product_ids: list[str]
    dgp_config: dict
    account_name_list: list[str]

    def __init__(self, master: Frame):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.data = ShortcutData()
        self.filename = StringVar()
        self.dgp_config = DgpSessionV2().get_config()
        self.product_ids = [x["productId"] for x in self.dgp_config["contents"]]
        self.account_name_list = [x.stem for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]

    @error_toast
    def create(self):
        if not self.winfo_children():
            CTkLabel(self, text=i18n.t("app.shortcut.add_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)

        EntryComponent(self, text=i18n.t("app.shortcut.filename"), tooltip=i18n.t("app.shortcut.filename_tooltip"), required=True, variable=self.filename).create()
        text = i18n.t("app.shortcut.product_id")
        OptionMenuComponent(self, text=text, tooltip=i18n.t("app.shortcut.product_id_tooltip"), values=self.product_ids, variable=self.data.product_id).create()
        text = i18n.t("app.shortcut.account_path")
        OptionMenuComponent(self, text=text, tooltip=i18n.t("app.shortcut.account_path_tooltip"), values=self.account_name_list, variable=self.data.account_path).create()

        game_args_tooltip = i18n.t("app.shortcut.game_args_tooltip")
        EntryComponent(self, text=i18n.t("app.shortcut.game_args"), tooltip=game_args_tooltip, variable=self.data.game_args).create()
        PaddingComponent(self, height=5).create()

        CTkButton(self, text=i18n.t("app.shortcut.create_bypass_shortcut_and_save"), command=self.bypass_callback).pack(fill=ctk.X, pady=5)
        CTkButton(self, text=i18n.t("app.shortcut.create_shortcut_and_save"), command=self.save_callback).pack(fill=ctk.X, pady=5)
        CTkButton(self, text=i18n.t("app.shortcut.save_only"), command=self.save_only_callback).pack(fill=ctk.X, pady=5)
        return self

    def save(self, exists=False):
        if self.data.product_id.get() == "":
            raise Exception(i18n.t("app.shortcut.product_id_not_entered"))
        if self.filename.get() == "":
            raise Exception(i18n.t("app.shortcut.filename_not_entered"))

        path = DataPathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        if not exists:
            file_create(path, name=i18n.t("app.shortcut.filename"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.data.to_dict()))

    @error_toast
    def bypass_callback(self):
        self.save()
        task = Schtasks(self.filename.get())
        if task.check():
            task.set()

        name, icon = self.get_game_info()
        sorce = Path.home().joinpath("Desktop").joinpath(name).with_suffix(".lnk")
        args = ["/run", "/tn", task.name]
        Shortcut().create(sorce=sorce, target=Env.SCHTASKS, args=args, icon=icon)

        self.toast.info(i18n.t("app.shortcut.save_success"))

    @error_toast
    def save_callback(self):
        self.save()
        name, icon = self.get_game_info()
        sorce = Path.home().joinpath("Desktop").joinpath(name).with_suffix(".lnk")
        args = [self.filename.get()]
        Shortcut().create(sorce=sorce, args=args, icon=icon)
        self.toast.info(i18n.t("app.shortcut.save_success"))

    @error_toast
    def save_only_callback(self):
        self.save()
        self.toast.info(i18n.t("app.shortcut.save_success"))

    def get_game_info(self) -> tuple[str, Path]:
        game_path = Path([x["detail"]["path"] for x in self.dgp_config["contents"] if x["productId"] == self.data.product_id.get()][0])
        path = DataPathConfig.ACCOUNT.joinpath(self.data.account_path.get()).with_suffix(".bytes")
        session = DgpSessionV2().read_cookies(path)
        data = session.lunch(self.data.product_id.get()).json()["data"]

        title = data["title"].replace("/", "").replace("\\", "")
        title = title.replace(":", "").replace("*", "").replace("?", "")
        title = title.replace('"', "").replace("<", "").replace(">", "").replace("|", "")

        return title, game_path.joinpath(data["exec_file_name"])


class ShortcutEdit(ShortcutCreate):
    selected: StringVar
    values: list[str]

    def __init__(self, master: Frame):
        super().__init__(master)
        self.values = [x.stem for x in DataPathConfig.SHORTCUT.iterdir() if x.suffix == ".json"]
        self.selected = StringVar()

    @error_toast
    def create(self):
        CTkLabel(self, text=i18n.t("app.shortcut.edit_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)

        LabelComponent(self, text=i18n.t("app.shortcut.file_select")).create()
        CTkOptionMenu(self, values=self.values, variable=self.selected, command=self.option_callback).pack(fill=ctk.X)

        if self.selected.get() in self.values:
            self.data = self.read()
            super().create()
            self.filename.set(self.selected.get())
            CTkButton(self, text=i18n.t("app.shortcut.delete"), command=self.delete_callback).pack(fill=ctk.X, pady=5)

        return self

    def save(self):
        path = DataPathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        selected = DataPathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        if path == selected:
            super().save(exists=True)
        else:
            super().save()
            selected.unlink()
            self.values.remove(self.selected.get())
            self.values.append(self.filename.get())
            self.selected.set(self.filename.get())
            self.option_callback("_")

    @error_toast
    def delete_callback(self):
        path = DataPathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        path.unlink()
        self.values.remove(self.selected.get())
        self.selected.set("")
        self.option_callback("_")
        self.toast.info(i18n.t("app.shortcut.save_success"))

    @error_toast
    def option_callback(self, _: str):
        children_destroy(self)
        self.create()

    @error_toast
    def read(self) -> ShortcutData:
        path = DataPathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        with open(path, "r", encoding="utf-8") as f:
            return ShortcutData.from_dict(json.load(f))


class AccountShortcutCreate(CTkScrollableFrame):
    toast: ToastController
    account_name_list: list[str]
    account_path: StringVar

    def __init__(self, master: Frame):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.account_name_list = [x.stem for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]
        self.account_path = StringVar()

    @error_toast
    def create(self):
        text = i18n.t("app.account.account_path")
        OptionMenuComponent(self, text=text, tooltip=i18n.t("app.account.account_path_tooltip"), values=self.account_name_list, variable=self.account_path).create()
        CTkButton(self, text=i18n.t("app.account.create_shortcut_and_save"), command=self.callback).pack(fill=ctk.X, pady=5)
        return self

    @error_toast
    def callback(self):
        if self.account_path.get() == "":
            raise Exception(i18n.t("app.account.file_not_selected"))

        name = self.account_path.get()
        sorce = Path.home().joinpath("Desktop").joinpath(name).with_suffix(".lnk")
        args = [name, "--type", "launcher"]
        Shortcut().create(sorce=sorce, args=args)

        self.toast.info(i18n.t("app.shortcut.save_success"))
