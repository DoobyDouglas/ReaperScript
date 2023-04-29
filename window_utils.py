from typing import List
import tkinter
import win32gui


def wait():
    pass


def on_closing():
    raise SystemExit


def buttons_freeze(master: tkinter.Tk, BUTTONS: List):
    for button in BUTTONS:
        master.nametowidget(button).config(state='disabled')
    master.protocol('WM_DELETE_WINDOW', wait)


def buttons_active(master: tkinter.Tk, BUTTONS: List):
    for button in BUTTONS:
        master.nametowidget(button).config(state='normal')
    master.protocol('WM_DELETE_WINDOW', on_closing)


def is_reaper_run():
    hwnd = win32gui.FindWindow(
        'REAPERwnd',
        None
    )
    if not hwnd:
        tkinter.messagebox.showerror(
            'REAPER выключен',
            'Сначала включите REAPER'
        )
        raise SystemExit
