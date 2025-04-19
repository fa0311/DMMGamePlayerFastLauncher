import logging
import subprocess
import sys
import time
import traceback
from base64 import b64encode
from pathlib import Path
from typing import Callable

import customtkinter as ctk
import i18n
import psutil
from component.component import CTkProgressWindow
from customtkinter import CTk
from lib.DGPSessionWrap import DgpSessionWrap
from lib.discord import start_rich_presence
from lib.process_manager import ProcessIdManager, ProcessManager
from lib.thread import threading_wrapper
from lib.toast import ErrorWindow
from models.setting_data import AppConfig
from models.shortcut_data import BrowserConfigData, LauncherShortcutData, ShortcutData
from static.config import DataPathConfig
from static.constant import Constant
from static.env import Env
from tab.home import HomeTab
from utils.utils import get_driver, login_driver


class GameLauncher(CTk):
    loder: Callable

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("900x600")
        self.withdraw()
        loder(self)

    def create(self):
        HomeTab(self).create().pack(expand=True, fill=ctk.BOTH)
        return self

    @threading_wrapper
    def thread(self, id: str, kill: bool = False, force_non_uac: bool = False):
        try:
            self.launch(id, kill, force_non_uac)
            self.quit()
        except Exception as e:
            if Env.DEVELOP:
                self.iconify()
                raise
            else:
                self.iconify()
                ErrorWindow(self, str(e), traceback.format_exc(), quit=True).create()

    def launch(self, id: str, kill: bool = False, force_non_uac: bool = False):
        path = DataPathConfig.SHORTCUT.joinpath(id).with_suffix(".json")
        data = ShortcutData.from_path(path)

        if data.account_path.get() == Constant.ALWAYS_EXTRACT_FROM_DMM:
            session = DgpSessionWrap.read_dgp()
        else:
            account_path = DataPathConfig.ACCOUNT.joinpath(data.account_path.get()).with_suffix(".bytes")
            browser_config_path = DataPathConfig.BROWSER_CONFIG.joinpath(data.account_path.get()).with_suffix(".json")
            session = DgpSessionWrap.read_cookies(account_path)
            if browser_config_path.exists():
                browser_config = BrowserConfigData.from_path(browser_config_path)
                profile_path = DataPathConfig.BROWSER_PROFILE.joinpath(browser_config.profile_name.get()).absolute()
                userdata = session.post_dgp(DgpSessionWrap.USER_INFO).json()
                if userdata["result_code"] != 100 or True:
                    res = session.post_dgp(DgpSessionWrap.LOGIN_URL, json={"prompt": ""}).json()
                    if res["result_code"] != 100:
                        raise Exception(res["error"])
                    driver = get_driver(browser_config.browser.get(), profile_path)
                    code = login_driver(res["data"]["url"], driver)
                    driver.quit()
                    res = session.post_dgp(DgpSessionWrap.ACCESS_TOKEN, json={"code": code}).json()
                    if res["result_code"] != 100:
                        raise Exception(res["error"])
                    session.actauth = {"accessToken": res["data"]["access_token"]}
                    session.write_bytes(str(account_path))

        dgp_config = session.get_config()
        game = [x for x in dgp_config["contents"] if x["productId"] == data.product_id.get()][0]

        response = session.lunch(data.product_id.get(), game["gameType"]).json()

        if response["result_code"] != 100:
            raise Exception(response["error"])

        if response["data"].get("drm_auth_token") is not None:
            filename = b64encode(data.product_id.get().encode("utf-8")).decode("utf-8")
            drm_path = Env.DMM_GAME_PLAYER_HIDDEN_FOLDER.joinpath(filename)
            drm_path.parent.mkdir(parents=True, exist_ok=True)
            with open(drm_path.absolute(), "w+") as f:
                f.write(response["data"]["drm_auth_token"])

        game_file = Path(game["detail"]["path"])
        game_path = game_file.joinpath(response["data"]["exec_file_name"])

        if response["data"]["latest_version"] != game["detail"]["version"]:
            if data.auto_update.get():
                download = session.download(response["data"]["sign"], response["data"]["file_list_url"], game_file)
                box = CTkProgressWindow(self).create()
                for progress, file in download:
                    box.set(progress)
                box.destroy()
                game["detail"]["version"] = response["data"]["latest_version"]
                session.set_config(dgp_config)

        dmm_args = response["data"]["execute_args"].split(" ") + data.game_args.get().split(" ")
        game_path = str(game_path.relative_to(game_file))
        game_full_path = str(game_file.joinpath(game_path))
        is_admin = ProcessManager.admin_check()
        if kill:
            process = ProcessManager.run([game_path] + dmm_args, cwd=str(game_file))
            try:
                process.wait(2)
            except subprocess.TimeoutExpired:
                for child in psutil.Process(process.pid).children(recursive=True):
                    child.kill()
        else:
            pid_manager = ProcessIdManager()
            timer = time.time()
            if response["data"]["is_administrator"] and (not is_admin) and (not force_non_uac):
                process = ProcessManager.admin_run([game_path] + dmm_args, cwd=str(game_file))
                game_pid = pid_manager.new_process().search(game_full_path)
                if data.external_tool_path.get() != "":
                    external_tool_pid_manager = ProcessIdManager()
                    ProcessManager.admin_run([data.external_tool_path.get()], cwd=str(game_file))
                    external_tool_pid = external_tool_pid_manager.new_process().search_or_none(data.external_tool_path.get())
                if data.rich_presence.get():
                    start_rich_presence(game_pid, data.product_id.get(), response["data"]["title"])
                while psutil.pid_exists(game_pid):
                    time.sleep(1)
            else:
                process = ProcessManager.run([game_path] + dmm_args, cwd=str(game_file))
                if data.external_tool_path.get() != "":
                    external_tool_process = ProcessManager.run([data.external_tool_path.get()], cwd=str(game_file))
                    external_tool_pid = external_tool_process.pid
                if data.rich_presence.get():
                    start_rich_presence(process.pid, data.product_id.get(), response["data"]["title"])
                assert process.stdout is not None
                for line in process.stdout:
                    logging.debug(decode(line))
            if time.time() - timer < 10:
                logging.warning("Unexpected process termination")
                time.sleep(10 - (time.time() - timer))
                logging.warning("Restarting the process")
                game_pid = pid_manager.new_process().search_or_none(game_full_path)
                if game_pid is not None:
                    if data.rich_presence.get():
                        start_rich_presence(game_pid, data.product_id.get(), response["data"]["title"])
                    while psutil.pid_exists(game_pid):
                        time.sleep(1)
            if data.external_tool_path.get() != "" and external_tool_pid is not None:
                for child in psutil.Process(external_tool_pid).children(recursive=True):
                    child.kill()


class LanchLauncher(CTk):
    loder: Callable

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("900x600")
        self.withdraw()
        loder(self)

    def create(self):
        HomeTab(self).create().pack(expand=True, fill=ctk.BOTH)
        return self

    @threading_wrapper
    def thread(self, id: str):
        try:
            self.launch(id)
            self.quit()
        except Exception as e:
            if not Env.DEVELOP:
                self.iconify()
                ErrorWindow(self, str(e), traceback.format_exc(), quit=True).create()
            raise

    def launch(self, id: str):
        if DgpSessionWrap.is_running_dmm():
            raise Exception(i18n.t("app.lib.dmm_already_running"))

        path = DataPathConfig.ACCOUNT_SHORTCUT.joinpath(id).with_suffix(".json")
        data = LauncherShortcutData.from_path(path)

        account_path = DataPathConfig.ACCOUNT.joinpath(data.account_path.get()).with_suffix(".bytes")

        before_session = DgpSessionWrap.read_dgp()

        session = DgpSessionWrap.read_cookies(Path(account_path))
        if session.get_access_token() is None:
            raise Exception(i18n.t("app.launch.export_error"))
        session.write()

        dgp = AppConfig.DATA.dmm_game_player_program_folder.get_path()

        dmm_args = data.dgp_args.get().split(" ")
        process = ProcessManager.run(["DMMGamePlayer.exe"] + dmm_args, cwd=str(dgp.absolute()))

        assert process.stdout is not None
        for line in process.stdout:
            logging.debug(decode(line))

        session = DgpSessionWrap.read_dgp()
        if session.get_access_token() is None:
            raise Exception(i18n.t("app.launch.import_error"))
        session.write_bytes(str(account_path))
        before_session.write()


class GameLauncherUac(CTk):
    @staticmethod
    def wait(args: list[str]):
        if not ProcessManager.admin_check():
            pid_manager = ProcessIdManager()
            ProcessManager.admin_run([sys.executable, *args])
            print(sys.executable)
            game_pid = pid_manager.new_process().search(sys.executable)
            while psutil.pid_exists(game_pid):
                time.sleep(1)


def decode(s: bytes) -> str:
    try:
        return s.decode("utf-8").strip()
    except Exception:
        pass
    try:
        return s.decode("cp932").strip()
    except Exception:
        pass
    return str(s)
