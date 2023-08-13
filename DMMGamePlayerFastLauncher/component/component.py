from pathlib import Path
from tkinter import Frame, StringVar, filedialog
from typing import Callable, Optional

import customtkinter as ctk
import i18n
from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu
from customtkinter import ThemeManager as CTkm


class LabelComponent(CTkFrame):
    text: str
    tooltip: Frame
    required: bool

    def __init__(self, master: Frame, text: str, tooltip: Optional[str] = None, required: bool = False) -> None:
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.tooltip = CTkFrame(self.master.master, fg_color=CTkm.theme["CTkFrame"]["fg_color"], corner_radius=0)

        self.required = required

    def create(self):
        label = CTkLabel(self, text=self.text)
        label.pack(side=ctk.LEFT)
        label.bind("<Enter>", self.enter_event)
        label.bind("<Leave>", self.leave_event)
        CTkLabel(self, text=i18n.t("*"), text_color="red").pack(side=ctk.LEFT)

        CTkLabel(self.tooltip, text="入力必須項目です。必ず入力してください。", fg_color=CTkm.theme["CTkFrame"]["fg_color"]).pack(padx=5, pady=0)

        return self

    def enter_event(self, event):
        assert self.tooltip is not None
        self.tooltip.place(x=0, y=50)

    def leave_event(self, event):
        assert self.tooltip is not None
        self.tooltip.place_forget()


class EntryComponent(CTkFrame):
    variable: StringVar
    text: str

    def __init__(self, master: Frame, text: str, variable: StringVar) -> None:
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable

    def create(self):
        CTkLabel(self, text=self.text).pack(anchor=ctk.W)

        CTkEntry(self, textvariable=self.variable).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self


class PathComponentBase(EntryComponent):
    def create(self):
        super().create()

        CTkButton(self, text=i18n.t("app.word.reference"), command=self.callback, width=0).pack(side=ctk.LEFT, padx=2)
        return self

    def callback(self):
        raise NotImplementedError


class FilePathComponent(PathComponentBase):
    def callback(self):
        path = filedialog.askopenfilename(title=self.text, initialdir=self.variable.get())
        self.variable.set(str(Path(path)))


class DirectoryPathComponent(PathComponentBase):
    def callback(self):
        path = filedialog.askdirectory(title=self.text, initialdir=self.variable.get())
        if path != "":
            self.variable.set(str(Path(path)))


class OptionMenuComponent(CTkFrame):
    variable: StringVar
    text: str
    values: list[str]
    command: Optional[Callable[[str], None]]

    def __init__(
        self,
        master: Frame,
        text: str,
        variable: StringVar,
        values: list[str],
        command: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable
        self.values = values
        self.command = command

    def create(self):
        CTkLabel(self, text=self.text).pack(anchor=ctk.W)

        CTkOptionMenu(self, values=self.values, variable=self.variable, command=self.command).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self
