import tkinter as tk
from pathlib import Path
from tkinter import Frame, Misc, StringVar, filedialog
from typing import Any, Callable, Optional

import customtkinter as ctk
import i18n
from component.var import PathVar
from customtkinter import CTkBaseClass, CTkButton, CTkCheckBox, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu, CTkProgressBar, CTkToplevel, Variable
from customtkinter import ThemeManager as CTkm


class LabelComponent(CTkFrame):
    text: str
    frame: CTkFrame
    tooltip: Optional[str]
    required: bool

    def __init__(self, master: Misc, text: str, tooltip: Optional[str] = None, required: bool = False) -> None:
        super().__init__(master, fg_color="transparent")
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.tooltip = tooltip
        self.frame = CTkFrame(self.winfo_toplevel(), fg_color=CTkm.theme["LabelComponent"]["fg_color"])
        self.required = required
        if self.required:
            if self.tooltip:
                self.tooltip = i18n.t("app.component.required") + "\n" + self.tooltip
            else:
                self.tooltip = i18n.t("app.component.required")

    def create(self):
        label = CTkLabel(self, text=self.text)
        label.pack(side=ctk.LEFT)
        if self.tooltip is not None:
            label.bind("<Enter>", self.enter_event)
            label.bind("<Leave>", self.leave_event)
            CTkLabel(self.frame, text=self.tooltip, fg_color=CTkm.theme["LabelComponent"]["fg_color"], justify=ctk.LEFT).pack(padx=5, pady=0)

        if self.required:
            CTkLabel(self, text=i18n.t("app.component.required_symbol"), text_color=CTkm.theme["LabelComponent"]["required_color"], justify=ctk.LEFT).pack(side=ctk.LEFT)

        return self

    def enter_event(self, event):
        assert self.tooltip is not None
        self.frame.place(x=self.winfo_rootx() - self.frame.master.winfo_rootx(), y=self.winfo_rooty() - self.frame.master.winfo_rooty() + 28)

    def leave_event(self, event):
        assert self.tooltip is not None
        self.frame.place_forget()

    def destroy(self):
        self.frame.destroy()
        return super().destroy()


class CheckBoxComponent(CTkFrame):
    variable: Variable
    text: str

    def __init__(self, master: Frame, text: str, variable: Variable):
        super().__init__(master, fg_color="transparent")
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable

    def create(self):
        CTkCheckBox(
            self,
            height=40,
            checkbox_width=CTkm.theme["CheckBoxComponent"]["checkbox_width"],
            checkbox_height=CTkm.theme["CheckBoxComponent"]["checkbox_height"],
            border_width=CTkm.theme["CheckBoxComponent"]["border_width"],
            text=self.text,
            variable=self.variable,
        ).pack(fill=ctk.X)
        return self


class EntryComponent(CTkFrame):
    variable: Variable
    text: str
    required: bool
    tooltip: Optional[str]
    required: bool
    command: list[tuple[str, Callable[[Variable], None]]]
    state: str
    alnum_only: bool

    def __init__(
        self,
        master: Frame,
        text: str,
        variable: Variable,
        tooltip: Optional[str] = None,
        required: bool = False,
        command: Optional[list[tuple[str, Callable[[Variable], None]]]] = None,
        state: Optional[str] = None,
        alnum_only: bool = False,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable
        self.tooltip = tooltip
        self.required = required
        self.command = command or []
        self.state = state or tk.NORMAL
        self.alnum_only = alnum_only

    def create(self):
        LabelComponent(self, text=self.text, required=self.required, tooltip=self.tooltip).create()
        entry = CTkEntry(self, textvariable=self.variable, state=self.state)
        entry.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        if self.alnum_only:
            entry.bind("<Key>", self.alnum_only_callback)

        for cmd in self.command:
            CTkButton(self, text=cmd[0], command=self.call(cmd[1]), width=0).pack(side=ctk.LEFT, padx=2)
        return self

    def call(self, cmd):
        return lambda: cmd(self.variable)

    def alnum_only_callback(self, event):
        char = event.char.encode("utf-8")
        if event.keysym in ["backslash", "colon", "slash", "asterisk", "question", "quote", "less", "greater", "pipe"]:
            return "break"
        if char.isascii():
            return
        return "break"


class ButtonComponent(CTkFrame):
    frame: CTkFrame
    text: str
    tooltip: Optional[str]
    command: Callable[[], None]
    state: str

    def __init__(
        self,
        master: Frame,
        text: str,
        command: Callable[[], None],
        tooltip: Optional[str] = None,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.frame = CTkFrame(self.winfo_toplevel(), fg_color=CTkm.theme["LabelComponent"]["fg_color"])
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.tooltip = tooltip
        self.command = command

    def create(self):
        button = CTkButton(self, text=self.text, command=self.command)
        button.pack(fill=ctk.X, pady=5)
        if self.tooltip is not None:
            button.bind("<Enter>", self.enter_event)
            button.bind("<Leave>", self.leave_event)
            CTkLabel(self.frame, text=self.tooltip, fg_color=CTkm.theme["LabelComponent"]["fg_color"], justify=ctk.LEFT).pack(padx=5, pady=0)

        return self

    def enter_event(self, event):
        assert self.tooltip is not None
        self.frame.place(x=self.winfo_rootx() - self.frame.master.winfo_rootx(), y=self.winfo_rooty() - self.frame.master.winfo_rooty() + 35)

    def leave_event(self, event):
        assert self.tooltip is not None
        self.frame.place_forget()

    def destroy(self):
        self.frame.destroy()
        return super().destroy()


class PathComponentBase(EntryComponent):
    variable: PathVar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command.append((i18n.t("app.component.reference"), self.reference_callback))

    def reference_callback(self, variable):
        raise NotImplementedError


class FilePathComponent(PathComponentBase):
    def reference_callback(self, variable):
        path = filedialog.askopenfilename(title=self.text, initialdir=variable.get())
        if path != "":
            variable.set_path(Path(path))


class DirectoryPathComponent(PathComponentBase):
    def reference_callback(self, variable):
        path = filedialog.askdirectory(title=self.text, initialdir=variable.get())
        if path != "":
            variable.set_path(Path(path))


class OptionMenuComponent(CTkFrame):
    variable: StringVar
    text: str
    values: list[str]
    command: Optional[Callable[[str], None]]
    tooltip: Optional[str]

    def __init__(self, master: Frame, text: str, variable: StringVar, values: list[str], command: Optional[Callable[[str], None]] = None, tooltip: Optional[str] = None):
        super().__init__(master, fg_color="transparent")
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable
        self.values = values
        self.command = command
        self.tooltip = tooltip

    def create(self):
        required = self.variable.get() not in self.values
        LabelComponent(self, text=self.text, tooltip=self.tooltip, required=required).create()
        CTkOptionMenu(self, values=self.values, variable=self.variable, command=self.command).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self


class OptionMenuTupleComponent(CTkFrame):
    variable: StringVar
    shadow_variable: StringVar
    text: str
    values: list[tuple[Any, str]]
    command: Optional[Callable[[str], None]]
    tooltip: Optional[str]

    def __init__(
        self, master: Frame, text: str, variable: StringVar, values: list[tuple[Any, str]], command: Optional[Callable[[str], None]] = None, tooltip: Optional[str] = None
    ):
        super().__init__(master, fg_color="transparent")
        self.pack(fill=ctk.X, expand=True)
        self.text = text
        self.variable = variable
        default = [x[1] for x in values if x[0] == variable.get()]
        self.shadow_variable = StringVar(value=default[0] if len(default) else None)
        self.values = values
        self.command = command
        self.tooltip = tooltip

    def create(self):
        required = self.shadow_variable.get() not in [x[1] for x in self.values]
        LabelComponent(self, text=self.text, tooltip=self.tooltip, required=required).create()
        values = [x[1] for x in self.values]

        CTkOptionMenu(self, values=values, variable=self.shadow_variable, command=self.callback).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self

    def callback(self, text: str):
        var = [x[0] for x in self.values if x[1] == text][0]
        self.variable.set(var)
        if self.command is not None:
            self.command(var)


class PaddingComponent(CTkFrame):
    def __init__(self, master: Frame, width: int = 0, height: int = 0):
        super().__init__(master, fg_color="transparent")
        self.pack(fill=ctk.X, expand=True)
        self.width = width
        self.height = height

    def create(self):
        CTkBaseClass(self, width=self.width, height=self.height).pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        return self


class ConfirmWindow(CTkToplevel):
    command: Callable
    text: str

    def __init__(self, master: Frame, command: Callable, text: str):
        super().__init__(master)
        self.geometry("300x100")
        self.command = command
        self.text = text

    def create(self):
        CTkLabel(self, text=self.text).pack(side=ctk.TOP, fill=ctk.X)
        CTkButton(self, text=i18n.t("app.component.yes"), command=self.yes).pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=10)
        CTkButton(self, text=i18n.t("app.component.no"), command=self.no).pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=10)

    def yes(self):
        try:
            self.command()
        except Exception:
            self.destroy()
            raise
        self.destroy()

    def no(self):
        self.destroy()


class CTkProgressWindow(CTkToplevel):
    label: CTkLabel
    progress: CTkProgressBar
    now: float
    max: float

    def __init__(self, master: Misc, now: float = 0, max: float = 1):
        super().__init__(master)
        self.geometry("300x100")
        self.label = CTkLabel(self, text="0.00%", justify=ctk.LEFT, anchor=ctk.W)
        self.progress = CTkProgressBar(self, width=300)

        self.deiconify()
        self.lift()
        self.focus_force()

        self.now = now
        self.max = max

    def create(self):
        CTkLabel(self, text=i18n.t("app.component.download")).pack(fill=ctk.X, expand=True, padx=10, pady=(10, 0))
        self.label.pack(fill=ctk.X, expand=True, padx=10, pady=0)
        self.progress.pack(fill=ctk.X, expand=True, padx=10, pady=(0, 10))

        self.progress.set(self.now / self.max)
        return self

    def add(self, value: float):
        self.now += value
        self.progress.set(self.now / self.max)
        self.label.configure(text=f"{(self.now / self.max * 100):.2f}%")

    def set(self, value: float):
        self.now = value
        self.progress.set(self.now / self.max)
        self.label.configure(text=f"{(self.now / self.max * 100):.2f}%")
