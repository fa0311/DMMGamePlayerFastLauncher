import webbrowser

import customtkinter as ctk
import i18n
from customtkinter import CTkBaseClass, CTkButton, CTkScrollableFrame, CTkTextbox
from static.config import PathConfig, UrlConfig


class HelpTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color="transparent")

    def create(self):
        CTkButton(self, text=i18n.t("app.help.coop_in_develop"), command=self.contribution_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text=i18n.t("app.help.donations_to_developer"), command=self.donation_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text=i18n.t("app.help.bug_report"), command=self.report_callback).pack(fill=ctk.X, pady=10)

        with open(PathConfig.LICENSE, "r", encoding="utf-8") as f:
            license = f.read()

        box = CTkTextbox(self, width=590, height=400)
        box.pack(padx=10, pady=(0, 10))
        box.insert("0.0", license)

        return self

    def contribution_callback(self):
        webbrowser.open(UrlConfig.CONTRIBUTION)

    def donation_callback(self):
        webbrowser.open(UrlConfig.DONATE)

    def report_callback(self):
        webbrowser.open(UrlConfig.ISSUE)
