import subprocess
import requests
import argparse
import re
import json
import glob
import win32crypt
import random
import hashlib

requests.packages.urllib3.disable_warnings()

argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)

argpar.add_argument("product_id", default=None)
argpar.add_argument("--game-path", default=False)
argpar.add_argument(
    "-dgp-path",
    "--dmmgameplayer-path",
    default="C:/Program Files/DMMGamePlayer/DMMGamePlayer.exe",
)
argpar.add_argument("--non-kill", action="store_true")
argpar.add_argument("--debug", action="store_true")
argpar.add_argument("--login-force", action="store_true")
argpar.add_argument("--anonymous", action="store_true")
arg = argpar.parse_args()

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

class dgp5_process:
    def __init__(self):
        self.process = subprocess.Popen(
            args="",
            executable=arg.dmmgameplayer_path,
            shell=True,
            stdout=subprocess.PIPE,
        )
        self.debug = False

    def get_install_data(self):
        for line in self.process.stdout:
            text = self._decode(line)
            if "Parsing json string is " in text:
                install_data = json.loads(
                    text.lstrip("Parsing json string is ").rstrip(".")
                )
                return install_data
        self._end_stdout()

    def get_client_data(self):
        for line in self.process.stdout:
            text = self._decode(line)
            if (
                "https://apidgp-gameplayer.games.dmm.com/v5/gameplayer/agreement/check"
                in text
            ):
                return self._req_body_to_dict(text)
        self._end_stdout()

    def get_cookie(self):
        for line in self.process.stdout:
            text = self._decode(line)
            if 'Header key: "cookie"' in text:
                cookie = re.findall(r'"(.*?)"', text)[1]
                return cookie
        self._end_stdout()

    def wait(self):
        for line in self.process.stdout:
            self._decode(line)

    def kill(self):
        self.process.terminate()

    def _req_body_to_dict(self, line):
        return json.loads(line.split(" :: Request body is ")[1][:-1])

    def _decode(self, line):
        text = line.decode("utf-8").strip()
        if self.debug:
            print(text)
        return text

    def _end_stdout(self):
        raise Exception("DMMGamePlayerの実行中にエラーが発生しました\n既に実行されているか実行中に終了した可能性があります")


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
}

if arg.anonymous:
    client_data = {
        "mac_address": gen_rand_address(),
        "hdd_serial": gen_rand_hex(),
        "motherboard": gen_rand_hex(),
        "user_os": "win",
    }



open("cookie.bytes", "a+")
with open("cookie.bytes", "rb") as f:
    blob = f.read()

process = dgp5_process()
process.debug = arg.debug
install_data = process.get_install_data()

if not arg.anonymous:
    client_data = process.get_client_data()[0]

if blob == b"" or arg.login_force:
    cookie = process.get_cookie()
    new_blob = win32crypt.CryptProtectData(cookie.encode(), "DMMGamePlayerFastLauncher")
    with open("cookie.bytes", "wb") as f:
        f.write(new_blob)
else:
    _, cookie = win32crypt.CryptUnprotectData(blob)

if not arg.game_path:
    for contents in install_data["contents"]:
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
                process.kill()
                raise Exception("ゲームのパスの検出に失敗しました")
            break
    else:
        process.kill()
        raise Exception(
            "product_id が無効です\n"
            + " ".join([contents["productId"] for contents in install_data["contents"]])
            + "から選択して下さい"
        )

headers["cookie"] = cookie
params.update(client_data)
print(params)

response = requests.post(
    "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl",
    headers=headers,
    json=params,
    verify=False,
).json()

if response["result_code"] == 100:
    dmm_args = response["data"]["execute_args"].split(" ")
    subprocess.Popen([game_path, dmm_args[0], dmm_args[1]])
else:
    with open("cookie.bytes", "wb") as f:
        f.write(b"")
    process.kill()
    raise Exception("起動にエラーが発生したため修復プログラムを実行しました\n" + json.dumps(response))

if arg.non_kill:
    process.wait()
else:
    process.kill()
