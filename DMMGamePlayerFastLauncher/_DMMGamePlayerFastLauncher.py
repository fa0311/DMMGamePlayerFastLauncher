# type: ignore
import subprocess
import argparse
import json
import glob
import ctypes
import os
import time
from urllib.parse import urlparse
import win32security
import sys
from lib.DGPSession import *
import logging


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


class LogHandler(logging.Handler):
    records: list[object] = []

    def __init__(self, level=logging.NOTSET):
        super().__init__(level=level)

    def emit(self, record):
        self.records.append(record)

    def output(self) -> list[str]:
        return [self.format(record) for record in self.records]


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

    format: logging.Formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    logger: logging.Logger = logging.getLogger(__qualname__)
    logHandler: LogHandler = LogHandler()
    streamHandler: logging.StreamHandler = logging.StreamHandler()

    def __init__(self) -> None:
        self.streamHandler.setFormatter(self.format)
        self.logHandler.setFormatter(self.format)
        self.set_logger(self.logger)

    def error(self, error: ErrorManagerType, log: str | None = None):
        output = filter(
            lambda x: x is not None,
            [error.solution, error.url, log],
        )
        if self.skip:
            self.logger.warning("\n".join(output), exc_info=True)
        else:
            raise Exception("\n".join([error.message] + self.logHandler.output() + list(output)))

    def set_logger(self, logger: logging.Logger):
        logger.setLevel(logging.DEBUG)
        if os.environ.get("ENV") == "DEVELOP":
            logger.addHandler(self.streamHandler)
        else:
            logger.addHandler(self.logHandler)


class ProcessManager:
    non_request_admin: bool = False
    non_bypass_uac: bool = False
    error_manager: ErrorManager

    def __init__(self, error_manager: ErrorManager) -> None:
        self.error_manager = error_manager

    def run(self, args: dict[str], admin: bool = False, force: bool = False) -> subprocess.Popen[bytes] | None:
        error_manager.logger.info(" ".join(args))
        if admin:
            if not self.non_bypass_uac and not force:
                error_manager.logger.info("Run Bypass UAC")
                run_bypass_uac()
            elif self.non_request_admin:
                self.error_manager.error(error=ErrorManager.permission_error)
            else:
                args = [f'"{arg}"' for arg in args]
                ctypes.windll.shell32.ShellExecuteW(None, "runas", args[0], " ".join(args[1:]), None, 1)
        else:
            return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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
        schtasks_xml_path = r"{appdata}\DMMGamePlayerFastLauncher\assets\{name}.xml".format(appdata=os.environ["APPDATA"], name=schtasks_file)
        schtasks_task_path = r"{appdata}\DMMGamePlayerFastLauncher\Tools\Task.exe".format(appdata=os.environ["APPDATA"])
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
argpar.add_argument("--force-bypass-uac", action="store_true")
argpar.add_argument("--schtasks-path", default="schtasks.exe")


try:
    arg = argpar.parse_args()
    error_manager.skip = arg.skip_exception
    process_manager.non_request_admin = arg.non_request_admin
    process_manager.non_bypass_uac = arg.non_bypass_uac
except Exception as e:
    error_manager.error(error=ErrorManager.argument_error)

error_manager.logger.info(" ".join(sys.argv))

try:
    error_manager.logger.info("Start DgpSession")
    session = DgpSession(arg.https_proxy_uri)
    error_manager.set_logger(session.logger)
except:
    error_manager.logger.info("DgpSession Error", exc_info=True)

try:
    error_manager.logger.info("Read DB")
    session.read()
except:
    error_manager.logger.info("Read Error", exc_info=True)


if len(session.cookies.items()) == 0:
    try:
        error_manager.logger.info("Read Cache")
        session.read_cache()
    except:
        error_manager.logger.info("Read Cache Error", exc_info=True)

if arg.login_force:
    try:
        requests.cookies.remove_cookie_by_name(session.cookies, "login_session_id")
    except:
        pass

if session.cookies.get("login_session_id", **session.cookies_kwargs) == None:
    error_manager.logger.info("Request Session Id")
    response = session.get("https://apidgp-gameplayer.games.dmm.com/v5/loginurl")
    url = response.json()["data"]["url"]
    token = urlparse(url).path.split("path=")[-1]
    session.get(url)
    login_url = "https://accounts.dmm.com/service/login/token/=/path={token}/is_app=false"
    try:
        session.get(login_url)
    except:
        pass

if session.cookies.get("login_session_id", **session.cookies_kwargs) == None:
    try:
        error_manager.logger.info("Read Cookies Cache")
        session.read_cache()
    except:
        error_manager.logger.info("Read Cache Error", exc_info=True)

if session.cookies.get("login_session_id", **session.cookies_kwargs) == None:
    error_manager.error(error=ErrorManager.login_error)

try:
    error_manager.logger.info("Write DB")
    session.write()
except:
    error_manager.logger.info("Write Error", exc_info=True)


try:
    error_manager.logger.info("Write Cache")
    session.write_cache()
except:
    error_manager.logger.info("Write Cache Error", exc_info=True)

session.close()

try:
    error_manager.logger.info("Read DGP Congig")
    dpg5_config = session.get_config()
except:
    error_manager.logger.info("Read DGP Congig Error", exc_info=True)

if arg.game_path is None:
    for contents in dpg5_config["contents"]:
        if contents["productId"] == arg.product_id:
            game_path_list = glob.glob("{path}\*.exe._".format(path=contents["detail"]["path"]))
            if len(game_path_list) > 0:
                game_path = game_path_list[0][:-2]
                break
            game_path_list = glob.glob("{path}\*.exe".format(path=contents["detail"]["path"]))
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

error_manager.logger.info("Request to Launch Token")

launch_url = "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl"
response = session.lunch(launch_url, arg.product_id).json()

if response["result_code"] == 100:
    dmm_args = response["data"]["execute_args"].split(" ")
    if arg.game_args is not None:
        dmm_args = dmm_args + arg.game_args.split(" ")
    if arg.force_bypass_uac and not arg.non_bypass_uac and response["data"]["is_administrator"]:
        error_manager.logger.info("Run Bypass UAC")
        run_bypass_uac()
    start_time = time.time()
    process = process_manager.run([game_path] + dmm_args)
    for line in process.stdout:
        text = line.decode("utf-8").strip()
        print(text)  # GameLog
    if time.time() - start_time < 2:
        if response["data"]["is_administrator"]:
            process = process_manager.run([game_path] + dmm_args, admin=True)
        else:
            error_manager.error(error=ErrorManager.startup_error, log=json.dumps(response))

elif response["result_code"] == 307:
    error_manager.error(error=ErrorManager.auth_device_error)
elif response["result_code"] == 801:
    error_manager.error(error=ErrorManager.access_error)
else:
    error_manager.error(error=ErrorManager.startup_error, log=json.dumps(response))
