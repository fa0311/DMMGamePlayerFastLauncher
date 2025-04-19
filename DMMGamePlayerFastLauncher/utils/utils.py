import locale
import time
import urllib.parse
from pathlib import Path
from tkinter import Misc
from typing import Optional, Tuple, TypeVar

import i18n
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from static.config import AssetsPathConfig

T = TypeVar("T")


def isinstance_filter(obj, cls: type[T]) -> list[T]:
    return list(filter(lambda x: isinstance(x, cls), obj))


def get_isinstance(obj, cls: type[T]) -> Optional[T]:
    ins = isinstance_filter(obj, cls)
    if len(ins) > 0:
        return ins[0]
    return None


def children_destroy(master: Misc):
    for child in master.winfo_children():
        child.destroy()


def file_create(path: Path, name: str):
    if path.exists():
        raise FileExistsError(i18n.t("app.utils.file_exists", name=name))
    else:
        path.touch()


def get_supported_lang() -> list[tuple[str, str]]:
    return [(y, i18n.t("app.language", locale=y)) for y in [x.suffixes[0][1:] for x in AssetsPathConfig.I18N.iterdir()]]


def get_default_locale() -> Tuple[str, str]:
    lang, encoding = locale.getdefaultlocale()
    if lang not in [x[0] for x in get_supported_lang()]:
        lang = "en"
    if encoding is None:
        encoding = "utf-8"
    return lang, encoding


def get_driver(browser: str, path: Optional[Path]) -> webdriver.Chrome | webdriver.Edge | webdriver.Firefox:
    absolute_path = path.absolute() if path is not None else None
    if browser == "Chrome":
        options = ChromeOptions()
        if absolute_path is not None:
            options.add_argument(f"--user-data-dir={absolute_path}")
        return webdriver.Chrome(options=options)
    elif browser == "Edge":
        options = EdgeOptions()
        if absolute_path is not None:
            options.add_argument(f"--user-data-dir={absolute_path}")
        return webdriver.Edge(options=options)
    elif browser == "Firefox":
        options = FirefoxOptions()
        if absolute_path is not None:
            options.add_argument("-profile")
            options.add_argument(str(absolute_path))
        return webdriver.Firefox(options=options)
    else:
        raise Exception(i18n.t("app.account.browser_not_selected"))


def login_driver(url: str, driver: webdriver.Chrome | webdriver.Edge | webdriver.Firefox):
    driver.get(url)
    parsed_url = urllib.parse.urlparse(driver.current_url)
    while not (parsed_url.netloc == "webdgp-gameplayer.games.dmm.com" and parsed_url.path == "/login/success"):
        time.sleep(0.2)
        parsed_url = urllib.parse.urlparse(driver.current_url)

    code = urllib.parse.parse_qs(parsed_url.query)["code"][0]
    return code
