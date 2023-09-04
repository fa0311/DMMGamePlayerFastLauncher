import webbrowser
from tkinter import Misc

import i18n
from customtkinter import CTkFont, CTkFrame, CTkImage, CTkLabel
from lib.toast import ToastController
from PIL import Image
from static.config import AssetsPathConfig, UrlConfig
from static.env import Env


class HomeTab(CTkFrame):
    toast: ToastController
    update_flag: bool = False

    def __init__(self, master: Misc):
        super().__init__(master, fg_color="transparent")
        self.toast = ToastController(self)

    def create(self):
        frame = CTkFrame(self, fg_color="transparent")
        frame.pack(anchor="center", expand=1)

        image = CTkImage(light_image=Image.open(AssetsPathConfig.ICONS.joinpath("DMMGamePlayerFastLauncher.png")), size=(240, 240))
        CTkLabel(frame, image=image, text="").pack()
        CTkLabel(frame, text=i18n.t("app.title"), font=CTkFont(size=28)).pack(pady=20)

        CTkLabel(frame, text=Env.VERSION, font=CTkFont(size=18)).pack()

        if Env.RELEASE_VERSION != Env.VERSION and HomeTab.update_flag is False:
            HomeTab.update_flag = True
            self.toast.command_info(i18n.t("app.home.new_version"), lambda: webbrowser.open(UrlConfig.RELEASE))

        return self
