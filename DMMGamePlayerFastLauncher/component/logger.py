from logging import Handler, LogRecord

import customtkinter as ctk
from customtkinter import CTkTextbox, CTkToplevel


class TkinkerHandler(Handler):
    box: CTkTextbox

    def __init__(self, master):
        super().__init__()
        self.box = CTkTextbox(master, height=30)

    def create(self):
        self.box.pack(fill=ctk.BOTH, padx=10, pady=(0, 10), expand=True)
        return self

    def emit(self, record: LogRecord) -> None:
        self.box.insert(ctk.END, self.format(record) + "\n")
        self.box.see(ctk.END)
        self.flush()


class TkinkerLogger(CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Log")
        self.geometry("600x300")
