import customtkinter as ctk
from customtkinter import CTkTextbox, CTkToplevel
from tkinter_colored_logging_handlers.main import ColorSchemeLight, StyleSchemeBase


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

    def create(self):
        self.box.pack(fill=ctk.BOTH, padx=10, pady=(0, 10), expand=True)
        return self
