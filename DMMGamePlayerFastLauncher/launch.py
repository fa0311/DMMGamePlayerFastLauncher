import json
import traceback
from pathlib import Path
from typing import Callable

import i18n
from component.tab_menu import TabMenuComponent
from customtkinter import CTk
from lib.DGPSessionV2 import DgpSessionV2
from lib.process_manager import ProcessManager
from lib.toast import ErrorWindow
from models.shortcut_data import ShortcutData
from static.config import AppConfig, DataPathConfig


class GameLauncher(CTk):
    loder: Callable
    tab: TabMenuComponent

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("900x600")
        loder()

    def create(self, id: str):
        try:
            self.launch(id)
        except Exception as e:
            ErrorWindow(self.master, str(e), traceback.format_exc()).create()

    def launch(self, id: str):
        path = DataPathConfig.SHORTCUT.joinpath(id).with_suffix(".json")
        with open(path, "r", encoding="utf-8") as f:
            data = ShortcutData.from_dict(json.load(f))

        account_path = DataPathConfig.ACCOUNT.joinpath(data.account_path.get()).with_suffix(".bytes")
        session = DgpSessionV2.read_cookies(account_path)
        response = session.lunch(data.product_id.get()).json()
        dgp_config = DgpSessionV2().get_config()

        if response["result_code"] == 100:
            dmm_args = response["data"]["execute_args"].split(" ")

            game_file = Path([x["detail"]["path"] for x in dgp_config["contents"] if x["productId"] == data.product_id][0])
            game_path = game_file.joinpath(response["data"]["exec_file_name"])

            process = ProcessManager.run([str(game_path)] + dmm_args)
            assert process.stdout is not None
            for line in process.stdout:
                text = line.decode("utf-8").strip()
                print(text)  # GameLog

            # if response["data"]["is_administrator"]:


class LanchLauncher(CTk):
    loder: Callable
    tab: TabMenuComponent

    def __init__(self, loder):
        super().__init__()

        self.title("DMMGamePlayer Fast Launcher")
        self.geometry("900x600")
        loder()

    def create(self, id: str):
        try:
            self.launch(id)
        except Exception as e:
            ErrorWindow(self.master, str(e), traceback.format_exc()).create()

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
