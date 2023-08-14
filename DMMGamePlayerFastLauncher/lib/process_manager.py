import ctypes
import os
import subprocess
from pathlib import Path

import win32security
from static.config import PathConfig, SchtasksConfig


class ProcessManager:
    @staticmethod
    def admin_run(args: list[str]) -> int:
        args = [f'"{arg}"' for arg in args]
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", args[0], " ".join(args[1:]), None, 1)

    @staticmethod
    def run(args: list[str]) -> subprocess.Popen[bytes]:
        return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_sid() -> str:
    desc = win32security.GetFileSecurity(".", win32security.OWNER_SECURITY_INFORMATION)
    sid = desc.GetSecurityDescriptorOwner()
    sidstr = win32security.ConvertSidToStringSid(sid)
    return sidstr


class Schtasks:
    file: str
    name: str

    def __init__(self) -> None:
        self.file = SchtasksConfig.FILE.format(os.getlogin())
        self.name = SchtasksConfig.NAME.format(self.file)

    def check(self) -> bool:
        run_args = [SchtasksConfig.PATH, "/run", "/tn", self.name]
        return ProcessManager.run(run_args).wait() == 0

    def set(self) -> None:
        with open(PathConfig.SCHTASKS_TEMPLATE, "r") as f:
            template = f.read()

        template = template.replace(r"{{UID}}", self.file)
        template = template.replace(r"{{SID}}", get_sid())
        template = template.replace(r"{{COMMAND}}", str(Path(__file__).absolute()))
        template = template.replace(r"{{WORKING_DIRECTORY}}", os.getcwd())

        xml_path = PathConfig.SCHTASKS.joinpath(self.file).with_suffix(".xml")
        with open(xml_path, "w") as f:
            f.write(template)
        create_args = [SchtasksConfig.PATH, "/create", "/xml", str(xml_path.absolute()), "/tn", self.name]

        ProcessManager.admin_run(create_args)

    def delete(self) -> None:
        delete_args = [SchtasksConfig.PATH, "/delete", "/tn", self.name, "/f"]
        ProcessManager.admin_run(delete_args)
