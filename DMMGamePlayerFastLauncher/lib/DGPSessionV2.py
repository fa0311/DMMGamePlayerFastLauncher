# flake8: noqa

import base64
import hashlib
import json
import logging
import os
import random
import re
import sqlite3
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import requests.cookies
import urllib3
import win32crypt
from Crypto.Cipher import AES

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


class DgpSessionV2:
    DGP5_PATH: Path
    HEADERS: dict[str, str]
    PROXY: Optional[dict[str, str]]
    DGP5_HEADERS: dict[str, str]
    DGP5_LAUNCH_PARAMS: dict[str, str]
    DATA_DESCR: str
    LAUNCH_URL: str
    db: sqlite3.Connection
    session: requests.Session
    cookies: requests.cookies.RequestsCookieJar
    cookies_kwargs = {
        "domain": ".dmm.com",
        "path": "/",
    }
    DGP5_PATH = Path(os.environ["APPDATA"]).joinpath("dmmgameplayer5")

    PROXY: Optional[dict[str, str]] = None
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
        "game_type": "GCL",
        "game_os": "win",
        "launch_type": "LIB",
        "mac_address": DgpSessionUtils.gen_rand_address(),
        "hdd_serial": DgpSessionUtils.gen_rand_hex(),
        "motherboard": DgpSessionUtils.gen_rand_hex(),
        "user_os": "win",
    }
    DATA_DESCR = "DMMGamePlayerFastLauncher"
    LAUNCH_URL = "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl"

    def __init__(self, https_proxy_uri: Optional[str] = None):
        self.session = requests.session()
        self.cookies = self.session.cookies

        if https_proxy_uri:
            self.PROXY = None if https_proxy_uri is None else {"https": https_proxy_uri}

    def __enter__(self):
        self.db = sqlite3.connect(self.DGP5_PATH.joinpath("Network", "Cookies"))
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
            except:
                pass
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
            except:
                pass

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

    def get(self, url: str) -> requests.Response:
        return self.session.get(url, headers=self.HEADERS, proxies=self.PROXY)

    def post(self, url: str) -> requests.Response:
        return self.session.post(url, headers=self.HEADERS, proxies=self.PROXY)

    def lunch(self, product_id: str) -> requests.Response:
        # {
        #     "result_code": 100,
        #     "data": {
        #         "product_id": "priconner",
        #         "title": "プリンセスコネクト！Re:Dive",
        #         "exec_file_name": "PrincessConnectReDive.exe",
        #         "install_dir": "priconner",
        #         "file_list_url": "/gameplayer/filelist/28102",
        #         "is_administrator": True,
        #         "file_check_type": "FILELIST",
        #         "total_size": 150183072,
        #         "latest_version": "7.6.0",
        #         "execute_args": "/viewer_id=0000 /onetime_token=xxxx",
        #         "conversion_url": None,
        #     },
        #     "error": None,
        # }
        json = {"product_id": product_id}
        json.update(self.DGP5_LAUNCH_PARAMS)
        return self.session.post(
            self.LAUNCH_URL,
            headers=self.DGP5_HEADERS,
            proxies=self.PROXY,
            json=json,
            verify=False,
        )

    def login(self):
        response = self.session.get("https://apidgp-gameplayer.games.dmm.com/v5/loginurl")
        url = response.json()["data"]["url"]
        token = urlparse(url).path.split("path=")[-1]
        try:
            self.session.get(url)
            self.session.get(f"https://accounts.dmm.com/service/login/token/=/path={token}/is_app=false")
        except:
            pass

    def get_config(self):
        with open(self.DGP5_PATH.joinpath("dmmgame.cnf"), "r", encoding="utf-8") as f:
            config = f.read()
        return json.loads(config)

    def get_aes_key(self):
        with open(self.DGP5_PATH.joinpath("Local State"), "r", encoding="utf-8") as f:
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
        session = DgpSessionV2()
        session.read_bytes(str(path))
        session.login()
        session.write_bytes(str(path))
        return session
