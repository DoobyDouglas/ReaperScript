from help_texts import HOW_TO_USE
from tkinter import ttk
from typing import List
import tkinter
import win32gui


def wait():
    pass


def on_closing():
    raise SystemExit


def on_closing_help(
        master: tkinter.Tk,
        help_window: tkinter.Tk
        ):
    master.nametowidget('help').config(state='normal')
    help_window.destroy()


def buttons_freeze(master: tkinter.Tk, BUTTONS: List):
    for button in BUTTONS:
        if button != 'help':
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


def show_help_window(master: tkinter.Tk):
    master.nametowidget('help').config(state='disabled')
    master_geometry_x = master.geometry().split('+')[0].split('x')[0]
    master_geometry_y = master.geometry().split('+')[0].split('x')[1]
    master_position = master.geometry().split('x')[1].split('+')[1:]
    x = int(master_position[0]) + int(master_geometry_x) + 6
    y = master_position[1]
    help_window = tkinter.Toplevel(master)
    help_window.title('HOW TO USE')
    help_window.geometry(f'615x{master_geometry_y}+{x}+{y}')
    help_window.resizable(False, False)
    help_window.protocol(
        'WM_DELETE_WINDOW',
        lambda: on_closing_help(master, help_window)
    )
    text_field = tkinter.Text(
        help_window,
        background='#ffc0cb',
        padx=6,
        pady=3,
    )
    text_field.insert('1.0', HOW_TO_USE)
    text_field.configure(state='disabled')
    scrollbar = ttk.Scrollbar(
        help_window,
        orient='vertical',
        command=text_field.yview
    )
    text_field.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    text_field.pack(side='left', fill='both', expand=True)
    help_window.focus_force()
    help_window.mainloop()


def set_geometry(master: tkinter.Tk):
    width = 380
    height = 476
    s_width = master.winfo_screenwidth()
    s_height = master.winfo_screenheight()
    upper = s_height // 8
    x = (s_width - width) // 2
    y = (s_height - height) // 2
    return f'{width}x{height}+{x}+{y - upper}'


if __name__ == '__main__':
    pass
