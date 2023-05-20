# pyinstaller --noconfirm --onefile --noconsole --add-data 'background.png;.' --add-data 'ico.ico;.' --icon=ico.ico ReaperScript.py
from multiprocessing import freeze_support
from check_standalone import fix_checker
from threading import Thread
from reapy import reascript_api as RPR
from typing import List, Dict
from PIL import Image, ImageTk
from config_works import (
    get_config,
    load_path,
    get_option,
    save_options,
)
from file_works import (
    file_works,
    path_choice,
    resource_path,
)
from reaper_works import (
    audio_select,
    split,
    hidden_normalize,
    import_subs,
    fix_check,
    project_save,
    back_up,
    render,
    create_project,
    de_noizer,
)
from window_utils import (
    on_closing,
    buttons_freeze,
    buttons_active,
    is_reaper_run,
    show_help_window,
)
from help_texts import HELP_DICT
from tkinter import ttk
from tktooltip import ToolTip
import tkinter.messagebox
import asstosrt
import win32gui
import win32con
import pysubs2
import tkinter
import ffmpeg
import reapy
import time
import os


def make_episode(
        video: List[str],
        folder: str,
        title: str,
        number: str,
        ext: str,
        output_file: str
        ) -> None:
    """Функция для создания видео с озвучкой"""
    video_path = os.path.normpath(video[0])
    audio_path = output_file
    output_file = f'{folder}/{title} {number} DUB{ext}'
    video_file = ffmpeg.input(video_path)
    audio_file = ffmpeg.input(audio_path)
    output_options = {
        'vcodec': 'copy',
        'acodec': 'aac',
        'audio_bitrate': '256k',
    }
    output = ffmpeg.output(
        video_file['v'],
        audio_file['a'],
        output_file,
        **output_options)
    ffmpeg.run(output)


def reaper_main(
        checkboxes: Dict[str, str],
        master: tkinter.Tk,
        BUTTONS: List
        ) -> None:
    """Основная функция"""
    save_options(checkboxes)
    project_path = load_path('project_path')
    if not project_path:
        path_choice('project_path')
        project_path = load_path('project_path')
    if get_option('noise_reduction') and not load_path('nrtemplate'):
        path_choice('nrtemplate')
    folder = path_choice('folder')
    if folder:
        buttons_freeze(master, BUTTONS)
    subs, audio, video, title, number, ext = file_works(folder)
    if audio and video and load_path('project_path'):
        master.iconify()
        new_path = project_save(folder, project_path, 'main', title, number)
        hwnd = win32gui.FindWindow('REAPERwnd', None)
        win32gui.ShowWindow(hwnd, 2)
        if get_option('noise_reduction') and load_path('nrtemplate'):
            audio = de_noizer(folder, audio)
        project = create_project(new_path)
        audio_select(audio, 'main')
        RPR.InsertMedia(video[0], 512 | 0)
        project.save(False)
        if subs:
            sbttls = pysubs2.load(subs[0])
            step = len(sbttls) // 8
            strt_idx, end_idx = 0, step
            if get_option('sub_region'):
                import_subs(sbttls, project, step, 'region', strt_idx, end_idx)
            if get_option('sub_item'):
                import_subs(sbttls, project, step, 'item', strt_idx, end_idx)
        if get_option('split'):
            split(project)
        project.save(False)
        hidden_normalize(project)
        back_up(project, new_path)
        if get_option('fix_check'):
            fix_check(project, subs)
        project.save(False)
        if get_option('render_audio'):
            output_file = render(folder, 'main')
            time.sleep(2)
            old_file_size = os.path.getsize(output_file)
            time.sleep(3)
            new_file_size = os.path.getsize(output_file)
            while old_file_size < new_file_size:
                old_file_size = os.path.getsize(output_file)
                time.sleep(3)
                new_file_size = os.path.getsize(output_file)
            time.sleep(2)
            if get_option('render_video'):
                make_episode(video, folder, title, number, ext, output_file)
    buttons_active(master, BUTTONS)
    master.wm_deiconify()
    master.focus_force()


def on_start_click(checkboxes: Dict, master: tkinter.Tk, BUTTONS: List):
    thread = Thread(target=reaper_main, args=(checkboxes, master, BUTTONS))
    thread.start()


def on_fix_check_click(master: tkinter.Tk, BUTTONS: List):
    thread = Thread(target=fix_checker, args=(master, BUTTONS))
    thread.start()


master = tkinter.Tk(className='REAPERSCRIPT.main')
width = 380
height = 440
s_width = master.winfo_screenwidth()
s_height = master.winfo_screenheight()
upper = s_height // 8
x = (s_width - width) // 2
y = (s_height - height) // 2
master.geometry(f'{width}x{height}+{x}+{y - upper}')
master.resizable(width=False, height=False)
master.title('REAPERSCRIPT v3.20')
master.iconbitmap(default=resource_path('ico.ico'))
img = Image.open(resource_path('background.png'))
tk_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(master, image=tk_img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
master.protocol('WM_DELETE_WINDOW', on_closing)
OPTIONS = [
    'noise_reduction',
    'volume_up_dubbers',
    'subs_cleaner',
    'sub_region',
    'sub_item',
    'split',
    'normalize',
    'normalize_dubbers',
    'normalize_video',
    'fix_check',
    'render_audio',
    'render_video',
]
config = get_config()
checkboxes = {}
checkbox_style = ttk.Style()
checkbox_style.configure('TCheckbutton', background='#ffc0cb')
button_style = ttk.Style()
button_style.configure('TButton', background='#ffc0cb')
for i, option in enumerate(OPTIONS):
    var = tkinter.BooleanVar()
    if option in config['OPTIONS']:
        var.set(config['OPTIONS'].getboolean(option))
    else:
        var.set(False)
    checkbox = ttk.Checkbutton(
        master,
        text=option,
        variable=var,
        padding=7,
    )
    checkbox.grid(
        row=i,
        column=0,
        sticky=tkinter.W
    )
    ToolTip(checkbox, HELP_DICT[option], 1)
    checkboxes[option] = var
BUTTONS = [
    'start',
    'template',
    'rfx',
    'fixcheck_standalone',
    'help',
    'nrtemplate',
]
start_bttn = ttk.Button(
    master,
    text='START',
    name='start',
    command=lambda: on_start_click(checkboxes, master, BUTTONS)
)
start_bttn.place(relx=0.5, rely=1.0, anchor="s", y=-9)
ToolTip(start_bttn, HELP_DICT['start'], 1)
template_btn = ttk.Button(
    master,
    text='TEMPLATE',
    name='template',
    command=lambda: path_choice('project_path')
)
template_btn.grid(
    row=(len(OPTIONS) + 2),
    column=0,
    sticky=tkinter.W,
    padx=6,
    pady=3
)
ToolTip(template_btn, HELP_DICT['template'], 1)
rfxchains_btn = ttk.Button(
    master,
    text='RFXCHAINS',
    name='rfx',
    command=lambda: path_choice('fx_chains_folder')
)
rfxchains_btn.grid(
    row=(len(OPTIONS) + 3),
    column=0,
    sticky=tkinter.W,
    padx=6,
    pady=3
)
ToolTip(rfxchains_btn, HELP_DICT['rfx'], 1)
fix_check_btn = ttk.Button(
    master,
    text='FIXCHECK',
    name='fixcheck_standalone',
    command=lambda: on_fix_check_click(master, BUTTONS)
)
fix_check_btn.place(relx=0.5, rely=1.0, anchor="s", x=145, y=-9)
ToolTip(fix_check_btn, HELP_DICT['fixcheck_standalone'], 1)
nr_template_btn = ttk.Button(
    master,
    text='NR TEMP',
    name='nrtemplate',
    command=lambda: path_choice('nrtemplate')
)
nr_template_btn.place(relx=0.5, rely=1.0, anchor="s", x=145, y=-40)
ToolTip(nr_template_btn, HELP_DICT['nrtemplate'], 1)
help_btn = ttk.Button(
    master,
    text='HELP',
    name='help',
    command=lambda: show_help_window(master),
)
help_btn.place(relx=0.5, rely=1.0, anchor="s", x=145, y=-407)
ToolTip(help_btn, HELP_DICT['help'], 1)


if __name__ == '__main__':
    freeze_support()
    is_reaper_run()
    master.focus_force()
    master.mainloop()
