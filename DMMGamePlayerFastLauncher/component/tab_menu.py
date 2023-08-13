from tkinter import Misc

import customtkinter as ctk
from customtkinter import CTkButton, CTkFrame
from customtkinter import ThemeManager as CTkm
from utils.utils import children_destroy


class TabMenuComponent:
    tab_master: CTkFrame
    body_master: CTkFrame
    row: int = 0

    def __init__(self, master: Misc) -> None:
        self.tab_master = CTkFrame(master)
        self.body_master = CTkFrame(master)

        self.tab_master.pack(side=ctk.LEFT, fill=ctk.Y, padx=5, pady=5)
        self.body_master.pack(side=ctk.LEFT, expand=True, fill=ctk.BOTH, padx=0, pady=5)

    def add(self, text: str, callback):
        row = self.row

        fg_color = CTkm.theme["CTkFrame"]["fg_color"]
        text_color = CTkm.theme["MenuComponent"]["text_color"]
        command = lambda: self.callback_wrapper(callback, row=row)  # noqa E731

        btn = CTkButton(self.tab_master, text=text, fg_color=fg_color, text_color=text_color, command=command)
        btn.pack(pady=2, padx=4)
        if self.row == 0:
            self.callback_wrapper(callback, row=self.row)

        self.row += 1

    def callback_wrapper(self, callback, row):
        children_destroy(self.body_master)
        for key, child in enumerate(self.tab_master.winfo_children()):
            if key == row:
                child.configure(
                    fg_color=CTkm.theme["CTkButton"]["fg_color"],
                    hover_color=CTkm.theme["CTkButton"]["fg_color"],
                    text_color=CTkm.theme["CTkButton"]["text_color"],
                )
            else:
                child.configure(
                    fg_color=CTkm.theme["CTkFrame"]["fg_color"],
                    hover_color=CTkm.theme["CTkButton"]["hover_color"],
                    text_color=CTkm.theme["MenuComponent"]["text_color"],
                )
            child.update()

        callback(self.body_master)

    def is_dark(self):
        return ctk.get_appearance_mode() == "Dark"
