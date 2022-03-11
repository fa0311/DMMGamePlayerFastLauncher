import subprocess
import time
import requests
import DMMLogAnalysis
import argparse
import tempfile

requests.packages.urllib3.disable_warnings()


argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)

argpar.add_argument("product_id")
argpar.add_argument("game_path")
arg = argpar.parse_args()

argpar.add_argument("-dgp-path", "--dmmgameplayer-path", default="C:/Program Files/DMMGamePlayer/DMMGamePlayer.exe".format(product_id=arg.product_id))
argpar.add_argument("--game-uri", default="dmmgameplayer://{product_id}/cl/general/{product_id}".format(product_id=arg.product_id))
argpar.add_argument("--temp-path", default="{tempdir}/dmm.log".format(product_id=arg.product_id, tempdir=tempfile.gettempdir().replace("\\","/")))
argpar.add_argument("--kill", default=True)
arg = argpar.parse_args()



process = subprocess.Popen([arg.dmmgameplayer_path, arg.game_uri, ">", arg.temp_path], shell=True)

log = DMMLogAnalysis.DMMLogAnalysis()
while not log.check(arg.temp_path):
    time.sleep(0.2)

if arg.kill:
    process.kill()

session = requests.session()
for cookie in log.session:
    session.cookies.set_cookie(
        requests.cookies.create_cookie(name=cookie["name"],value=cookie["value"],domain=cookie["domain"],path=cookie["path"],secure=cookie["secure"])
    )

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
    "mac_address": "00:11:22:33:44:55",
    "hdd_serial": "0000000011111111222222223333333344444444555555556666666677777777",
    "motherboard": "0000000011111111222222223333333344444444555555556666666677777777",
    "user_os": "win"
}

response = session.post("https://apidgp-gameplayer.games.dmm.com/v5/launch/cl", headers=headers, json=params,verify=False)
dmm_args = response.json()["data"]["execute_args"].split(" ")

subprocess.Popen([arg.game_path, dmm_args[0], dmm_args[1]], shell=True)