import base64
import json
import logging
import os
from pathlib import Path

import psutil
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from lib.DGPSessionBase import DMMAlreadyRunningException, DgpSessionBase, DgpSessionUtils, text_factory
from win32 import win32crypt


class DgpSessionV2(DgpSessionBase):
    DGP5_PATH = Path(os.environ["PROGRAMFILES"]).joinpath("DMMGamePlayer")
    DGP5_DATA_PATH = Path(os.environ["APPDATA"]).joinpath("dmmgameplayer5")
    LOGGER = logging.getLogger("DgpSessionV2")

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

    def get_aes_key(self):
        with open(self.DGP5_DATA_PATH.joinpath("Local State"), "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"].encode())[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key

    @classmethod
    def read_dgp(cls) -> "DgpSessionV2":
        session = cls()
        session.read()
        return session

    @classmethod
    def read_cookies(cls, path: Path) -> "DgpSessionV2":
        session = cls()
        session.read_bytes(str(path))
        return session

    @classmethod
    def is_running_dmm(cls) -> bool:
        for proc in psutil.process_iter():
            try:
                if Path(proc.exe()) == cls.DGP5_PATH.joinpath("DMMGamePlayer.exe"):
                    return True
            except Exception:
                pass
        return False
