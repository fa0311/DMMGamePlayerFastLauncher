from tkinter import Misc
from typing import Callable

import customtkinter as ctk
from customtkinter import CTkButton, CTkFrame
from customtkinter import ThemeManager as CTkm
from utils.utils import children_destroy


class TabMenuComponent:
    tab_master: CTkFrame
    body_master: CTkFrame
    row: int
    selected: int

    def __init__(self, master: Misc) -> None:
        self.tab_master = CTkFrame(master)
        self.body_master = CTkFrame(master, fg_color="transparent")
        self.row = 0
        self.selected = 0

    def create(self):
        self.tab_master.pack(side=ctk.LEFT, fill=ctk.Y, padx=5, pady=5)
        self.body_master.pack(side=ctk.LEFT, expand=True, fill=ctk.BOTH, padx=0, pady=5)
        children_destroy(self.tab_master)
        self.row = 0
        return self

    def add(self, text: str, callback: Callable):
        row = self.row
        text_color = CTkm.theme["MenuComponent"]["text_color"]
        command = lambda: self.callback_wrapper(callback, row=row)  # noqa E731

        btn = CTkButton(self.tab_master, text=text, fg_color="transparent", text_color=text_color, command=command)
        btn.pack(pady=2, padx=4)

        if self.selected == row:
            self.render(callback, row=row)
        self.row += 1

    def callback_wrapper(self, callback, row):
        if self.selected != row:
            self.render(callback, row)

    def render(self, callback, row):
        for key, child in enumerate(self.tab_master.winfo_children()):
            if key == row:
                self.selected = key
                child.configure(
                    fg_color=CTkm.theme["CTkButton"]["fg_color"],
                    hover_color=CTkm.theme["CTkButton"]["fg_color"],
                    text_color=CTkm.theme["CTkButton"]["text_color"],
                )
            else:
                child.configure(
                    fg_color="transparent",
                    hover_color=CTkm.theme["CTkButton"]["hover_color"],
                    text_color=CTkm.theme["MenuComponent"]["text_color"],
                )
            child.update()

        children_destroy(self.body_master)
        callback(self.body_master)

    def is_dark(self):
        return ctk.get_appearance_mode() == "Dark"
