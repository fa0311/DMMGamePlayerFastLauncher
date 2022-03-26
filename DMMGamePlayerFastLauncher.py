import requests
import argparse
import json
import glob
import random
import hashlib
import sqlite3

requests.packages.urllib3.disable_warnings()

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


headers = {
    "Host": "apidgp-gameplayer.games.dmm.com",
    "Connection": "keep-alive",
    "User-Agent": "DMMGamePlayer5-Win/17.1.2 Electron/17.1.2",
    "Client-App": "DMMGamePlayer5",
    "Client-version": "17.1.2",
}

params = {
    "product_id": "umamusume",
    "game_type": "GCL",
    "game_os": "win",
    "launch_type": "LIB",
    "mac_address": gen_rand_address(),
    "hdd_serial": gen_rand_hex(),
    "motherboard": gen_rand_hex(),
    "user_os": "win",
}

db = sqlite3.connect(
    "C:/Users/yuki/AppData/Roaming/dmmgameplayer5/Network/Cookies"
).cursor()

login_session_id = ""

login_secure_id = db.execute(
    'select * from cookies where name = "login_secure_id"'
).fetchone()[4]


cookies = {"login_session_id": login_session_id, "login_secure_id": login_secure_id}

response = requests.post(
    "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl",
    headers=headers,
    json=params,
    cookies=cookies,
    verify=False,
).json()
print(response)
