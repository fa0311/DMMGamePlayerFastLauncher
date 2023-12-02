import base64
import concurrent.futures
import hashlib
import json
import logging
import os
import random
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import psutil
import requests
import requests.cookies
import urllib3
from Crypto.Cipher import AES
from win32 import win32crypt

urllib3.disable_warnings()


class DgpSessionUtils:
    @staticmethod
    def gen_rand_hex():
        return hashlib.sha256(str(random.random()).encode()).hexdigest()

    @staticmethod
    def gen_rand_address():
        hex = DgpSessionUtils.gen_rand_hex()
        address = ""
        for x in range(12):
            address += hex[x]
            if x % 2 == 1:
                address += ":"
        return address[:-1]


class DMMAlreadyRunningException(Exception):
    pass


class DgpSessionV2:
    DGP5_PATH: Path
    DGP5_DATA_PATH: Path
    HEADERS: dict[str, str]
    DGP5_HEADERS: dict[str, str]
    DGP5_DEVICE_PARAMS: dict[str, str]
    DATA_DESCR: str
    db: sqlite3.Connection
    session: requests.Session
    cookies: requests.cookies.RequestsCookieJar
    cookies_kwargs = {
        "domain": ".dmm.com",
        "path": "/",
    }
    DGP5_PATH = Path(os.environ["PROGRAMFILES"]).joinpath("DMMGamePlayer")
    DGP5_DATA_PATH = Path(os.environ["APPDATA"]).joinpath("dmmgameplayer5")

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    }
    DGP5_HEADERS = {
        "Host": "apidgp-gameplayer.games.dmm.com",
        "Connection": "keep-alive",
        "User-Agent": "DMMGamePlayer5-Win/5.2.22 Electron/22.0.0",
        "Client-App": "DMMGamePlayer5",
        "Client-version": "5.2.22",
    }
    DGP5_DEVICE_PARAMS = {
        "mac_address": DgpSessionUtils.gen_rand_address(),
        "hdd_serial": DgpSessionUtils.gen_rand_hex(),
        "motherboard": DgpSessionUtils.gen_rand_hex(),
        "user_os": "win",
    }
    DATA_DESCR = "DMMGamePlayerFastLauncher"
    LOGGER = logging.getLogger("DgpSessionV2")

    API_DGP = "https://apidgp-gameplayer.games.dmm.com{0}"
    LAUNCH_CL = API_DGP.format("/v5/launch/cl")
    LAUNCH_PKG = API_DGP.format("/v5/launch/pkg")
    HARDWARE_CODE = API_DGP.format("/v5/hardwarecode")
    HARDWARE_CONF = API_DGP.format("/v5/hardwareconf")
    HARDWARE_LIST = API_DGP.format("/v5/hardwarelist")
    HARDWARE_REJECT = API_DGP.format("/v5/hardwarereject")
    GET_COOKIE = API_DGP.format("/getCookie")
    LOGIN_URL = API_DGP.format("/v5/loginurl")

    LOGIN = "https://accounts.dmm.com/service/login/token/=/path={token}/is_app=false"
    SIGNED_URL = "https://cdn-gameplayer.games.dmm.com/product/*"

    PROXY = {}

    def __init__(self):
        self.session = requests.session()
        self.session.proxies = self.PROXY
        self.cookies = self.session.cookies

    def __enter__(self):
        self.db = sqlite3.connect(self.DGP5_DATA_PATH.joinpath("Network", "Cookies"))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

    def write(self):
        aes_key = self.get_aes_key()
        for cookie_row in self.db.cursor().execute("select * from cookies"):
            try:
                value = self.cookies.get(cookie_row[3], domain=cookie_row[1], path=cookie_row[6]) or ""
                v10, nonce, _, _ = self.split_encrypted_data(cookie_row[5])
                cipher = AES.new(aes_key, AES.MODE_GCM, nonce)
                decrypt_data, mac = cipher.encrypt_and_digest(value.encode())
                data = self.join_encrypted_data(v10, nonce, decrypt_data, mac)
                self.db.execute(
                    "update cookies set encrypted_value = ? where name = ?",
                    (memoryview(data), cookie_row[3]),
                )
            except Exception as e:
                self.LOGGER.warn("Failed to decrypt cookie: %s", cookie_row[3], exc_info=e)
        self.db.commit()

    def read(self):
        aes_key = self.get_aes_key()
        for cookie_row in self.db.cursor().execute("select * from cookies"):
            try:
                _, nonce, data, mac = self.split_encrypted_data(cookie_row[5])
                cipher = AES.new(aes_key, AES.MODE_GCM, nonce)
                value = cipher.decrypt_and_verify(data, mac).decode()
                cookie_data = {
                    "name": cookie_row[3],
                    "value": value,
                    "domain": cookie_row[1],
                    "path": cookie_row[6],
                    "secure": cookie_row[8],
                }
                self.cookies.set_cookie(requests.cookies.create_cookie(**cookie_data))
            except Exception as e:
                self.LOGGER.warn("Failed to decrypt cookie: %s", cookie_row[3], exc_info=e)

    def write_bytes(self, file: str):
        contents = []
        for cookie in self.cookies:
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
                rest=cookie._rest,  # type: ignore
            )
            contents.append(cookie_dict)
        data = win32crypt.CryptProtectData(
            json.dumps(contents).encode(),
            self.DATA_DESCR,
        )
        with open(file, "wb") as f:
            f.write(data)

    def read_bytes(self, file: str):
        with open(file, "rb") as f:
            data = f.read()
            _, contents = win32crypt.CryptUnprotectData(data)
            for cookie in json.loads(contents):
                self.cookies.set_cookie(requests.cookies.create_cookie(**cookie))

    def get(self, url: str, params=None, **kwargs) -> requests.Response:
        self.LOGGER.info("params %s", params)
        res = self.session.get(url, headers=self.HEADERS, params=params, **kwargs)
        return self.logger(res)

    def post(self, url: str, json=None, **kwargs) -> requests.Response:
        self.LOGGER.info("json %s", json)
        res = self.session.post(url, headers=self.HEADERS, json=json, **kwargs)
        return self.logger(res)

    def get_dgp(self, url: str, params=None, **kwargs) -> requests.Response:
        self.LOGGER.info("params %s", params)
        res = self.session.get(url, headers=self.DGP5_HEADERS, params=params, **kwargs)
        return self.logger(res)

    def post_dgp(self, url: str, json=None, **kwargs) -> requests.Response:
        self.LOGGER.info("json %s", json)
        res = self.session.post(url, headers=self.DGP5_HEADERS, json=json, **kwargs)
        return self.logger(res)

    def post_device_dgp(self, url: str, json=None, **kwargs) -> requests.Response:
        json = (json or {}) | self.DGP5_DEVICE_PARAMS
        return self.post_dgp(url, json=json, **kwargs)

    def logger(self, res: requests.Response) -> requests.Response:
        if res.headers.get("Content-Type") == "application/json":
            self.LOGGER.info("application/json %s", res.text)
        return res

    def lunch(self, product_id: str, game_type: str) -> requests.Response:
        if game_type == "GCL":
            url = self.LAUNCH_CL
        elif game_type == "ACL":
            url = self.LAUNCH_CL
        elif game_type == "AMAIN":
            url = self.LAUNCH_PKG
        else:
            raise Exception("Unknown game_type: " + game_type + " " + product_id)
        json = {
            "product_id": product_id,
            "game_type": game_type,
            "game_os": "win",
            "launch_type": "LIB",
        }
        return self.post_device_dgp(url, json=json, verify=False)

    def login(self):
        response = self.get(self.LOGIN_URL)
        url = response.json()["data"]["url"]
        token = urlparse(url).path.split("path=")[-1]
        try:
            self.get(url)
            self.get(self.LOGIN.format(token=token))
        except Exception:
            pass

    def download(self, filelist_url: str, output: Path):
        token = self.post_dgp(self.GET_COOKIE, json={"url": self.SIGNED_URL}).json()
        signed = {
            "Policy": token["policy"],
            "Signature": token["signature"],
            "Key-Pair-Id": token["key"],
        }
        url = self.API_DGP.format(filelist_url)
        data = self.get_dgp(url).json()

        def download_save(file: dict):
            content = self.get(data["data"]["domain"] + "/" + file["path"], params=signed).content
            path = output.joinpath(file["local_path"][1:])
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            return file["size"], file

        if data["data"]["page"] > 1:
            raise Exception("Not supported multiple pages")

        size = sum([x["size"] for x in data["data"]["file_list"]])
        download_size = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            tasks = [pool.submit(lambda x: download_save(x), x) for x in data["data"]["file_list"]]
            for task in concurrent.futures.as_completed(tasks):
                res = task.result()
                download_size += res[0]
                yield download_size / size, res[1]

    def get_config(self):
        with open(self.DGP5_DATA_PATH.joinpath("dmmgame.cnf"), "r", encoding="utf-8") as f:
            config = f.read()
        res = json.loads(config)
        self.LOGGER.info("READ dmmgame.cnf %s", res)
        return res

    def set_config(self, config):
        with open(self.DGP5_DATA_PATH.joinpath("dmmgame.cnf"), "w", encoding="utf-8") as f:
            f.write(json.dumps(config, indent=4))

    def get_aes_key(self):
        with open(self.DGP5_DATA_PATH.joinpath("Local State"), "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"].encode())[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key

    def split_encrypted_data(self, encrypted_data: bytes) -> tuple[bytes, bytes, bytes, bytes]:
        return (
            encrypted_data[0:3],
            encrypted_data[3:15],
            encrypted_data[15:-16],
            encrypted_data[-16:],
        )

    def join_encrypted_data(self, v10: bytes, nonce: bytes, data: bytes, mac: bytes) -> bytes:
        return v10 + nonce + data + mac

    @staticmethod
    def read_cookies(path: Path) -> "DgpSessionV2":
        if DgpSessionV2.is_running_dmm():
            raise DMMAlreadyRunningException("DMMGamePlayer is already running")

        session = DgpSessionV2()
        session.read_bytes(str(path))
        session.login()
        session.write_bytes(str(path))
        return session

    @staticmethod
    def is_running_dmm() -> bool:
        for proc in psutil.process_iter():
            try:
                if Path(proc.exe()) == DgpSessionV2.DGP5_PATH.joinpath("DMMGamePlayer.exe"):
                    return True
            except Exception:
                pass
        return False
