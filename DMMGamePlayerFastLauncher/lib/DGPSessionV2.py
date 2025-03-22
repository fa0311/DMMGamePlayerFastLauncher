import base64
import concurrent.futures
import hashlib
import json
import logging
import os
import random
from pathlib import Path
from urllib.parse import parse_qsl

import psutil
import requests
import requests.cookies
import urllib3
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from win32 import win32crypt

urllib3.disable_warnings()


def text_factory(x: bytes):
    try:
        return x.decode("utf-8")
    except Exception:
        return x


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
    DGP5_PATH = Path(os.environ["PROGRAMFILES"]).joinpath("DMMGamePlayer")
    DGP5_DATA_PATH = Path(os.environ["APPDATA"]).joinpath("dmmgameplayer5")

    HEADERS: dict[str, str] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }
    DGP5_HEADERS: dict[str, str] = {
        "Connection": "keep-alive",
        "User-Agent": "DMMGamePlayer5-Win/5.3.25 Electron/34.3.0",
        "Client-App": "DMMGamePlayer5",
        "Client-Version": "5.3.25",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ja",
        "Priority": "u=1, i",
    }
    DGP5_DEVICE_PARAMS: dict[str, str] = {
        "mac_address": DgpSessionUtils.gen_rand_address(),
        "hdd_serial": DgpSessionUtils.gen_rand_hex(),
        "motherboard": DgpSessionUtils.gen_rand_hex(),
        "user_os": "win",
    }
    DATA_DESCR: str = "DMMGamePlayerFastLauncher"
    LOGGER = logging.getLogger("DgpSessionV2")

    API_DGP = "https://apidgp-gameplayer.games.dmm.com{0}"
    LAUNCH_CL = API_DGP.format("/v5/r2/launch/cl")
    LAUNCH_PKG = API_DGP.format("/v5/launch/pkg")
    HARDWARE_CODE = API_DGP.format("/v5/hardwarecode")
    HARDWARE_CONF = API_DGP.format("/v5/hardwareconf")
    HARDWARE_LIST = API_DGP.format("/v5/hardwarelist")
    HARDWARE_REJECT = API_DGP.format("/v5/hardwarereject")
    ACCESS_TOKEN = API_DGP.format("/v5/auth/accesstoken/issue")
    LOGIN_URL = API_DGP.format("/v5/auth/login/url")
    SIGNED_URL = "https://cdn-gameplayer.games.dmm.com/product/*"
    WEB_LOGIN_URL = "https://accounts.dmm.com/service/oauth/=/path="
    PROXY = {}

    actauth: dict[str, str]
    session: requests.Session

    def __init__(self):
        self.actauth = {}
        self.session = requests.Session()
        self.session.cookies = requests.cookies.RequestsCookieJar()
        self.session.cookies.set("age_check_done", "0", domain=".dmm.com", path="/")
        self.session.proxies = self.PROXY

    def write_safe(self, data: bytes):
        file = self.DGP5_DATA_PATH.joinpath("authAccessTokenData.enc")
        with open(file, "wb") as f:
            f.write(data)

    def read_safe(self):
        file = self.DGP5_DATA_PATH.joinpath("authAccessTokenData.enc")
        if file.exists():
            with open(file, "rb") as f:
                return f.read()
        return None

    def write(self):
        aes_key = self.get_aes_key()
        v10 = "v10".encode()
        nonce = get_random_bytes(12)
        value = json.dumps(self.actauth).encode()
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce)
        data, mac = cipher.encrypt_and_digest(value)
        enc = self.join_encrypted_data(v10, nonce, data, mac)
        self.write_safe(enc)

    def read(self):
        aes_key = self.get_aes_key()
        enc = self.read_safe()
        if enc:
            v10, nonce, data, mac = self.split_encrypted_data(enc)
            cipher = AES.new(aes_key, AES.MODE_GCM, nonce)
            value = cipher.decrypt_and_verify(data, mac)
            self.actauth = json.loads(value.decode())
        else:
            self.actauth = {}

    def write_bytes(self, file: str):
        data = win32crypt.CryptProtectData(
            json.dumps(self.actauth).encode(),
            self.DATA_DESCR,
        )
        with open(file, "wb") as f:
            f.write(data)

    def read_bytes(self, file: str):
        with open(file, "rb") as f:
            data = f.read()
        _, contents = win32crypt.CryptUnprotectData(data)
        self.actauth = json.loads(contents.decode())

    def get_access_token(self):
        return self.actauth.get("accessToken")

    def get_headers(self):
        return self.DGP5_HEADERS | {"actauth": self.get_access_token()}

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
        res = self.session.get(url, headers=self.get_headers(), params=params, **kwargs)
        return self.logger(res)

    def post_dgp(self, url: str, json=None, **kwargs) -> requests.Response:
        self.LOGGER.info("json %s", json)
        res = self.session.post(url, headers=self.get_headers(), json=json, **kwargs)
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

    def download(self, sign: str, filelist_url: str, output: Path):
        sign_dict = dict(parse_qsl(sign.replace(";", "&")))
        signed = {
            "Policy": sign_dict["CloudFront-Policy"],
            "Signature": sign_dict["CloudFront-Signature"],
            "Key-Pair-Id": sign_dict["CloudFront-Key-Pair-Id"],
        }
        url = self.API_DGP.format(filelist_url)
        data = self.get_dgp(url).json()

        def download_save(file: dict) -> tuple[int, dict]:
            path = output.joinpath(file["local_path"][1:])
            content = self.get(data["data"]["domain"] + "/" + file["path"], params=signed).content
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            return file["size"], file

        def check_sum(file: dict) -> tuple[bool, dict]:
            path = output.joinpath(file["local_path"][1:])
            if not file["check_hash_flg"]:
                return True, file
            if file["force_delete_flg"]:
                path.unlink()
                return True, file
            if not path.exists():
                return False, file
            try:
                with open(path, "rb") as f:
                    content = f.read()
                return file["hash"] == hashlib.md5(content).hexdigest(), file
            except Exception:
                return False, file

        check_count = 0
        check_failed_list: list[dict] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            tasks = [pool.submit(lambda x: check_sum(x), x) for x in data["data"]["file_list"]]
            for task in concurrent.futures.as_completed(tasks):
                res, file = task.result()
                check_count += 1
                if not res:
                    check_failed_list.append(file)
                yield check_count / len(data["data"]["file_list"]), file

        yield 0, None

        check_failed_list = sorted(check_failed_list, key=lambda x: x["size"], reverse=True)
        download_max_size = sum([x["size"] for x in check_failed_list])
        download_size: int = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            tasks = [pool.submit(lambda x: download_save(x), x) for x in check_failed_list]
            for task in concurrent.futures.as_completed(tasks):
                size, file = task.result()
                download_size += size
                yield download_size / download_max_size, file

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
    def read_dgp() -> "DgpSessionV2":
        session = DgpSessionV2()
        session.read()
        return session

    @staticmethod
    def read_cookies(path: Path) -> "DgpSessionV2":
        session = DgpSessionV2()
        session.read_bytes(str(path))
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
