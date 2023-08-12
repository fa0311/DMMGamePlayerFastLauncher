from typing import Optional, TypeVar, Union, List
import os
from tkinter import (
    BaseWidget,
    Entry,
    Frame,
    StringVar,
    Tk,
    Toplevel,
    Widget,
    filedialog,
    Misc,
    Label,
)
import webbrowser
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
    CTkToplevel,
    CTkTextbox,
)
from customtkinter import ThemeManager as CTKM
import queue

import traceback

from lib.Component import get_isinstance


# class ToastComponent(CTkFrame):
#     def __init__(self, master: Misc) -> None:
#         self.instance = get_isinstance(master, ToastComponent)

#         super().__init__(
#             master,
#             width=0,
#             height=0,
#             bg_color="transparent",
#             fg_color="transparent",
#         )
#         self.place(x=-20, relx=1, rely=1, anchor=ctk.SE)
#         CTkBaseClass(self, width=0, height=0).pack()

#     def show(self, text: str) -> None:
#         if self.instance:
#             return self.instance.show(text)

#         label = CTkLabel(self, text=text, fg_color="transparent")
#         label.pack(anchor=ctk.SE, padx=10)
#         self.after(3000, lambda: self.hide(label))

#     def hide(self, label: CTkLabel):
#         label.destroy()


class ToastController(CTkFrame):
    master: Union[Tk, Toplevel]
    instance: "ToastController"
    toast_list: list["CTkBaseClass"]

    def __init__(self, master: Misc) -> None:
        self.master = master.winfo_toplevel()
        instance = get_isinstance(self.master.winfo_children(), ToastController)
        self.toast_list = []
        if instance:
            self.instance = instance
        else:
            super().__init__(self.master)
            self.place()
            self.instance = self
            print("create")

    def info(self, text: str):
        widget = InfoLabel(self.instance.master, text=text)
        self.instance.show(widget)

    def error(self, text: str):
        widget = ErrorLabel(self.instance.master, text=text)
        self.instance.show(widget)

    def show(self, widget: "CTkBaseClass"):
        self.toast_list.append(widget)
        self.update()
        self.after(5000, self.hide)

    def update(self):
        for key, x in enumerate(reversed(self.toast_list)):
            x.place(x=-18, y=-28 * key - 10, relx=1, rely=1, anchor=ctk.SE)

    def hide(self):
        widget = self.toast_list.pop(0)
        widget.destroy()
        self.update()


class InfoLabel(CTkFrame):
    text: str
    trace: str

    def __init__(self, master: Union[Tk, Toplevel], text: str) -> None:
        super().__init__(master, corner_radius=10)
        self.text = text
        self.create()

    def create(self):
        CTkLabel(
            self,
            text=self.text,
        ).pack(side=ctk.LEFT, padx=10)


class ErrorLabel(CTkFrame):
    text: str
    trace: str

    def __init__(self, master: Union[Tk, Toplevel], text: str) -> None:
        super().__init__(master, fg_color="red", corner_radius=10)
        self.text = text
        self.trace = traceback.format_exc()
        self.create()

    def create(self):
        CTkLabel(
            self,
            text=self.text,
        ).pack(side=ctk.LEFT, padx=10)
        CTkButton(
            self,
            text="詳細",
            command=self.copy,
            width=0,
            height=0,
            fg_color="#ffaaaa",
            text_color="black",
            hover_color="white",
        ).pack(side=ctk.LEFT, padx=10)

    def copy(self):
        ErrorWindow(self.master, self.text, self.trace)


class ErrorWindow(CTkToplevel):
    text: str
    trace: str

    def __init__(self, master, text: str, trace: str):
        super().__init__(master)
        self.text = text
        self.trace = trace
        self.geometry("600x300")
        self.create()

    def create(self):
        CTkLabel(self, text=self.text).pack(pady=10)

        box = CTkTextbox(self)
        box.pack(fill=ctk.BOTH, padx=10, pady=(0, 10), expand=True)
        box.insert("0.0", self.trace)

        frame = CTkFrame(self)
        frame.pack(fill=ctk.BOTH, padx=10, pady=(0, 10))

        CTkButton(
            frame,
            text="クリップボードにコピー",
            command=lambda: self.clipboard(box),
        ).pack(side=ctk.LEFT, expand=True)

        CTkButton(
            frame,
            text="報告",
            command=lambda: self.report(),
        ).pack(side=ctk.LEFT, expand=True)

    def clipboard(self, box: CTkTextbox):
        self.clipboard_clear()
        self.clipboard_append(box.get("0.0", "end"))
        self.update()

    def report(self):
        url = "https://github.com/fa0311/DMMGamePlayerFastLauncher/issues/new"
        webbrowser.open(url)
