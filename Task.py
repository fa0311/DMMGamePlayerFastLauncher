import psutil
import os
import signal
import ctypes


for p in psutil.process_iter(attrs=("name", "pid", "cmdline")):
    if p.info["name"] != "DMMGamePlayerFastLauncher.exe":
        continue
    cmdline = p.info["cmdline"]
    if "--bypass-uac" in cmdline:
        cmdline.remove("--bypass-uac")
        os.kill(p.info["pid"], signal.SIGTERM)
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", cmdline[0], " ".join(cmdline[1:]), None, 1
        )
        break
