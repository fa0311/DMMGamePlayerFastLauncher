import psutil
import subprocess
import os
import signal


for p in psutil.process_iter(attrs=("name", "pid", "cmdline")):
    if p.info["name"] != "DMMGamePlayerFastLauncher.exe":
        continue
    if "--bypass-uac" in p.info["cmdline"]:
        p.info["cmdline"].remove("--bypass-uac")
        os.kill(p.info["pid"], signal.SIGTERM)
        subprocess.Popen(p.info["cmdline"], shell=True)
        break
