import ctypes
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import psutil
import win32security
from static.config import AssetsPathConfig, DataPathConfig, SchtasksConfig
from static.env import Env


class ProcessManager:
    @staticmethod
    def admin_run(args: list[str], cwd: Optional[str] = None) -> int:
        file = args.pop(0)
        logging.info({"cwd": cwd, "args": args, "file": file})
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", str(file), " ".join([f"{arg}" for arg in args]), cwd, 1)

    @staticmethod
    def admin_check() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    @staticmethod
    def run(args: list[str], cwd: Optional[str] = None) -> subprocess.Popen:
        logging.info({"cwd": cwd, "args": args})
        return subprocess.Popen(args, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def run_ps(args: str) -> int:
        logging.info(args)
        args = args.replace('"', '\\"').replace("\n", "").replace("\r", "")
        text = f'powershell -Command "{args}"'
        return subprocess.call(text, shell=True)

    @staticmethod
    def search_process(name: str) -> psutil.Process:
        for process in psutil.process_iter():
            if process.name() == name:
                return process
        raise Exception(f"Process not found: {name}")


class ProcessIdManager:
    process: list[tuple[int, Optional[str]]]

    def __init__(self, _process: Optional[list[tuple[int, Optional[str]]]] = None) -> None:
        def wrapper(x: psutil.Process) -> Optional[str]:
            try:
                return x.exe()
            except Exception:
                return None

        if _process is None:
            self.process = [(x.pid, wrapper(x)) for x in psutil.process_iter()]
        else:
            self.process = _process

    def __sub__(self, other: "ProcessIdManager") -> "ProcessIdManager":
        process = [x for x in self.process if x not in other.process]
        return ProcessIdManager(process)

    def __add__(self, other: "ProcessIdManager") -> "ProcessIdManager":
        process = list(set(self.process + other.process))
        return ProcessIdManager(process)

    def __repr__(self) -> str:
        return "\n".join([f"{x[0]}: {x[1]}" for x in self.process]) + "\n"

    def new_process(self) -> "ProcessIdManager":
        return ProcessIdManager() - self

    def search(self, name: str) -> int:
        process = [x[0] for x in self.process if x[1] == name]
        if len(process) != 1:
            raise Exception(f"Process not found: {name}")
        return process[0]

    def search_or_none(self, name: str) -> Optional[int]:
        process = [x[0] for x in self.process if x[1] == name]
        if len(process) != 1:
            return None
        return process[0]


def get_sid() -> str:
    username = os.getlogin()
    sid, domain, type = win32security.LookupAccountName("", username)
    sidstr = win32security.ConvertSidToStringSid(sid)
    return sidstr


class Schtasks:
    file: str
    name: str

    def __init__(self, args: str) -> None:
        self.file = SchtasksConfig.FILE.format(os.getlogin(), args)
        self.name = SchtasksConfig.NAME.format(self.file)
        self.args = args

    def check(self) -> bool:
        xml_path = DataPathConfig.SCHTASKS.joinpath(self.file).with_suffix(".xml")
        return not xml_path.exists()

    def set(self) -> None:
        with open(AssetsPathConfig.SCHTASKS, "r", encoding="utf-8") as f:
            template = f.read()

        if Env.DEVELOP:
            command = Path(sys.executable)
            args = [str(Path(sys.argv[0]).absolute()), self.args, "--type", "game"]
        else:
            command = Path(sys.argv[0])
            args = [self.args, "--type", "game"]

        template = template.replace(r"{{UID}}", self.file)
        template = template.replace(r"{{SID}}", get_sid())
        template = template.replace(r"{{COMMAND}}", str(command.absolute()))
        template = template.replace(r"{{ARGUMENTS}}", " ".join(f"{x}" for x in args))
        template = template.replace(r"{{WORKING_DIRECTORY}}", os.getcwd())

        xml_path = DataPathConfig.SCHTASKS.joinpath(self.file).with_suffix(".xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(template)
        create_args = [Env.SCHTASKS, "/create", "/xml", str(xml_path.absolute()), "/tn", self.name]

        ProcessManager.admin_run(create_args)

    def delete(self) -> None:
        delete_args = [Env.SCHTASKS, "/delete", "/tn", self.name, "/f"]
        ProcessManager.admin_run(delete_args)


class Shortcut:
    def create(self, sorce: Path, target: Optional[Path] = None, args: Optional[list[str]] = None, icon: Optional[Path] = None):
        with open(AssetsPathConfig.SHORTCUT, "r", encoding="utf-8") as f:
            template = f.read()
        if icon is None:
            icon = Path(sys.argv[0])
        if args is None:
            args = []

        if target is None:
            if Env.DEVELOP:
                target = Path(sys.executable)
                args.insert(0, str(Path(sys.argv[0]).absolute()))
            else:
                target = Path(sys.argv[0])

        template = template.replace(r"{{SORCE}}", str(sorce.absolute()))
        template = template.replace(r"{{TARGET}}", str(target))
        template = template.replace(r"{{WORKING_DIRECTORY}}", os.getcwd())
        template = template.replace(r"{{ICON_LOCATION}}", str(icon.absolute()))
        template = template.replace(r"{{ARGUMENTS}}", " ".join(f"{x}" for x in args))

        ProcessManager.run_ps(template)
