import re

import customtkinter as ctk
from customtkinter import CTkTextbox, CTkToplevel
from tkinter_colored_logging_handlers import ColorSchemeLight, LoggingHandler, StyleSchemeBase


class StyleScheme(StyleSchemeBase, ColorSchemeLight):
    UNDERLINE = ("UNDERLINE", "4", {"underline": True})
    BLINK = ("BLINK", "5", {"overstrike": True})
    REVERSE = ("REVERSE", "7", {"overstrike": True})
    STRIKE = ("STRIKE", "9", {"overstrike": True})


class TkinkerLogger(CTkToplevel):
    box: CTkTextbox

    def __init__(self, master):
        super().__init__(master)
        self.title("Log")
        self.geometry("600x300")
        self.box = CTkTextbox(self, height=30)
        self.protocol("WM_DELETE_WINDOW", lambda: self.withdraw())

    def create(self):
        self.box.pack(fill=ctk.BOTH, padx=10, pady=(0, 10), expand=True)
        return self


class LoggingHandlerMask(LoggingHandler):
    def format(self, record):
        formated = super().format(record)
        formated = re.sub(r"(?<=\=)[0-9a-zA-Z]{32,}", lambda x: f"\033[31m[CENSORED {len(x.group())}]\033[0m", formated)
        return formated
