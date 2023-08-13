import webbrowser

import customtkinter as ctk
from config import PathConfig, UrlConfig
from customtkinter import CTkBaseClass, CTkButton, CTkScrollableFrame, CTkTextbox
from customtkinter import ThemeManager as CTkm


class HelpTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])

    def create(self):
        CTkButton(self, text="開発に協力", command=self.contribution_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text="開発者に寄付", command=self.donation_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text="バグ報告", command=self.report_callback).pack(fill=ctk.X, pady=10)

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
