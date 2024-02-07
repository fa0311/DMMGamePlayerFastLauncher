import locale
from pathlib import Path
from tkinter import Misc
from typing import Optional, Tuple, TypeVar

import i18n
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
