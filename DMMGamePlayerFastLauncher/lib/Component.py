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


class TabMenuComponent:
    tab_master: CTkFrame
    body_master: CTkFrame
    row: int = 0

    def __init__(self, master: Misc) -> None:
        self.tab_master = CTkFrame(master)
        self.body_master = CTkFrame(master)

        self.tab_master.pack(side=ctk.LEFT, fill=ctk.Y, padx=5, pady=5)
        self.body_master.pack(
            side=ctk.LEFT,
            expand=True,
            fill=ctk.BOTH,
            padx=(5, 0),
            pady=5,
        )

    def add(self, text: str, callback):
        row = self.row

        CTkButton(
            self.tab_master,
            text=text,
            fg_color=CTKM.theme["CTkFrame"]["fg_color"],
            command=lambda: self.callback_wrapper(callback, row=row),
        ).pack()

        if self.row == 0:
            self.callback_wrapper(callback, row=self.row)

        self.row += 1

    def callback_wrapper(self, callback, row):
        tab_children: list[CTkButton] = self.tab_master.winfo_children()
        body_children: list[CTkBaseClass] = self.body_master.winfo_children()

        for child in body_children:
            child.destroy()

        for key, child in enumerate(tab_children):
            if key == row:
                child.configure(
                    fg_color=CTKM.theme["CTkButton"]["fg_color"],
                    hover_color=CTKM.theme["CTkButton"]["fg_color"],
                )
            else:
                child.configure(
                    fg_color=CTKM.theme["CTkFrame"]["fg_color"],
                    hover_color=CTKM.theme["CTkButton"]["hover_color"],
                )
            child.update()

        callback(self.body_master)


class EntryComponent:
    master: Frame
    var: StringVar
    text: str

    def __init__(
        self,
        master: Frame,
        text: str,
        var: StringVar,
    ) -> None:
        self.master = CTkFrame(master, fg_color=CTKM.theme["CTkToplevel"]["fg_color"])
        self.master.pack(fill=ctk.X, expand=True)
        self.text = text
        self.var = var

    def create(self):
        CTkLabel(self.master, text=self.text).pack(anchor=ctk.W)

        CTkEntry(
            self.master,
            textvariable=self.var,
        ).pack(
            side=ctk.LEFT,
            fill=ctk.BOTH,
            expand=True,
        )
        return self


class PathComponentBase(EntryComponent):
    def create(self):
        super().create()

        CTkButton(
            self.master,
            text=i18n.t("app.word.reference"),
            command=self.callback,
            width=10,
        ).pack(side=ctk.LEFT)
        return self

    def callback(self):
        raise NotImplementedError


class FilePathComponent(PathComponentBase):
    def callback(self):
        path = filedialog.askopenfilename(title=self.text, initialdir=self.var.get())
        self.var.set(str(Path(path)))


class DirectoryPathComponent(PathComponentBase):
    def callback(self):
        path = filedialog.askdirectory(title=self.text, initialdir=self.var.get())
        self.var.set(str(Path(path)))


T = TypeVar("T")


def isinstance_filter(obj, cls: type[T]) -> list[T]:
    return list(filter(lambda x: isinstance(x, cls), obj))


def get_isinstance(obj, cls: type[T]) -> Optional[T]:
    ins = isinstance_filter(obj, cls)
    if len(ins) > 0:
        return ins[0]
    return None
