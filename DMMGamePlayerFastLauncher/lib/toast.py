import traceback
import webbrowser
from tkinter import Misc, Tk, Toplevel
from typing import Union

import customtkinter as ctk
import i18n
from customtkinter import CTkBaseClass, CTkButton, CTkFrame, CTkLabel, CTkTextbox, CTkToplevel
from static.config import UrlConfig
from utils.utils import get_isinstance


def error_toast(func):
    def _wrapper(self, *arg, **kwargs):
        try:
            assert isinstance(self.toast, ToastController)
            return func(self, *arg, **kwargs)
        except Exception as e:
            self.toast.error(str(e))
            raise

    return _wrapper


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

    def info(self, text: str):
        widget = InfoLabel(self.instance.master, text=text).create()
        self.instance.show(widget)

    def error(self, text: str):
        widget = ErrorLabel(self.instance.master, text=text).create()
        self.instance.show(widget)

    def show(self, widget: "CTkBaseClass"):
        self.toast_list.append(widget)
        self.update_state()
        self.after(5000, self.hide)

    def update_state(self):
        for key, x in enumerate(reversed(self.toast_list)):
            x.place(x=-18, y=-28 * key - 10, relx=1, rely=1, anchor=ctk.SE)

    def hide(self):
        widget = self.toast_list.pop(0)
        widget.destroy()
        self.update_state()


class InfoLabel(CTkFrame):
    text: str
    trace: str

    def __init__(self, master: Union[Tk, Toplevel], text: str) -> None:
        super().__init__(master, corner_radius=10)
        self.text = text

    def create(self):
        CTkLabel(self, text=self.text).pack(side=ctk.LEFT, padx=10)
        return self


class ErrorLabel(CTkFrame):
    text: str
    trace: str

    def __init__(self, master: Union[Tk, Toplevel], text: str) -> None:
        super().__init__(master, fg_color="red", corner_radius=10)
        self.text = text
        self.trace = traceback.format_exc()

    def create(self):
        CTkLabel(self, text=self.text).pack(side=ctk.LEFT, padx=10)
        btn = CTkButton(self, text=i18n.t("app.toast.details"), command=self.copy, width=0, height=0, fg_color="#ffaaaa", text_color="black", hover_color="white")
        btn.pack(side=ctk.LEFT, padx=10)
        return self

    def copy(self):
        ErrorWindow(self.master, self.text, self.trace).create()


class ErrorWindow(CTkToplevel):
    text: str
    trace: str

    def __init__(self, master, text: str, trace: str, quit: bool = False):
        super().__init__(master)
        self.text = text
        self.trace = trace
        self.geometry("600x300")
        self.deiconify()
        self.lift()
        self.focus_force()

        if quit:
            self.protocol("WM_DELETE_WINDOW", self.quit)

    def create(self):
        ErrorFrame(self, self.text, self.trace).create().pack(fill=ctk.BOTH, padx=10, pady=10, expand=True)
        return self


class ErrorFrame(CTkFrame):
    text: str
    trace: str

    def __init__(self, master, text: str, trace: str):
        super().__init__(master, fg_color="transparent")
        self.text = text
        self.trace = trace

    def create(self):
        CTkLabel(self, text=self.text).pack(pady=10)

        box = CTkTextbox(self, height=30)
        box.pack(fill=ctk.BOTH, padx=10, pady=(0, 10), expand=True)
        box.insert("0.0", self.trace)

        frame = CTkFrame(self, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, padx=10, pady=(0, 10))

        CTkButton(frame, text=i18n.t("app.toast.copy_to_clipboard"), command=lambda: self.clipboard(box)).pack(side=ctk.LEFT, expand=True)

        CTkButton(frame, text=i18n.t("app.toast.report"), command=lambda: self.report()).pack(side=ctk.LEFT, expand=True)
        return self

    def clipboard(self, box: CTkTextbox):
        self.clipboard_clear()
        self.clipboard_append(box.get("0.0", "end"))
        self.update()

    def report(self):
        webbrowser.open(UrlConfig.ISSUE)
