from ast import List
import os
from tkinter import Entry, StringVar, filedialog
import i18n
from pathlib import Path

import customtkinter as ctk
from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    CTkScrollbar,
    CTkScrollableFrame,
    CTkBaseClass,
)

from customtkinter import ThemeManager as CTKM


class HelpTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])

    def create(self):
        text = CTkLabel(self, text="help")
        text.pack()
        return self
