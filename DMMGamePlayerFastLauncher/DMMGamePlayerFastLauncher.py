import json
import os
import sys
from pathlib import Path

import customtkinter as ctk
import i18n
from app import App
from lib.DGPSessionV2 import DgpSessionV2
from lib.process_manager import ProcessManager
from models.shortcut_data import ShortcutDataRaw
from static.config import AppConfig, AssetsPathConfig, DataPathConfig
from static.loder import config_loder


def loder():
    config_loder()
    i18n.load_path.append(str(AssetsPathConfig.I18N))
    i18n.set("locale", AppConfig.DATA.lang.get())

    os.makedirs(DataPathConfig.ACCOUNT, exist_ok=True)
    os.makedirs(DataPathConfig.SHORTCUT, exist_ok=True)
    os.makedirs(DataPathConfig.SCHTASKS, exist_ok=True)

    ctk.set_default_color_theme(str(AssetsPathConfig.THEMES.joinpath(AppConfig.DATA.theme.get()).with_suffix(".json")))
    ctk.set_appearance_mode(AppConfig.DATA.appearance_mode.get())

    try:
        ctk.set_widget_scaling(AppConfig.DATA.window_scaling.get())
    except Exception:
        pass


if len(sys.argv) == 1:
    App(loder).create().mainloop()

else:
    shortcut_path = DataPathConfig.SHORTCUT.joinpath(sys.argv[1]).with_suffix(".json")
    with open(shortcut_path, "r") as f:
        data = ShortcutDataRaw(**json.load(f))

    account_path = DataPathConfig.ACCOUNT.joinpath(data.account_path).with_suffix(".bytes")
    session = DgpSessionV2.read_cookies(account_path)
    response = session.lunch(data.product_id).json()
    dgp_config = DgpSessionV2().get_config()
    print(response)

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
