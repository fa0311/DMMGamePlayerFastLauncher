import os
import json
import requests
import win32crypt
import random
import hashlib
import sqlite3
import base64
from Crypto.Cipher import AES

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
        aes_key = self.get_aes_key()
        for cookie_row in self.db.cursor().execute("select * from cookies"):
            value = self.session.cookies.get(cookie_row[3])
            v10, nonce, _, _ = self.split_encrypted_data(cookie_row[5])
            cipher = AES.new(aes_key, AES.MODE_GCM, nonce)
            decrypt_data, mac = cipher.encrypt_and_digest(value.encode())
            data = self.join_encrypted_data(v10, nonce, decrypt_data, mac)
            self.db.execute(
                "update cookies set encrypted_value = ? where name = ?",
                (memoryview(data), cookie_row[3]),
            )
        self.db.commit()

    def read(self):
        aes_key = self.get_aes_key()
        for cookie_row in self.db.cursor().execute("select * from cookies"):
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

    def get_aes_key(self):
        with open(self.DGP5_PATH + "\\Local State", "r") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(
            local_state["os_crypt"]["encrypted_key"].encode()
        )[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key

    def split_encrypted_data(self, encrypted_data: bytes) -> bytes:
        return (
            encrypted_data[0:3],
            encrypted_data[3:15],
            encrypted_data[15:-16],
            encrypted_data[-16:],
        )

    def join_encrypted_data(
        self, v10: bytes, nonce: bytes, data: bytes, mac: bytes
    ) -> bytes:
        return v10 + nonce + data + mac

    def close(self):
        self.db.close()