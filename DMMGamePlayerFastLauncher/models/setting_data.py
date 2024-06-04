from dataclasses import dataclass, field
from tkinter import BooleanVar, DoubleVar, StringVar

from component.var import PathVar
from component.variable_base import VariableBase
from lib.DGPSessionV2 import DgpSessionV2
from static.env import Env
from utils.utils import get_default_locale


@dataclass
class SettingData(VariableBase):
    last_version: StringVar = field(default_factory=lambda: StringVar(value="v0.0.0"))  # field(default_factory=lambda: StringVar(value=Env.VERSION))
    dmm_game_player_program_folder: PathVar = field(default_factory=lambda: PathVar(value=Env.DEFAULT_DMM_GAME_PLAYER_PROGURAM_FOLDER))
    dmm_game_player_data_folder: PathVar = field(default_factory=lambda: PathVar(value=Env.DEFAULT_DMM_GAME_PLAYER_DATA_FOLDER))
    proxy_all: StringVar = field(default_factory=StringVar)
    dmm_proxy_all: StringVar = field(default_factory=StringVar)
    lang: StringVar = field(default_factory=lambda: StringVar(value=get_default_locale()[0]))
    theme: StringVar = field(default_factory=lambda: StringVar(value="blue"))
    force_use_os_font: BooleanVar = field(default_factory=lambda: BooleanVar(value=True))
    appearance_mode: StringVar = field(default_factory=lambda: StringVar(value="dark"))
    window_scaling: DoubleVar = field(default_factory=lambda: DoubleVar(value=1.0))
    debug_window: BooleanVar = field(default_factory=lambda: BooleanVar(value=False))
    output_logfile: BooleanVar = field(default_factory=lambda: BooleanVar(value=False))
    mask_token: BooleanVar = field(default_factory=lambda: BooleanVar(value=True))

    def update(self):
        DgpSessionV2.DGP5_PATH = self.dmm_game_player_program_folder.get_path()
        DgpSessionV2.DGP5_DATA_PATH = self.dmm_game_player_data_folder.get_path()


@dataclass
class DeviceData(VariableBase):
    mac_address: StringVar = field(default_factory=lambda: StringVar(value=DgpSessionV2.DGP5_DEVICE_PARAMS["mac_address"]))
    hdd_serial: StringVar = field(default_factory=lambda: StringVar(value=DgpSessionV2.DGP5_DEVICE_PARAMS["hdd_serial"]))
    motherboard: StringVar = field(default_factory=lambda: StringVar(value=DgpSessionV2.DGP5_DEVICE_PARAMS["motherboard"]))
    user_os: StringVar = field(default_factory=lambda: StringVar(value=DgpSessionV2.DGP5_DEVICE_PARAMS["user_os"]))

    def update(self):
        DgpSessionV2.DGP5_DEVICE_PARAMS = {
            "mac_address": self.mac_address.get(),
            "hdd_serial": self.hdd_serial.get(),
            "motherboard": self.motherboard.get(),
            "user_os": self.user_os.get(),
        }


class AppConfig:
    DATA: SettingData
    DEVICE: DeviceData
