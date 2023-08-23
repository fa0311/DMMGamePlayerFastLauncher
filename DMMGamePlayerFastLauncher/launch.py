import json
import logging
import traceback
from pathlib import Path
from typing import Callable

import i18n
from component.component import CTkProgressWindow
from component.tab_menu import TabMenuComponent
from customtkinter import CTk
from lib.DGPSessionV2 import DgpSessionV2
from lib.process_manager import ProcessManager
from lib.thread import threading_wrapper
from lib.toast import ErrorWindow
from models.shortcut_data import ShortcutData
from static.config import AppConfig, DataPathConfig
from static.env import Env


class GameLauncher(CTk):
    loder: Callable
    tab: TabMenuComponent

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("600x300")
        self.withdraw()
        loder(self)

    @threading_wrapper
    def thread(self, id: str):
        try:
            self.launch(id)
            self.quit()
        except Exception as e:
            if not Env.DEVELOP:
                ErrorWindow(self, str(e), traceback.format_exc()).create()
            raise

    def launch(self, id: str):
        path = DataPathConfig.SHORTCUT.joinpath(id).with_suffix(".json")
        with open(path, "r", encoding="utf-8") as f:
            data = ShortcutData.from_dict(json.load(f))

        account_path = DataPathConfig.ACCOUNT.joinpath(data.account_path.get()).with_suffix(".bytes")
        session = DgpSessionV2.read_cookies(account_path)
        response = session.lunch(data.product_id.get()).json()
        dgp_config = session.get_config()
        game = [x for x in dgp_config["contents"] if x["productId"] == data.product_id.get()][0]

        if not Env.DEVELOP:
            if response["data"]["is_administrator"] and not ProcessManager.admin_check():
                raise Exception(i18n.t("app.launch.admin_error"))

        if response["result_code"] != 100:
            raise Exception(response["error"])

        game_file = Path(game["detail"]["path"])
        game_path = game_file.joinpath(response["data"]["exec_file_name"])

        if response["data"]["latest_version"] != game["detail"]["version"]:
            if data.auto_update.get():
                download = session.download(response["data"]["latest_version"], response["data"]["file_list_url"], game_path.parent)
                box = CTkProgressWindow(self).create()
                for progress, file in download:
                    logging.info(file["local_path"])
                    box.set(progress)
                box.destroy()
                game["detail"]["version"] = response["data"]["latest_version"]
                session.set_config(dgp_config)

        dmm_args = response["data"]["execute_args"].split(" ")
        process = ProcessManager.run([str(game_path.absolute())] + dmm_args)

        assert process.stdout is not None
        for line in process.stdout:
            text = line.decode("utf-8").strip()
            logging.info(text)


class LanchLauncher(CTk):
    loder: Callable
    tab: TabMenuComponent

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("600x300")
        self.withdraw()
        loder(self)

    @threading_wrapper
    def thread(self, id: str):
        try:
            self.launch(id)
            self.quit()
        except Exception as e:
            if not Env.DEVELOP:
                ErrorWindow(self, str(e), traceback.format_exc()).create()
            raise

    def launch(self, id: str):
        path = DataPathConfig.ACCOUNT.joinpath(id).with_suffix(".bytes")
        with DgpSessionV2() as session:
            session.read_bytes(str(path))
            if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                raise Exception(i18n.t("app.launch.export_error"))
            session.write()

        dgp = AppConfig.DATA.dmm_game_player_program_folder.get_path().joinpath("DMMGamePlayer.exe").absolute()
        process = ProcessManager().run([str(dgp)])

        assert process.stdout is not None
        for line in process.stdout:
            text = line.decode("utf-8").strip()
            print(text)

        with DgpSessionV2() as session:
            session.read()
            if session.cookies.get("login_secure_id", **session.cookies_kwargs) is None:
                raise Exception(i18n.t("app.launch.import_error"))
            session.write_bytes(str(path))

            session.cookies.clear()
            session.write()
