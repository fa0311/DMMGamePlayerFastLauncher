import webbrowser

import customtkinter as ctk
from config import UrlConfig
from customtkinter import CTkBaseClass, CTkButton, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm


class HelpTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])

    def create(self):
        CTkButton(self, text="開発に協力", command=self.contribution_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text="開発者に寄付", command=self.donation_callback).pack(fill=ctk.X, pady=10)
        CTkButton(self, text="バグ報告", command=self.report_callback).pack(fill=ctk.X, pady=10)
        return self

    def contribution_callback(self):
        webbrowser.open(UrlConfig.CONTRIBUTION)

    def donation_callback(self):
        webbrowser.open(UrlConfig.DONATE)

    def report_callback(self):
        webbrowser.open(UrlConfig.ISSUE)
