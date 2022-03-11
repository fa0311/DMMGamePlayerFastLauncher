import subprocess
import requests
import argparse
import re
import json
import glob

requests.packages.urllib3.disable_warnings()

argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)

argpar.add_argument("product_id")
argpar.add_argument("--game-path", default=False)
argpar.add_argument(
    "-dgp-path",
    "--dmmgameplayer-path",
    default="C:/Program Files/DMMGamePlayer/DMMGamePlayer.exe",
)
argpar.add_argument("--non-kill", action='store_true')
argpar.add_argument("--debug", action='store_true')
arg = argpar.parse_args()

headers = {
    "Host": "apidgp-gameplayer.games.dmm.com",
    "Connection": "keep-alive",
    "User-Agent": "DMMGamePlayer5-Win/17.1.2 Electron/17.1.2",
    "Client-App": "DMMGamePlayer5",
    "Client-version": "17.1.2",
}

params = {
    "product_id": arg.product_id,
    "game_type": "GCL",
    "game_os": "win",
    "launch_type": "LIB",
    "mac_address": "00:11:22:33:44:55",
    "hdd_serial": "0000000011111111222222223333333344444444555555556666666677777777",
    "motherboard": "0000000011111111222222223333333344444444555555556666666677777777",
    "user_os": "win",
}


def dgp5_session():
    process = subprocess.Popen(
        args="", executable=arg.dmmgameplayer_path, shell=True, stdout=subprocess.PIPE
    )
    for line in process.stdout:
        text = line.decode("utf8").strip()
        if arg.debug:
            print(text)
        if "Parsing json string is " in text:
            install_data = json.loads(
                text.lstrip("Parsing json string is ").rstrip(".")
            )
        if 'Header key: "cookie"' in text:
            cookie = re.findall(r'"(.*?)"', text)[1]
            if not arg.non_kill:
                process.terminate()
            return install_data, cookie
    raise Exception("DMMGamePlayerの実行中にエラーが発生しました\n既に実行されているか実行中に終了した可能性があります")


install_data, headers["cookie"] = dgp5_session()

if not arg.game_path:
    for contents in install_data["contents"]:
        if contents["productId"] == arg.product_id:
            game_path = glob.glob(
                "{path}\*.exe._".format(path=contents["detail"]["path"])
            )[0][:-2]

response = requests.session().post(
    "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl",
    headers=headers,
    json=params,
    verify=False,
)
dmm_args = response.json()["data"]["execute_args"].split(" ")

subprocess.Popen([game_path, dmm_args[0], dmm_args[1]])
