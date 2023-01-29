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
import win32security
import sys


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


class ErrorManagerType:
    message: str
    solution: str | None
    url: str | None

    def __init__(
        self,
        message: str,
        solution: str | None = None,
        url: str | None = None,
    ):
        self.message = message
        self.solution = solution
        self.url = url


class ErrorManager:
    skip: bool = False
    argument_error: ErrorManagerType = ErrorManagerType(
        message="Could not parse argument.",
        solution="Is the product_id specified correctly?",
        url="https://github.com/fa0311/DMMGamePlayerFastLauncher/blob/master/docs/README-advance.md#引数",
    )
    login_error: ErrorManagerType = ErrorManagerType(
        message="Login failed",
        solution="If DMMGamePlayer is running, exit it or Please start DMMGamePlayer and login again.",
    )
    game_path_error: ErrorManagerType = ErrorManagerType(
        message="Game path detection failed.",
        solution="Try using --game_path.",
        url="https://github.com/fa0311/DMMGamePlayerFastLauncher/blob/master/docs/README-advance.md#game-path",
    )
    product_id_error: ErrorManagerType = ErrorManagerType(
        message="product_id is invalid.",
        solution="Please select:",
    )
    permission_error: ErrorManagerType = ErrorManagerType(
        message="Game did not start.",
        solution="Please allow administrative privileges.",
    )
    process_error: ErrorManagerType = ErrorManagerType(
        message="Game did not start.",
        solution="There may be an update to the game.",
    )
    access_error: ErrorManagerType = ErrorManagerType(
        message="Access from outside Japan is prohibited.",
        solution="Try using --https-proxy-uri or VPN.",
        url="https://github.com/fa0311/DMMGamePlayerFastLauncher/blob/master/docs/README-advance.md#https-proxy-uri",
    )
    auth_device_error: ErrorManagerType = ErrorManagerType(
        message="Failed to authenticate device.",
        solution="Check the box for 'DMMGAMEPLAYER Settings' > 'デバイス設定' > 'デバイス認証' > '有料ゲームと一部基本無料ゲームでデバイス認証'",
        url="https://github.com/fa0311/DMMGamePlayerFastLauncher/blob/master/docs/README-advance.md#failed-to-authenticate-deviceというエラーが出る",
    )
    startup_error: ErrorManagerType = ErrorManagerType(
        message="Error in startup.",
        solution="Report an Issues.",
        url="https://github.com/fa0311/DMMGamePlayerFastLauncher/issues",
    )

    elevate_admin_error: ErrorManagerType = ErrorManagerType(
        message="Failed to elevate to administrator privileges.",
        solution="Report an Issues.",
        url="https://github.com/fa0311/DMMGamePlayerFastLauncher/issues",
    )

    def error(self, error: ErrorManagerType, log: str | None = None):
        output = filter(
            lambda x: x != None,
            [error.message, error.solution, error.url, log],
        )
        if self.skip:
            self.info("\n".join(output))
        else:
            raise Exception("\n".join(output))

    def info(self, text: str):
        print(text)


class ProcessManager:
    non_request_admin: bool = False
    non_bypass_uac: bool = False
    error_manager: ErrorManager

    def __init__(self, error_manager: ErrorManager) -> None:
        self.error_manager = error_manager

    def run(
        self, args: dict[str], admin: bool = False, force: bool = False
    ) -> subprocess.Popen[bytes] | None:
        print(" ".join(args))
        if admin:
            if not self.non_bypass_uac and not force:
                run_bypass_uac()
            elif self.non_request_admin:
                self.error_manager.error(error=ErrorManager.permission_error)
            else:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", args[0], " ".join(args[1:]), None, 1
                )
        else:
            return subprocess.Popen(
                args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )


def get_sid() -> str:
    desc = win32security.GetFileSecurity(".", win32security.OWNER_SECURITY_INFORMATION)
    sid = desc.GetSecurityDescriptorOwner()
    sidstr = win32security.ConvertSidToStringSid(sid)
    return sidstr


def run_bypass_uac():
    schtasks_file = "schtasks_v1_" + os.getlogin()
    schtasks_name = f"\Microsoft\Windows\DMMGamePlayerFastLauncher\{schtasks_file}"

    run_args = [arg.schtasks_path, "/run", "/tn", schtasks_name]

    if process_manager.run(run_args).wait() == 1:
        schtasks_xml_path = (
            r"{appdata}\DMMGamePlayerFastLauncher\assets\{name}.xml".format(
                appdata=os.environ["APPDATA"], name=schtasks_file
            )
        )
        schtasks_task_path = (
            r"{appdata}\DMMGamePlayerFastLauncher\Tools\Task.exe".format(
                appdata=os.environ["APPDATA"]
            )
        )
        with open("assets/template.xml", "r") as f:
            template = f.read()

        with open(f"assets/{schtasks_file}.xml", "w") as f:
            f.write(
                template.replace(r"{{UID}}", schtasks_file)
                .replace(r"{{SID}}", get_sid())
                .replace(r"{{COMMAND}}", schtasks_task_path)
                .replace(r"{{WORKING_DIRECTORY}}", os.getcwd())
            )

        create_args = [
            arg.schtasks_path,
            "/create",
            "/xml",
            schtasks_xml_path,
            "/tn",
            schtasks_name,
        ]
        process_manager.run(create_args, admin=True, force=True)
        time.sleep(3)
        process_manager.run(run_args).wait()
    time.sleep(5)
    sys.exit()


error_manager = ErrorManager()
process_manager = ProcessManager(error_manager)

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
argpar.add_argument("--non-bypass-uac", action="store_true")
argpar.add_argument("--schtasks-path", default="schtasks.exe")

try:
    arg = argpar.parse_args()
    error_manager.skip = arg.skip_exception
    process_manager.non_request_admin = arg.non_request_admin
    process_manager.non_bypass_uac = arg.non_bypass_uac
except:
    error_manager.error(error=ErrorManager.argument_error)

session = DgpSession(arg.https_proxy_uri)

try:
    session.read()
except:
    error_manager.info("Read Error")
    try:
        session.read_cache()
    except:
        error_manager.info("Read Cache Error")

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
        error_manager.info("Read Cache Error")

if session.cookies.get("login_session_id") == None:
    error_manager.error(error=ErrorManager.login_error)

try:
    session.write()
except:
    error_manager.info("Write Error")


try:
    session.write_cache()
except:
    error_manager.info("Write Cache Error")

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
                if not all([i in lower_path for i in ["unity", "install", "help"]]):
                    game_path = path
                    break
            else:
                error_manager.error(error=ErrorManager.game_path_error)
            break
    else:
        ids = ", ".join([contents["productId"] for contents in dpg5_config["contents"]])
        error_manager.error(error=ErrorManager.product_id_error, log=ids)
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
    process = process_manager.run([game_path] + dmm_args)
    for line in process.stdout:
        text = line.decode("utf-8").strip()
        print(text)
    if time.time() - start_time < 2:
        if response["data"]["is_administrator"]:
            process = process_manager.run([game_path] + dmm_args, admin=True)
        else:
            error_manager.error(
                error=ErrorManager.startup_error, log=json.dumps(response)
            )

elif response["result_code"] == 307:
    error_manager.error(error=ErrorManager.auth_device_error)
elif response["result_code"] == 801:
    error_manager.error(error=ErrorManager.access_error)
else:
    error_manager.error(error=ErrorManager.startup_error, log=json.dumps(response))
