import os
import json
import pandas as pd

DGP5_PATH = os.environ["APPDATA"] + "\\dmmgameplayer5\\"

with open(DGP5_PATH + "dmmgame.cnf", "r") as f:
    config = f.read()
dpg5_config = json.loads(config)

table = [
    (contents["productId"], contents["detail"]["path"], contents["detail"]["version"])
    for contents in dpg5_config["contents"]
]

df = pd.DataFrame(table, columns=["productId", "path", "version"])
pd.set_option("display.unicode.east_asian_width", True)

print(df)
print("終了するには何かキーを押してください")
input()
