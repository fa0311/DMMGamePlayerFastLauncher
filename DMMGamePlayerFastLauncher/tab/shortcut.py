import webbrowser
from pathlib import Path
from tkinter import Frame, StringVar
from typing import Callable

import customtkinter as ctk
import i18n
from component.component import (
    ButtonComponent,
    CheckBoxComponent,
    EntryComponent,
    FilePathComponent,
    LabelComponent,
    OptionMenuComponent,
    OptionMenuTupleComponent,
    PaddingComponent,
)
from component.tab_menu import TabMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkOptionMenu, CTkScrollableFrame
from lib.DGPSessionWrap import DgpSessionWrap
from lib.process_manager import Schtasks, Shortcut
from lib.toast import ToastController, error_toast
from models.setting_data import AppConfig
from models.shortcut_data import LauncherShortcutData, ShortcutData
from static.config import DataPathConfig
from static.constant import Constant
from static.env import Env
from utils.utils import children_destroy, file_create, get_default_locale

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
        # self.tab.add(text=i18n.t("app.tab.launch_create"), callback=self.launch_create_callback)
        # self.tab.add(text=i18n.t("app.tab.launch_edit"), callback=self.launch_edit_callback)
        return self

    def create_callback(self, master: CTkBaseClass):
        ShortcutCreate(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        ShortcutEdit(master).create().pack(expand=True, fill=ctk.BOTH)

    def launch_create_callback(self, master: CTkBaseClass):
        LauncherShortcutCreate(master).create().pack(expand=True, fill=ctk.BOTH)

    def launch_edit_callback(self, master: CTkBaseClass):
        LauncherShortcutEdit(master).create().pack(expand=True, fill=ctk.BOTH)


# ===== Shortcut Body =====


class ShortcutBase(CTkScrollableFrame):
    toast: ToastController
    data: ShortcutData
    filename: StringVar
    product_ids: list[str]
    dgp_config: dict
    account_name_list: list[tuple[str, str]]

    def __init__(self, master: Frame):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.data = ShortcutData()
        self.filename = StringVar()
        self.dgp_config = DgpSessionWrap().get_config()
        self.product_ids = [x["productId"] for x in self.dgp_config["contents"]]
        self.account_name_list = [(x.stem, x.stem) for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]
        self.account_name_list.insert(0, (Constant.ALWAYS_EXTRACT_FROM_DMM, i18n.t("app.shortcut.always_extract_from_dmm")))

    def create(self):
        text = i18n.t("app.shortcut.filename")
        tooltip = i18n.t("app.shortcut.filename_tooltip")
        EntryComponent(self, text=text, tooltip=tooltip, required=True, variable=self.filename, alnum_only=True).create()
        text = i18n.t("app.shortcut.product_id")
        OptionMenuComponent(self, text=text, tooltip=i18n.t("app.shortcut.product_id_tooltip"), values=self.product_ids, variable=self.data.product_id).create()
        text = i18n.t("app.shortcut.account_path")
        OptionMenuTupleComponent(self, text=text, tooltip=i18n.t("app.shortcut.account_path_tooltip"), values=self.account_name_list, variable=self.data.account_path).create()

        text = i18n.t("app.shortcut.game_args")
        EntryComponent(self, text=text, tooltip=i18n.t("app.shortcut.game_args_tooltip"), variable=self.data.game_args).create()

        # 外部ツールの起動パス
        text = i18n.t("app.shortcut.external_tool_path")
        FilePathComponent(self, text=text, tooltip=i18n.t("app.shortcut.external_tool_path_tooltip"), variable=self.data.external_tool_path).create()

        CheckBoxComponent(self, text=i18n.t("app.shortcut.auto_update"), variable=self.data.auto_update).create()
        CheckBoxComponent(self, text=i18n.t("app.shortcut.rich_presence"), variable=self.data.rich_presence).create()

        PaddingComponent(self, height=5).create()

        text = i18n.t("app.shortcut.create_bypass_shortcut_and_save")
        ButtonComponent(self, text=text, tooltip=i18n.t("app.shortcut.create_bypass_shortcut_and_save_tooltip"), command=self.bypass_callback).create()
        text = i18n.t("app.shortcut.create_uac_shortcut_and_save")
        ButtonComponent(self, text=text, tooltip=i18n.t("app.shortcut.create_uac_shortcut_and_save_tooltip"), command=self.uac_callback).create()
        text = i18n.t("app.shortcut.create_shortcut_and_save")
        ButtonComponent(self, text=text, tooltip=i18n.t("app.shortcut.create_shortcut_and_save_tooltip"), command=self.save_callback).create()
        text = i18n.t("app.shortcut.save_only")
        ButtonComponent(self, text=text, tooltip=i18n.t("app.shortcut.save_only_tooltip"), command=self.save_only_callback).create()
        return self

    def save(self):
        if self.data.product_id.get() == "":
            raise Exception(i18n.t("app.shortcut.product_id_not_entered"))
        if self.filename.get() == "":
            raise Exception(i18n.t("app.shortcut.filename_not_entered"))
        if self.data.account_path.get() == "":
            raise Exception(i18n.t("app.shortcut.account_path_not_entered"))

        path = DataPathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        file_create(path, name=i18n.t("app.shortcut.filename"))
        self.data.write_path(path)

    def save_handler(self, fn: Callable[[], None]):
        pass

    @error_toast
    def bypass_callback(self):
        def fn():
            task = Schtasks(self.filename.get())
            if task.check():
                task.set()
            try:
                name, icon, admin = self.get_game_info()
            except Exception:
                name, icon = self.filename.get(), None
                self.toast.error(i18n.t("app.shortcut.game_info_error"))
            source = Env.DESKTOP.joinpath(name).with_suffix(".lnk")
            args = ["/run", "/tn", task.name]
            Shortcut().create(source=source, target=Env.SCHTASKS, args=args, icon=icon)
            self.toast.info(i18n.t("app.shortcut.save_success"))

        self.save_handler(fn)

    @error_toast
    def uac_callback(self):
        def fn():
            try:
                try:
                    name, icon, admin = self.get_game_info()
                except Exception:
                    name, icon = self.filename.get(), None
                    self.toast.error(i18n.t("app.shortcut.game_info_error"))
                source = Env.DESKTOP.joinpath(name).with_suffix(".lnk")
                args = [self.filename.get()]
                Shortcut().create(source=source, args=args, icon=icon)
                self.toast.info(i18n.t("app.shortcut.save_success"))
            except Exception:
                DataPathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json").unlink()
                raise

        self.save_handler(fn)

    @error_toast
    def save_callback(self):
        def fn():
            try:
                try:
                    name, icon, admin = self.get_game_info()
                except Exception:
                    name, icon, admin = self.filename.get(), None, False
                    self.toast.error(i18n.t("app.shortcut.game_info_error"))
                if admin:
                    raise Exception(i18n.t("app.shortcut.administrator_error"))
            except Exception:
                DataPathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json").unlink()
                raise
            source = Env.DESKTOP.joinpath(name).with_suffix(".lnk")
            args = [self.filename.get()]
            Shortcut().create(source=source, args=args, icon=icon)
            self.toast.info(i18n.t("app.shortcut.save_success"))

        self.save_handler(fn)

    @error_toast
    def save_only_callback(self):
        def fn():
            self.toast.info(i18n.t("app.shortcut.save_success"))

        self.save_handler(fn)

    def unity_command_line_args_callback(self):
        webbrowser.open(i18n.t("app.shortcut.unity_command_line_args_link"))

    def get_game_info(self) -> tuple[str, Path, bool]:
        game = [x for x in self.dgp_config["contents"] if x["productId"] == self.data.product_id.get()][0]
        game_path = Path(game["detail"]["path"])

        if self.data.account_path.get() == Constant.ALWAYS_EXTRACT_FROM_DMM:
            session = DgpSessionWrap.read_dgp()
        else:
            path = DataPathConfig.ACCOUNT.joinpath(self.data.account_path.get()).with_suffix(".bytes")
            session = DgpSessionWrap.read_cookies(path)
        response = session.lunch(self.data.product_id.get(), game["gameType"]).json()

        if response["result_code"] != 100:
            raise Exception(response["error"])

        data = response["data"]
        title = data["title"].replace("/", "").replace("\\", "")
        title = title.replace(":", "").replace("*", "").replace("?", "")
        title = title.replace('"', "").replace("<", "").replace(">", "").replace("|", "")

        file = game_path.joinpath(data["exec_file_name"])

        if get_default_locale()[1] == "cp932":
            return (title, file, data["is_administrator"])

        if all(ord(c) < 128 for c in title):
            return (title, file, data["is_administrator"])

        return (self.filename.get(), file, data["is_administrator"])


class ShortcutCreate(ShortcutBase):
    def create(self):
        if not self.winfo_children():
            CTkLabel(self, text=i18n.t("app.shortcut.add_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        super().create()

        PaddingComponent(self, height=15).create()
        text = i18n.t("app.shortcut.unity_command_line_args")
        ButtonComponent(self, text=text, tooltip=i18n.t("app.shortcut.unity_command_line_args_tooltip"), command=self.unity_command_line_args_callback).create()

        return self

    def save_handler(self, fn: Callable[[], None]):
        self.save()
        fn()


class ShortcutEdit(ShortcutBase):
    selected: StringVar
    values: list[str]

    def __init__(self, master: Frame):
        super().__init__(master)
        self.values = [x.stem for x in DataPathConfig.SHORTCUT.iterdir() if x.suffix == ".json"]
        self.selected = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.shortcut.edit_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)

        LabelComponent(self, text=i18n.t("app.shortcut.file_select")).create()
        CTkOptionMenu(self, values=self.values, variable=self.selected, command=self.option_callback).pack(fill=ctk.X)

        if self.selected.get() in self.values:
            self.data = self.read()
            super().create()
            self.filename.set(self.selected.get())
            CTkButton(self, text=i18n.t("app.shortcut.delete"), command=self.delete_callback).pack(fill=ctk.X, pady=5)

        PaddingComponent(self, height=15).create()
        text = i18n.t("app.shortcut.unity_command_line_args")
        ButtonComponent(self, text=text, tooltip=i18n.t("app.shortcut.unity_command_line_args_tooltip"), command=self.unity_command_line_args_callback).create()

        return self

    def save_handler(self, fn: Callable[[], None]):
        selected = DataPathConfig.SHORTCUT.joinpath(self.selected.get())
        selected.with_suffix(".json").rename(selected.with_suffix(".json.bak"))
        try:
            self.save()
            try:
                fn()
            except Exception as e:
                try:
                    DataPathConfig.SHORTCUT.joinpath(self.filename.get()).with_suffix(".json").unlink()
                except Exception:
                    pass
                raise e
        except Exception:
            selected.with_suffix(".json.bak").rename(selected.with_suffix(".json"))
            raise
        selected.with_suffix(".json.bak").unlink()
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

    def read(self) -> ShortcutData:
        path = DataPathConfig.SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        return ShortcutData.from_path(path)


class LauncherShortcutBase(CTkScrollableFrame):
    toast: ToastController
    account_name_list: list[str]
    filename: StringVar
    data: LauncherShortcutData

    def __init__(self, master: Frame):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.account_name_list = [x.stem for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]
        self.filename = StringVar()
        self.data = LauncherShortcutData()

    def create(self):
        text = i18n.t("app.shortcut.filename")
        tooltip = i18n.t("app.shortcut.filename_tooltip")
        EntryComponent(self, text=text, tooltip=tooltip, required=True, variable=self.filename, alnum_only=True).create()
        text = i18n.t("app.shortcut.account_path")
        OptionMenuComponent(self, text=text, values=self.account_name_list, variable=self.data.account_path).create()
        text = i18n.t("app.shortcut.dgp_args")
        EntryComponent(self, text=text, tooltip=i18n.t("app.shortcut.dgp_args_tooltip"), variable=self.data.dgp_args).create()

        PaddingComponent(self, height=5).create()
        CTkButton(self, text=i18n.t("app.shortcut.create_shortcut_and_save"), command=self.save_callback).pack(fill=ctk.X, pady=5)
        CTkButton(self, text=i18n.t("app.shortcut.save_only"), command=self.save_only_callback).pack(fill=ctk.X, pady=5)
        return self

    def save(self):
        if self.filename.get() == "":
            raise Exception(i18n.t("app.shortcut.filename_not_entered"))
        if self.data.account_path.get() == "":
            raise Exception(i18n.t("app.shortcut.file_not_selected"))

        path = DataPathConfig.ACCOUNT_SHORTCUT.joinpath(self.filename.get()).with_suffix(".json")
        file_create(path, name=i18n.t("app.shortcut.filename"))
        self.data.write_path(path)

    @error_toast
    def save_callback(self):
        self.save()
        try:
            name = self.filename.get()
            source = Env.DESKTOP.joinpath(name).with_suffix(".lnk")
            args = [name, "--type", "launcher"]
            icon = AppConfig.DATA.dmm_game_player_program_folder.get_path().joinpath("DMMGamePlayer.exe")
            Shortcut().create(source=source, args=args, icon=icon)
            self.toast.info(i18n.t("app.shortcut.save_success"))
        except Exception:
            DataPathConfig.ACCOUNT_SHORTCUT.joinpath(self.filename.get()).with_suffix(".json").unlink()
            raise

    @error_toast
    def save_only_callback(self):
        self.save()
        self.toast.info(i18n.t("app.shortcut.save_success"))


class LauncherShortcutCreate(LauncherShortcutBase):
    toast: ToastController
    account_name_list: list[str]
    filename: StringVar
    data: LauncherShortcutData

    def create(self):
        CTkLabel(self, text=i18n.t("app.shortcut.account_create_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        super().create()
        return self


class LauncherShortcutEdit(LauncherShortcutBase):
    selected: StringVar
    values: list[str]

    def __init__(self, master: Frame):
        super().__init__(master)
        self.values = [x.stem for x in DataPathConfig.ACCOUNT_SHORTCUT.iterdir() if x.suffix == ".json"]
        self.selected = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.shortcut.account_edit_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)

        LabelComponent(self, text=i18n.t("app.shortcut.file_select")).create()
        CTkOptionMenu(self, values=self.values, variable=self.selected, command=self.option_callback).pack(fill=ctk.X)

        if self.selected.get() in self.values:
            self.data = self.read()
            super().create()
            self.filename.set(self.selected.get())
            CTkButton(self, text=i18n.t("app.shortcut.delete"), command=self.delete_callback).pack(fill=ctk.X, pady=5)

        return self

    def save(self):
        selected = DataPathConfig.ACCOUNT_SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        selected.rename(selected.with_suffix(".json.bak"))
        try:
            super().save()
            selected.with_suffix(".json.bak").unlink()
            self.values.remove(self.selected.get())
            self.values.append(self.filename.get())
            self.selected.set(self.filename.get())
            self.option_callback("_")
        except Exception:
            selected.with_suffix(".json.bak").rename(selected.with_suffix(".json"))
            raise

    @error_toast
    def delete_callback(self):
        path = DataPathConfig.ACCOUNT_SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        path.unlink()
        self.values.remove(self.selected.get())
        self.selected.set("")
        self.option_callback("_")
        self.toast.info(i18n.t("app.shortcut.save_success"))

    @error_toast
    def option_callback(self, _: str):
        children_destroy(self)
        self.create()

    def read(self) -> LauncherShortcutData:
        path = DataPathConfig.ACCOUNT_SHORTCUT.joinpath(self.selected.get()).with_suffix(".json")
        return LauncherShortcutData.from_path(path)
