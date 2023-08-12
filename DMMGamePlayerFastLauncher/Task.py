# flake8: noqa
# type: ignore

import ctypes
import os
import signal

import psutil

for p in psutil.process_iter(attrs=("name", "pid", "cmdline")):
    if p.info["name"] != "DMMGamePlayerFastLauncher.exe":
        continue

    cmdline = p.info["cmdline"]
    if "--non-bypass-uac" not in cmdline:
        cmdline.append("--non-bypass-uac")
        cmdline = [f'"{cmd}"' for cmd in cmdline]
        os.kill(p.info["pid"], signal.SIGTERM)
        print("killed " + " ".join(cmdline))
        ctypes.windll.shell32.ShellExecuteW(None, "runas", cmdline[0], " ".join(cmdline[1:]), None, 1)
        break
else:
    print("Error")
