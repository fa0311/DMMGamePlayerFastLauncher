from __future__ import annotations

import logging
import time
import urllib.parse
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from lib.DGPSessionBase import DgpSessionBase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class Browser(str, Enum):
    chrome = "chrome"
    firefox = "firefox"


class GameType(str, Enum):
    GCL = "GCL"
    ACL = "ACL"
    AMAIN = "AMAIN"
    GMAIN = "GMAIN"


def resolve(
    product_id: str = typer.Argument(..., help="DMM product ID."),
    game_type: GameType = typer.Option(GameType.GCL, "--game-type", help="DMM game type."),
    game_dir: Optional[Path] = typer.Option(None, "--game-dir", help="Game install directory."),
    browser: Browser = typer.Option(Browser.chrome, "--browser", help="Browser used for login."),
    browser_arg: Optional[list[str]] = typer.Option(None, "--browser-arg", help="Extra browser argument. Can be repeated."),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL for DMM API requests."),
    log_level: str = typer.Option("WARNING", "--log-level", help="Python logging level."),
):
    """Resolve and print only the game executable arguments."""
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.WARNING), format="[%(levelname)s] %(message)s")

    if proxy:
        DgpSessionBase.PROXY["http"] = proxy
        DgpSessionBase.PROXY["https"] = proxy

    session = DgpSessionBase()
    res = session.post_dgp(session.LOGIN_URL, json={"prompt": ""}, verify=False).json()
    if res["result_code"] != 100:
        raise RuntimeError(res["error"])

    if browser == Browser.chrome:
        options = ChromeOptions()
        for arg in browser_arg or []:
            options.add_argument(arg)
        driver = webdriver.Chrome(options=options)
    else:
        options = FirefoxOptions()
        for arg in browser_arg or []:
            options.add_argument(arg)
        driver = webdriver.Firefox(options=options)

    try:
        driver.get(res["data"]["url"])
        parsed_url = urllib.parse.urlparse(driver.current_url)
        while not (parsed_url.netloc == "webdgp-gameplayer.games.dmm.com" and parsed_url.path == "/login/success"):
            time.sleep(0.2)
            parsed_url = urllib.parse.urlparse(driver.current_url)
        code = urllib.parse.parse_qs(parsed_url.query)["code"][0]
    finally:
        driver.quit()

    res = session.post_dgp(session.ACCESS_TOKEN, json={"code": code}, verify=False).json()
    if res["result_code"] != 100:
        raise RuntimeError(res["error"])
    session.actauth = {"accessToken": res["data"]["access_token"]}

    response = session.launch(product_id, game_type.value).json()
    if response["result_code"] != 100:
        raise RuntimeError(response["error"])

    if game_dir is not None:
        game_dir.mkdir(parents=True, exist_ok=True)
        for _ in session.download(response["data"]["sign"], response["data"]["file_list_url"], game_dir):
            pass

    typer.echo(response["data"].get("execute_args"))


def main():
    typer.run(resolve)


if __name__ == "__main__":
    main()
