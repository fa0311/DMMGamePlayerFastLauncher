import os
import json
import pandas as pd
from lib.DGPSession import *

session = DgpSession()

table = [
    (contents["productId"], contents["detail"]["path"], contents["detail"]["version"])
    for contents in session.get_config()["contents"]
]

df = pd.DataFrame(table, columns=["productId", "path", "version"])
pd.set_option("display.unicode.east_asian_width", True)

print(df)
print("Please press any key to exit")
input()
