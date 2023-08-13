from pathlib import Path
from tkinter import Frame, Misc, StringVar, filedialog
from typing import Callable, Optional

import customtkinter as ctk
import i18n
from component.var import PathVar
from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu
from customtkinter import ThemeManager as CTkm


class LabelComponent(CTkFrame):
    text: str
    frame: CTkFrame
    tooltip: list[str]
    required: bool

    def __init__(self, master: Misc, text: str, tooltip: Optional[list[str]] = None, required: bool = False) -> None:
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.tooltip = tooltip or []
        self.frame = CTkFrame(self.master.master, fg_color=CTkm.theme["LabelComponent"]["fg_color"])
        self.required = required
        if self.required:
            self.tooltip.append(i18n.t("app.detail.required"))

    def create(self):
        label = CTkLabel(self, text=self.text)
        label.pack(side=ctk.LEFT)
        if len(self.tooltip):
            label.bind("<Enter>", self.enter_event)
            label.bind("<Leave>", self.leave_event)
            CTkLabel(self.frame, text="\n".join(self.tooltip), fg_color=CTkm.theme["LabelComponent"]["fg_color"]).pack(padx=5, pady=0)

        if self.required:
            CTkLabel(self, text=i18n.t("app.symbol.required"), text_color=CTkm.theme["LabelComponent"]["required_color"]).pack(side=ctk.LEFT)

        return self

    def enter_event(self, event):
        assert self.tooltip is not None
        self.frame.place(x=self.winfo_rootx() - self.frame.master.winfo_rootx(), y=self.winfo_rooty() - self.frame.master.winfo_rooty() + 25)

    def leave_event(self, event):
        assert self.tooltip is not None
        self.frame.place_forget()


class EntryComponent(CTkFrame):
    variable: StringVar
    text: str
    required: bool
    tooltip: list[str]
    required: bool

    def __init__(self, master: Frame, text: str, variable: StringVar, tooltip: Optional[list[str]] = None, required: bool = False) -> None:
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable
        self.tooltip = tooltip or []
        self.required = required

    def create(self):
        LabelComponent(self, text=self.text, required=self.required, tooltip=self.tooltip).create()

        CTkEntry(self, textvariable=self.variable).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self


class PathComponentBase(EntryComponent):
    variable: PathVar

    def __init__(self, master: Frame, text: str, variable: PathVar, tooltip: Optional[list[str]] = None, required: bool = False) -> None:
        super().__init__(master, text, variable, tooltip, required)

    def create(self):
        super().create()

        CTkButton(self, text=i18n.t("app.word.reference"), command=self.callback, width=0).pack(side=ctk.LEFT, padx=2)
        return self

    def callback(self):
        raise NotImplementedError


class FilePathComponent(PathComponentBase):
    def callback(self):
        path = filedialog.askopenfilename(title=self.text, initialdir=self.variable.get())
        if path != "":
            self.variable.set_path(Path(path))


class DirectoryPathComponent(PathComponentBase):
    def callback(self):
        path = filedialog.askdirectory(title=self.text, initialdir=self.variable.get())
        if path != "":
            self.variable.set_path(Path(path))


class OptionMenuComponent(CTkFrame):
    variable: StringVar
    text: str
    values: list[str]
    command: Optional[Callable[[str], None]]

    def __init__(self, master: Frame, text: str, variable: StringVar, values: list[str], command: Optional[Callable[[str], None]] = None):
        super().__init__(master, fg_color=CTkm.theme["CTkToplevel"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable
        self.values = values
        self.command = command

    def create(self):
        LabelComponent(self, text=self.text, required=True).create()

        CTkOptionMenu(self, values=self.values, variable=self.variable, command=self.command).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self
