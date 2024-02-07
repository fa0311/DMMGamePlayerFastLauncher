import glob
import re
from typing import Any

import yaml

with open("assets/i18n/app.ja.yml", "r", encoding="utf-8") as f:
    yaml_load = yaml.safe_load(f)


def in_py(key):
    for file in glob.glob("**/*.py", root_dir="DMMGamePlayerFastLauncher", recursive=True):
        with open(f"DMMGamePlayerFastLauncher/{file}", "r", encoding="utf-8") as f:
            if f'i18n.t("{key}"' in f.read():
                return False
    return True


def i18n_flatten(data: dict[str, Any], parent: str) -> list[str]:
    res = []
    for k, v in data.items():
        if isinstance(v, dict):
            res.extend(i18n_flatten(v, f"{parent}.{k}"))
        elif isinstance(v, str):
            res.append(f"{parent}.{k}")
    return res


def get_py():
    res = []
    for file in glob.glob("**/*.py", root_dir="DMMGamePlayerFastLauncher", recursive=True):
        with open(f"DMMGamePlayerFastLauncher/{file}", "r", encoding="utf-8") as f:
            match = re.findall(r'i18n.t\("([a-z\.\_]*?)"', f.read())
            res.extend(match)
    return res


i18n = i18n_flatten(yaml_load["ja"], "app")
for key in i18n:
    if in_py(key):
        print(f"not found: {key}")

print("===")
for key in get_py():
    if key not in i18n:
        print(f"not used: {key}")
