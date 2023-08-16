import ctypes
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import win32security
from static.config import AssetsPathConfig, DataPathConfig, SchtasksConfig


class ProcessManager:
    @staticmethod
    def admin_run(args: list[str]) -> int:
        args = [f'"{arg}"' for arg in args]
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", args[0], " ".join(args[1:]), None, 1)

    @staticmethod
    def run(args: list[str]) -> subprocess.Popen[bytes]:
        return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def run_ps(args: str) -> int:
        args = args.replace('"', '\\"').replace("\n", "").replace("\r", "")
        return subprocess.call(f'powershell -Command "{args}"', shell=True)


def get_sid() -> str:
    desc = win32security.GetFileSecurity(".", win32security.OWNER_SECURITY_INFORMATION)
    sid = desc.GetSecurityDescriptorOwner()
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
        with open(AssetsPathConfig.SCHTASKS, "r") as f:
            template = f.read()

        if os.environ.get("ENV") == "DEVELOP":
            command = Path(sys.executable)
            args = [str(Path(sys.argv[0]).absolute()), self.args]
        else:
            command = Path(sys.argv[0])
            args = [self.args]

        template = template.replace(r"{{UID}}", self.file)
        template = template.replace(r"{{SID}}", get_sid())
        template = template.replace(r"{{COMMAND}}", str(command.absolute()))
        template = template.replace(r"{{ARGUMENTS}}", " ".join(f"{x}" for x in args))
        template = template.replace(r"{{WORKING_DIRECTORY}}", os.getcwd())

        xml_path = DataPathConfig.SCHTASKS.joinpath(self.file).with_suffix(".xml")
        with open(xml_path, "w") as f:
            f.write(template)
        create_args = [SchtasksConfig.PATH, "/create", "/xml", str(xml_path.absolute()), "/tn", self.name]

        ProcessManager.admin_run(create_args)

    def delete(self) -> None:
        delete_args = [SchtasksConfig.PATH, "/delete", "/tn", self.name, "/f"]
        ProcessManager.admin_run(delete_args)


class Shortcut:
    def create(self, sorce: Path, args: list[str], icon: Optional[Path] = None):
        with open(AssetsPathConfig.SHORTCUT, "r") as f:
            template = f.read()
        if icon is None:
            icon = Path(__file__)

        template = template.replace(r"{{SORCE}}", str(sorce.absolute()))
        template = template.replace(r"{{TARGET}}", SchtasksConfig.PATH)
        template = template.replace(r"{{WORKING_DIRECTORY}}", os.getcwd())
        template = template.replace(r"{{ICON_LOCATION}}", str(icon.absolute()))
        template = template.replace(r"{{ARGUMENTS}}", " ".join(f"{x}" for x in args))

        ProcessManager.run_ps(template)
