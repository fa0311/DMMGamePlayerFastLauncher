from customtkinter import CTkBaseClass, CTkLabel, CTkScrollableFrame
from customtkinter import ThemeManager as CTkm


class HelpTab(CTkScrollableFrame):
    def __init__(self, master: CTkBaseClass):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])

    def create(self):
        text = CTkLabel(self, text="help")
        text.pack()
        return self
