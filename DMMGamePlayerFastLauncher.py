import subprocess
import requests
import argparse
import json
import glob
import win32crypt
import random
import hashlib
import sqlite3
import os


def gen_rand_hex():
    return hashlib.sha256(str(random.random()).encode()).hexdigest()


def gen_rand_address():
    hex = gen_rand_hex()
    address = ""
    for x in range(12):
        address += hex[x]
        if x % 2 == 1:
            address += ":"
    return address[:-1]


def get_dgp5_session(dgp5_path):
    db = sqlite3.connect(dgp5_path + "Network/Cookies").cursor()
    session = requests.session()
    for cookie_row in db.execute("select * from cookies"):
        cookie_data = {
            "name": cookie_row[3],
            "value": cookie_row[4],
            "domain": cookie_row[1],
            "path": cookie_row[6],
            "secure": cookie_row[8],
        }
        session.cookies.set_cookie(requests.cookies.create_cookie(**cookie_data))
    return session


def get_dpg5_config(dgp5_path):
    with open(dgp5_path + "dmmgame.cnf", "r") as f:
        config = f.read()
    return json.loads(config)


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
}
DGP5_HEADERS = {
    "Host": "apidgp-gameplayer.games.dmm.com",
    "Connection": "keep-alive",
    "User-Agent": "DMMGamePlayer5-Win/17.1.2 Electron/17.1.2",
    "Client-App": "DMMGamePlayer5",
    "Client-version": "17.1.2",
}
DGP5_LAUNCH_PARAMS = {
    "product_id": "umamusume",
    "game_type": "GCL",
    "game_os": "win",
    "launch_type": "LIB",
    "mac_address": gen_rand_address(),
    "hdd_serial": gen_rand_hex(),
    "motherboard": gen_rand_hex(),
    "user_os": "win",
}

dgp5_path = os.environ["APPDATA"] + "/dmmgameplayer5/"
requests.packages.urllib3.disable_warnings()

argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)
argpar.add_argument("product_id", default=None)
argpar.add_argument("--game-path", default=False)
argpar.add_argument("--login-force", action="store_true")
arg = argpar.parse_args()


open("cookie.bytes", "a+")
with open("cookie.bytes", "rb") as f:
    blob = f.read()
if blob == b"" or arg.login_force:
    session = get_dgp5_session(dgp5_path)
    response = session.get(
        "https://www.dmm.com/my/-/login/auth/=/direct_login=1/path=DRVESVwZTkVPEh9cXltIVA4IGV5ETRQWVlID",
        headers=HEADERS,
    )
    if session.cookies.get("login_session_id") == None:
        raise Exception(
            "ログインに失敗しました\nDMMGamePlayerでログインしていない時またはDMMGamePlayerが起動している時にこのエラーが発生する可能性があります"
        )
    contents = json.dumps(
        {
            "login_session_id": session.cookies.get("login_session_id"),
            "login_secure_id": session.cookies.get("login_secure_id"),
        }
    )
    new_blob = win32crypt.CryptProtectData(
        contents.encode(), "DMMGamePlayerFastLauncher"
    )
    with open("cookie.bytes", "wb") as f:
        f.write(new_blob)
else:
    _, contents = win32crypt.CryptUnprotectData(blob)
cookie = json.loads(contents)

dpg5_config = get_dpg5_config(dgp5_path)
if not arg.game_path:
    for contents in dpg5_config["contents"]:
        if contents["productId"] == arg.product_id:
            game_path_list = glob.glob(
                "{path}\*.exe._".format(path=contents["detail"]["path"])
            )
            if len(game_path_list) > 0:
                game_path = game_path_list[0][:-2]
                break
            game_path_list = glob.glob(
                "{path}\*.exe".format(path=contents["detail"]["path"])
            )
            for path in game_path_list:
                lower_path = path.lower()
                if not ("unity" in lower_path or "install" in lower_path):
                    game_path = path
                    break
            else:
                raise Exception("ゲームのパスの検出に失敗しました")
            break
    else:
        raise Exception(
            "product_id が無効です\n"
            + " ".join([contents["productId"] for contents in dpg5_config["contents"]])
            + "から選択して下さい"
        )

response = requests.post(
    "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl",
    cookies=cookie,
    headers=DGP5_HEADERS,
    json=DGP5_LAUNCH_PARAMS,
    verify=False,
).json()

if response["result_code"] == 100:
    dmm_args = response["data"]["execute_args"].split(" ")
    subprocess.Popen([game_path, dmm_args[0], dmm_args[1]])
else:
    with open("cookie.bytes", "wb") as f:
        f.write(b"")
    raise Exception("起動にエラーが発生したため修復プログラムを実行しました\n" + json.dumps(response))