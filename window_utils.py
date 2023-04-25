from typing import List
import tkinter


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
