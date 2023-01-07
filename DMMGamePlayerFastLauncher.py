import subprocess
import requests
import argparse
import json
import glob
import win32crypt
import ctypes
import random
import hashlib
import sqlite3
import os
import time
from urllib.parse import urlparse


class DgpSession:
    DGP5_PATH: str
    HEADERS: dict[str, str]
    PROXY: dict[str, str | None]
    DGP5_HEADERS: dict[str, str]
    DGP5_LAUNCH_PARAMS: dict[str, str]
    db: sqlite3.Connection
    session: requests.Session
    cookies: requests.cookies.RequestsCookieJar

    def __init__(self, https_proxy_uri: str | None = None):
        requests.packages.urllib3.disable_warnings()
        self.DGP5_PATH = os.environ["APPDATA"] + "\\dmmgameplayer5\\"
        self.PROXY = {"https": https_proxy_uri}
        self.HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        }
        self.DGP5_HEADERS = {
            "Host": "apidgp-gameplayer.games.dmm.com",
            "Connection": "keep-alive",
            "User-Agent": "DMMGamePlayer5-Win/17.1.2 Electron/17.1.2",
            "Client-App": "DMMGamePlayer5",
            "Client-version": "17.1.2",
        }
        self.DGP5_LAUNCH_PARAMS = {
            "game_type": "GCL",
            "game_os": "win",
            "launch_type": "LIB",
            "mac_address": self.gen_rand_address(),
            "hdd_serial": self.gen_rand_hex(),
            "motherboard": self.gen_rand_hex(),
            "user_os": "win",
        }
        self.open()

    def gen_rand_hex(self):
        return hashlib.sha256(str(random.random()).encode()).hexdigest()

    def gen_rand_address(self):
        hex = self.gen_rand_hex()
        address = ""
        for x in range(12):
            address += hex[x]
            if x % 2 == 1:
                address += ":"
        return address[:-1]

    def write(self):
        for cookie_row in self.db.cursor().execute("select * from cookies"):
            name = cookie_row[3]
            value = self.session.cookies.get(name)
            if value != None:
                self.db.execute(
                    f"update cookies set value = '{value}' where name = '{name}'"
                )
        self.db.commit()

    def read(self):
        for cookie_row in self.db.cursor().execute("select * from cookies"):
            cookie_data = {
                "name": cookie_row[3],
                "value": cookie_row[4],
                "domain": cookie_row[1],
                "path": cookie_row[6],
                "secure": cookie_row[8],
            }
            self.session.cookies.set_cookie(
                requests.cookies.create_cookie(**cookie_data)
            )

    def write_cache(self, file: str = "cookie.bytes"):
        contents = []
        for cookie in self.session.cookies:
            cookie_dict = dict(
                version=cookie.version,
                name=cookie.name,
                value=cookie.value,
                port=cookie.port,
                domain=cookie.domain,
                path=cookie.path,
                secure=cookie.secure,
                expires=cookie.expires,
                discard=cookie.discard,
                comment=cookie.comment,
                comment_url=cookie.comment_url,
                rfc2109=cookie.rfc2109,
                rest=cookie._rest,
            )
            contents.append(cookie_dict)
        data = win32crypt.CryptProtectData(
            json.dumps(contents).encode(), "DMMGamePlayerFastLauncher"
        )
        with open(file, "wb") as f:
            f.write(data)

    def read_cache(self, file: str = "cookie.bytes"):
        open(file, "a+")
        with open(file, "rb") as f:
            data = f.read()
            _, contents = win32crypt.CryptUnprotectData(data)
            for cookie in json.loads(contents):
                self.session.cookies.set_cookie(
                    requests.cookies.create_cookie(**cookie)
                )

    def get(self, url: str) -> requests.Response:
        return self.session.get(url, headers=self.HEADERS, proxies=self.PROXY)

    def post(self, url: str) -> requests.Response:
        return self.session.post(url, headers=self.HEADERS, proxies=self.PROXY)

    def lunch(self, url: str, product_id: str) -> requests.Response:
        json = {"product_id": product_id}
        json.update(self.DGP5_LAUNCH_PARAMS)
        return self.session.post(
            url,
            headers=self.DGP5_HEADERS,
            proxies=self.PROXY,
            json=json,
            verify=False,
        )

    def get_config(self):
        with open(self.DGP5_PATH + "dmmgame.cnf", "r", encoding="utf-8") as f:
            config = f.read()
        return json.loads(config)

    def open(self):
        self.db = sqlite3.connect(self.DGP5_PATH + "Network/Cookies")
        self.session = requests.session()
        self.cookies = self.session.cookies

    def close(self):
        self.db.close()


argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)
argpar.add_argument("product_id", default=None)
argpar.add_argument("--game-path", default=None)
argpar.add_argument("--game-args", default=None)
argpar.add_argument("--login-force", action="store_true")
argpar.add_argument("--skip-exception", action="store_true")
argpar.add_argument("--https-proxy-uri", default=None)
argpar.add_argument("--non-request-admin", action="store_true")
try:
    arg = argpar.parse_args()
except:
    raise Exception(
        "\n".join(
            [
                "Could not parse argument.",
                "Is the product_id specified correctly?",
                "https://github.com/fa0311/DMMGamePlayerFastLauncher/blob/master/docs/README-advance.md#%E5%BC%95%E6%95%B0",
            ]
        )
    )


session = DgpSession(arg.https_proxy_uri)

try:
    session.read()
except:
    print("Read Error")
    try:
        session.read_cache()
    except:
        print("Read Cache Error")

if session.cookies.get("login_session_id") == None or arg.login_force:
    response = session.get("https://apidgp-gameplayer.games.dmm.com/v5/loginurl")
    url = response.json()["data"]["url"]
    token = urlparse(url).path.split("path=")[-1]
    session.get(url)
    res = session.get(
        f"https://accounts.dmm.com/service/login/token/=/path={token}/is_app=false"
    )

if session.cookies.get("login_session_id") == None:
    try:
        session.read_cache()
    except:
        print("Read Cache Error")

if session.cookies.get("login_session_id") == None:
    if not arg.skip_exception:
        raise Exception(
            "\n".join(
                [
                    "Login failed.",
                    "If DMMGamePlayer is running, exit it or Please start DMMGamePlayer and login again.",
                ]
            )
        )

try:
    session.write()
except:
    print("Write Error")


try:
    session.write_cache()
except:
    print("Write Cache Error")

session.close()

dpg5_config = session.get_config()
if arg.game_path is None:
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
                if not (
                    "unity" in lower_path
                    or "install" in lower_path
                    or "help" in lower_path
                ):
                    game_path = path
                    break
            else:
                if not arg.skip_exception:
                    raise Exception(
                        "\n".join(
                            [
                                "Game path detection failed.",
                                "Try using --game_path.",
                                "https://github.com/fa0311/DMMGamePlayerFastLauncher/blob/master/docs/README-advance.md#game-path",
                            ]
                        )
                    )
            break
    else:
        if not arg.skip_exception:
            message = [
                "product_id is invalid.",
                "Please select:",
                " ".join(
                    [contents["productId"] for contents in dpg5_config["contents"]]
                ),
            ]
            raise Exception("\n".join(message))
else:
    game_path = arg.game_path

response = session.lunch(
    "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl", arg.product_id
).json()

if response["result_code"] == 100:
    dmm_args = response["data"]["execute_args"].split(" ")
    if arg.game_args is not None:
        dmm_args = dmm_args + arg.game_args.split(" ")
    print(game_path)
    start_time = time.time()
    process = subprocess.Popen(
        [game_path] + dmm_args, shell=True, stdout=subprocess.PIPE
    )
    for line in process.stdout:
        text = line.decode("utf-8").strip()
        print(text)
    if time.time() - start_time < 2 and not arg.skip_exception:
        if response["data"]["is_administrator"] and not arg.non_request_admin:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", game_path, response["data"]["execute_args"], None, 1
                )
            else:
                raise Exception(
                    "Game did not start. Please allow administrative privileges."
                )
        elif response["data"]["is_administrator"]:
            raise Exception(
                "Game did not start. Please allow administrative privileges."
            )
        else:
            if not arg.skip_exception:
                raise Exception(
                    "Game did not start. There may be an update to the game."
                )
elif response["result_code"] == 801:
    if not arg.skip_exception:
        raise Exception(
            "\n".join(["Access from outside Japan is prohibited", json.dumps(response)])
        )
else:
    if not arg.skip_exception:
        raise Exception("\n".join(["Error in startup.", json.dumps(response)]))
