import time
import urllib.parse
from pathlib import Path
from tkinter import StringVar
from typing import TypeVar

import customtkinter as ctk
import i18n
from component.component import EntryComponent, OptionMenuComponent, PaddingComponent
from component.tab_menu import TabMenuComponent
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkScrollableFrame
from lib.DGPSessionWrap import DgpSessionWrap
from lib.toast import ToastController, error_toast
from selenium import webdriver
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
        self.tab.add(text=i18n.t("app.tab.account_import"), callback=self.import_callback)
        self.tab.add(text=i18n.t("app.tab.import_browser"), callback=self.import_browser_callback)
        self.tab.add(text=i18n.t("app.tab.account_edit"), callback=self.edit_callback)
        self.tab.add(text=i18n.t("app.tab.device"), callback=self.device_callback)
        self.tab.add(text=i18n.t("app.tab.device_list"), callback=self.device_list_callback)
        return self

    def import_callback(self, master: CTkBaseClass):
        AccountImport(master).create().pack(expand=True, fill=ctk.BOTH)

    def import_browser_callback(self, master: CTkBaseClass):
        AccountBrowserImport(master).create().pack(expand=True, fill=ctk.BOTH)

    def edit_callback(self, master: CTkBaseClass):
        AccountEdit(master).create().pack(expand=True, fill=ctk.BOTH)

    def device_callback(self, master: CTkBaseClass):
        SettingDeviceTab(master).create().pack(expand=True, fill=ctk.BOTH)

    def device_list_callback(self, master: CTkBaseClass):
        DeviceListTab(master).create().pack(expand=True, fill=ctk.BOTH)


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
        text = i18n.t("app.account.filename")
        tooltip = i18n.t("app.account.filename_tooltip")
        EntryComponent(self, text=text, tooltip=tooltip, required=True, variable=self.name, alnum_only=True).create()
        CTkButton(self, text=i18n.t("app.account.import"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    @error_toast
    def callback(self):
        path = DataPathConfig.ACCOUNT.joinpath(self.name.get()).with_suffix(".bytes")
        if self.name.get() == "":
            raise Exception(i18n.t("app.account.filename_not_entered"))
        if path.exists():
            raise Exception(i18n.t("app.account.filename_already_exists"))

        with DgpSessionWrap() as session:
            session.read()
            if session.get_access_token() is None:
                raise Exception(i18n.t("app.account.import_error"))
            session.write_bytes(str(path))
            session.write()
            self.toast.info(i18n.t("app.account.import_success"))


class AccountBrowserImport(CTkScrollableFrame):
    toast: ToastController
    name: StringVar
    browser: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.name = StringVar()
        self.browser = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.account.import_browser_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        text = i18n.t("app.account.filename")
        tooltip = i18n.t("app.account.filename_tooltip")
        EntryComponent(self, text=text, tooltip=tooltip, required=True, variable=self.name, alnum_only=True).create()
        text = i18n.t("app.account.browser_select")
        tooltip = i18n.t("app.account.browser_select_tooltip")
        OptionMenuComponent(self, text=text, tooltip=tooltip, values=["Chrome", "Edge", "Firefox"], variable=self.browser).create()
        CTkButton(self, text=i18n.t("app.account.import_browser"), command=self.callback).pack(fill=ctk.X, pady=10)
        return self

    def get_driver(self):
        if self.browser.get() == "Chrome":
            return webdriver.Chrome()
        elif self.browser.get() == "Edge":
            return webdriver.Edge()
        elif self.browser.get() == "Firefox":
            return webdriver.Firefox()
        else:
            raise Exception(i18n.t("app.account.browser_not_selected"))

    @error_toast
    def callback(self):
        path = DataPathConfig.ACCOUNT.joinpath(self.name.get()).with_suffix(".bytes")
        if self.name.get() == "":
            raise Exception(i18n.t("app.account.filename_not_entered"))
        if path.exists():
            raise Exception(i18n.t("app.account.filename_already_exists"))

        session = DgpSessionWrap()
        res = session.post_dgp(DgpSessionWrap.LOGIN_URL, json={"prompt": ""}).json()
        if res["result_code"] != 100:
            raise Exception(res["error"])
        driver = self.get_driver()
        driver.get(res["data"]["url"])
        parsed_url = urllib.parse.urlparse(driver.current_url)
        while not (parsed_url.netloc == "webdgp-gameplayer.games.dmm.com" and parsed_url.path == "/login/success"):
            time.sleep(0.2)
            parsed_url = urllib.parse.urlparse(driver.current_url)
        code = urllib.parse.parse_qs(parsed_url.query)["code"][0]
        res = session.post_dgp(DgpSessionWrap.ACCESS_TOKEN, json={"code": code}).json()
        if res["result_code"] != 100:
            raise Exception(res["error"])
        session.actauth = {"accessToken": res["data"]["access_token"]}
        session.write_bytes(str(path))


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
        self.body_var = {}
        self.body_filename = StringVar()

    def create(self):
        CTkLabel(self, text=i18n.t("app.account.edit_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
        OptionMenuComponent(self, text=i18n.t("app.account.file_select"), values=self.values, variable=self.filename, command=self.select_callback).create()
        self._parent_canvas.yview_moveto(0)
        self.body = CTkFrame(self, fg_color="transparent", height=0)
        self.body.pack(expand=True, fill=ctk.BOTH)
        return self

    @error_toast
    def select_callback(self, value: str):
        children_destroy(self.body)
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        self.body_filename.set(self.filename.get())
        text = i18n.t("app.account.filename")
        tooltip = i18n.t("app.account.filename_tooltip")
        EntryComponent(self.body, text=text, tooltip=tooltip, required=True, variable=self.body_filename, alnum_only=True).create()

        session = DgpSessionWrap()
        session.read_bytes(str(Path(path)))
        for key in session.actauth.keys():
            self.body_var[key] = StringVar(value=session.actauth[key] or "")
            EntryComponent(self.body, text=key, variable=self.body_var[key]).create()
        CTkButton(self.body, text=i18n.t("app.account.save"), command=self.save_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self.body, text=i18n.t("app.account.delete"), command=self.delete_callback).pack(fill=ctk.X)

    @error_toast
    def save_callback(self):
        if self.body_filename.get() == "":
            raise Exception(i18n.t("app.account.filename_not_entered"))

        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        body_path = DataPathConfig.ACCOUNT.joinpath(self.body_filename.get()).with_suffix(".bytes")

        def write():
            session = DgpSessionWrap()
            session.read_bytes(str(Path(path)))
            for key in session.actauth.keys():
                session.actauth[key] = self.body_var[key].get()
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


class SettingDeviceTab(CTkScrollableFrame):
    toast: ToastController
    mode: bool
    hardware_name: StringVar
    auth_code: StringVar

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.mode = False
        self.hardware_name = StringVar(value="DMMGamePlayerFastLauncher")
        self.auth_code = StringVar()

        self.values = [x.stem for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]
        self.filename = StringVar()

    def create(self):
        if self.mode:
            CTkLabel(self, text=i18n.t("app.account.device_detail"), justify=ctk.LEFT).pack(anchor=ctk.W)
            EntryComponent(self, text=i18n.t("app.account.hardware_name"), variable=self.hardware_name, required=True).create()
            EntryComponent(self, text=i18n.t("app.account.auth_code"), tooltip=i18n.t("app.account.auth_code_tooltip"), variable=self.auth_code, required=True).create()
            CTkButton(self, text=i18n.t("app.account.auth"), command=self.auth_callback).pack(fill=ctk.X, pady=10)

        else:
            OptionMenuComponent(self, text=i18n.t("app.account.file_select"), values=self.values, variable=self.filename).create()
            CTkButton(self, text=i18n.t("app.account.send_auth_code"), command=self.send_auth_code_callback).pack(fill=ctk.X, pady=10)

        return self

    @error_toast
    def send_auth_code_callback(self):
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        session = DgpSessionWrap.read_cookies(path)
        res = session.post_device_dgp(DgpSessionWrap.HARDWARE_CODE, verify=False).json()
        if res["result_code"] != 100:
            raise Exception(res["error"])

        self.mode = True
        children_destroy(self)
        self.create()
        self.toast.info(i18n.t("app.account.send_auth_code_success"))

    @error_toast
    def auth_callback(self):
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        session = DgpSessionWrap.read_cookies(path)
        json = {
            "hardware_name": self.hardware_name.get(),
            "auth_code": self.auth_code.get(),
        }
        res = session.post_device_dgp(DgpSessionWrap.HARDWARE_CONF, json=json, verify=False).json()
        if res["result_code"] != 100:
            raise Exception(res["error"])
        self.toast.info(i18n.t("app.account.auth_success"))


class DeviceListTab(CTkScrollableFrame):
    toast: ToastController

    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)
        self.values = [x.stem for x in DataPathConfig.ACCOUNT.iterdir() if x.suffix == ".bytes"]
        self.filename = StringVar()
        self.data = None

    def create(self):
        OptionMenuComponent(self, text=i18n.t("app.account.file_select"), values=self.values, variable=self.filename, command=self.select_callback).create()
        if self.data:
            count = len(self.data["hardwares"] or [])
            limit = self.data["device_auth_limit_num"]
            CTkLabel(self, text=i18n.t("app.account.device_registrations", count=count, limit=limit), justify=ctk.LEFT).pack(anchor=ctk.W)

            for hardware in self.data["hardwares"] or []:
                for key, value in hardware.items():
                    EntryComponent(self, text=key, variable=StringVar(value=value), state=ctk.DISABLED).create()

                def command(id=hardware["hardware_manage_id"]):
                    return self.delete_callback(id)

                CTkButton(self, text=i18n.t("app.account.delete"), command=command).pack(fill=ctk.X, pady=10)
                PaddingComponent(self, height=20).create()

        return self

    @error_toast
    def select_callback(self, value: str):
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        session = DgpSessionWrap.read_cookies(path)
        res = session.post_device_dgp(DgpSessionWrap.HARDWARE_LIST, json={}, verify=False).json()
        if res["result_code"] != 100:
            raise Exception(res["error"])
        self.data = res["data"]

        children_destroy(self)
        self.create()
        self.toast.info(i18n.t("app.account.device_list_success"))

    @error_toast
    def delete_callback(self, id: str):
        path = DataPathConfig.ACCOUNT.joinpath(self.filename.get()).with_suffix(".bytes")
        session = DgpSessionWrap.read_cookies(path)
        json = {"hardware_manage_id": [id]}
        res = session.post_device_dgp(DgpSessionWrap.HARDWARE_REJECT, json=json, verify=False).json()
        if res["result_code"] != 100:
            raise Exception(res["error"])
        assert isinstance(self.data, dict)
        self.data["hardwares"] = [x for x in self.data["hardwares"] if x["hardware_manage_id"] != id]

        children_destroy(self)
        self.create()
        self.toast.info(i18n.t("app.account.delete_success"))
