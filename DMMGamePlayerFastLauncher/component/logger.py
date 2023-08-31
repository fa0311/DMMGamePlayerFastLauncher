from logging import Handler, LogRecord

import customtkinter as ctk
from customtkinter import CTkTextbox, CTkToplevel


class StyleScheme:
    # BOLD = ("BOLD", "1", {"font": ("", 12, "bold")})
    GREY = ("GREY", "30", {"foreground": "#808080"})
    RED = ("RED", "31", {"foreground": "#FF0000"})
    GREEN = ("GREEN", "32", {"foreground": "#00FF00"})
    YELLOW = ("YELLOW", "33", {"foreground": "#FFFF00"})
    BLUE = ("BLUE", "34", {"foreground": "#0000FF"})
    PURPLE = ("PURPLE", "35", {"foreground": "#FF00FF"})
    SKYBLUE = ("SKYBLUE", "36", {"foreground": "#00FFFF"})
    BGRED = ("BGRED", "41", {"background": "#FF0000"})
    BGGREEN = ("BGGREEN", "42", {"background": "#00FF00"})
    BGYELLOW = ("BGYELLOW", "43", {"background": "#FFFF00"})
    BGBLUE = ("BGBLUE", "44", {"background": "#0000FF"})
    BGPURPLE = ("BGPURPLE", "45", {"background": "#FF00FF"})
    BGSKYBLUE = ("BGSKYBLUE", "46", {"background": "#00FFFF"})
    BGWHITE = ("BGWHITE", "47", {"background": "#FFFFFF"})

    @staticmethod
    def check():
        for i in range(1, 150):
            print(f"\033[{i}m[{i}]\033[0m", end="")

    @classmethod
    def to_dict(cls):
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}


class TkinkerHandler(Handler):
    box: CTkTextbox

    def __init__(self, master):
        super().__init__()
        self.box = CTkTextbox(master, height=30)

    def create(self):
        self.box.pack(fill=ctk.BOTH, padx=10, pady=(0, 10), expand=True)
        for style in StyleScheme.to_dict().values():
            self.box.tag_config(style[0], **style[2])

        return self

    def emit(self, record: LogRecord) -> None:
        formated = self.format(record)
        tag = []
        for text in formated.split("\033["):
            codes = text.split("m", 1)[0].split(";")

            for code in codes:
                if code == "0":
                    tag = []
                else:
                    for style in StyleScheme.to_dict().values():
                        if code == style[1]:
                            tag.append(style[0])
            self.box.insert(ctk.END, text.split("m", 1)[-1], tag)
        self.box.insert(ctk.END, "\n", tag)

        self.box.see(ctk.END)
        self.flush()


class TkinkerLogger(CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Log")
        self.geometry("600x300")
