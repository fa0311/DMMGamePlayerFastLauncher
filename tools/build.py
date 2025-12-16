import glob
from pathlib import Path

output = ""
width = 62


delimiter = "\n\n" + ("=" * width) + "\n\n"

Path("assets/license").mkdir(parents=True, exist_ok=True)

for file in ("./../DMMGamePlayerFastLauncher/LICENSE", *glob.glob(".venv/**/*[Ll][Ii][Cc][Ee][Nn][SsCc][Ee]*", recursive=True)):
    path = Path(file)
    if path.is_file():
        with open(file, "r", encoding="utf-8") as f:
            output += delimiter + path.parent.name.center(width * 2 - 1) + delimiter + f.read()


with open("assets/license/LICENSE", "w", encoding="utf-8") as f:
    f.write(output)
