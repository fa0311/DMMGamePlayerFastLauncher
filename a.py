from pathlib import Path

from DMMGamePlayerFastLauncher.lib.DGPSessionV2 import DgpSessionV2

session = DgpSessionV2.read_cookies(Path("data/account/a.bytes"))


json = {}
res = session.post_dgp("https://apidgp-gameplayer.games.dmm.com/v5/hardwarelist", json=json, verify=False)
print(res.json())


# json = {
#     "mac_address": "00:00:00:00:00:00",
#     "hdd_serial": "00000000",
#     "motherboard": "00000000",
#     "user_os": "win",
# }
# res = session.post_dgp("https://apidgp-gameplayer.games.dmm.com/v5/hardwarecode", json=json, verify=False)
# print(res.json())

# json = {
#     "mac_address": "00:00:00:00:00:00",
#     "hdd_serial": "00000000",
#     "motherboard": "00000000",
#     "user_os": "win",
#     "hardware_name": input("hardware_name: "),
#     "auth_code": input("auth_code: "),
# }
# res = session.post_dgp("https://apidgp-gameplayer.games.dmm.com/v5/hardwareconf", json=json, verify=False)
# print(res.json())

json = {
    "mac_address": "00:00:00:00:00:00",
    "hdd_serial": "00000000",
    "motherboard": "00000000",
    "user_os": "win",
    "product_id": "priconner",
    "game_type": "GCL",
    "game_os": "win",
    "launch_type": "LIB",
}

res = session.post_dgp("https://apidgp-gameplayer.games.dmm.com/v5/launch/pkg", json=json, verify=False)
print(res.json())
