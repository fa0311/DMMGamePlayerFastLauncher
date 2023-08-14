from pathlib import Path
from urllib.parse import urlparse

from DMMGamePlayerFastLauncher.lib.DGPSession import DgpSession

session = DgpSession()
session.read()


response = session.get("https://apidgp-gameplayer.games.dmm.com/v5/loginurl")
url = response.json()["data"]["url"]
token = urlparse(url).path.split("path=")[-1]
session.get(url)
login_url = "https://accounts.dmm.com/service/login/token/=/path={token}/is_app=false"
session.get(login_url)


launch_url = "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl"
response = session.lunch(launch_url, "umamusume").json()


print(response)
data = session.get("https://apidgp-gameplayer.games.dmm.com/gameplayer/filelist/28105").json()

domain = data["data"]["domain"]


base_path = Path(__file__).parent.joinpath("uma")
for file in data["data"]["file_list"]:
    data = session.get(domain + "/" + file["path"])

    path = base_path.joinpath(file["local_path"][1:])

    print(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        f.write(data.content)
