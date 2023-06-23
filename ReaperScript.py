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
    normalize,
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
    set_geometry,
    get_subs_langs,
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
    save_options(master, checkboxes)
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
        if get_option('hide_reaper'):
            win32gui.ShowWindow(win32gui.FindWindow('REAPERwnd', None), 2)
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
                if get_option('add_track_for_subs'):
                    project.add_track(1, 'SUBTITLES')
                import_subs(sbttls, project, step, 'item', strt_idx, end_idx)
        if get_option('split'):
            split(project)
        project.save(False)
        if get_option('normalize_dubbers') and get_option('normalize_video'):
            normalize(project, 'all')
        elif get_option('normalize_dubbers'):
            normalize(project, 'dubbers')
        elif get_option('normalize_video'):
            normalize(project, 'video')
        back_up(project, new_path)
        if get_option('fix_check'):
            fix_check(project, subs)
        project.save(False)
        if get_option('render_audio'):
            output_file = render(folder, 'main')
            if get_option('render_video'):
                make_episode(video, folder, title, number, ext, output_file)
    buttons_active(master, BUTTONS)
    master.wm_deiconify()
    master.focus_force()


def on_start_click(
        checkboxes: Dict,
        master: tkinter.Tk,
        BUTTONS: List
        ):
    thread = Thread(
        target=reaper_main,
        args=(checkboxes, master, BUTTONS)
    )
    thread.start()


def on_fix_check_click(master: tkinter.Tk, BUTTONS: List):
    thread = Thread(target=fix_checker, args=(master, BUTTONS))
    thread.start()


master = tkinter.Tk(className='REAPERSCRIPT.main')
master.geometry(set_geometry(master))
master.resizable(False, False)
master.title('REAPERSCRIPT v3.33')
master.iconbitmap(default=resource_path('ico.ico'))
master.protocol('WM_DELETE_WINDOW', on_closing)
style = ttk.Style()
style.configure('TCheckbutton', background='#ffc0cb')
style.configure('TButton', background='#ffc0cb')
style.configure('TLabel', background='#ffc0cb')
style.configure('TButton', width=13)
raw_img = Image.open(resource_path('background.png'))
image = ImageTk.PhotoImage(raw_img)
background = tkinter.Label(master, image=image)
background.place(x=0, y=0, relwidth=1, relheight=1)
config = get_config()
checkboxes = {}
OPTIONS = [
    'noise_reduction',
    'volume_up_dubbers',
    'sub_region',
    'sub_item',
    'split',
    'normalize_dubbers',
    'normalize_video',
    'fix_check',
    'render_audio',
    'render_video',
    'hide_reaper',
    'subs_cleaner',
    'add_track_for_subs',
]
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
    )
    checkbox.grid(
        row=i + 1,
        column=0,
        sticky=tkinter.W,
        pady=3,
        padx=6,
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
start_bttn.place(relx=0.5, rely=1.0, anchor="s", y=-6)
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
nr_template_btn = ttk.Button(
    master,
    text='NR TEMPLATE',
    name='nrtemplate',
    command=lambda: path_choice('nrtemplate')
)
nr_template_btn.grid(
    row=(len(OPTIONS) + 3),
    column=0,
    sticky=tkinter.W,
    padx=6,
    pady=3
)
ToolTip(nr_template_btn, HELP_DICT['nrtemplate'], 1)
rfxchains_btn = ttk.Button(
    master,
    text='RFXCHAINS',
    name='rfx',
    command=lambda: path_choice('fx_chains_folder')
)
rfxchains_btn.place(relx=0.5, rely=1.0, anchor="s", x=140, y=-37)
ToolTip(rfxchains_btn, HELP_DICT['rfx'], 1)
fix_check_btn = ttk.Button(
    master,
    text='FIX CHECK',
    name='fixcheck_standalone',
    command=lambda: on_fix_check_click(master, BUTTONS)
)
fix_check_btn.place(relx=0.5, rely=1.0, anchor="s", x=140, y=-6)
ToolTip(fix_check_btn, HELP_DICT['fixcheck_standalone'], 1)
help_btn = ttk.Button(
    master,
    text='HELP',
    name='help',
    command=lambda: show_help_window(master),
)
help_btn.place(relx=0.5, rely=1.0, anchor="s", x=140, y=-422)
ToolTip(help_btn, HELP_DICT['help'], 1)
subs_extract = ttk.Label(master, text='Select subtitles to extract:')
subs_extract.grid(row=0, column=0, sticky=tkinter.W, padx=6, pady=9)
SUBS_LANGS_LIST = list(get_subs_langs().keys())
menu = ttk.Combobox(
    master,
    values=SUBS_LANGS_LIST,
    name='subs_lang',
    state='readonly',
    width=13,
)
try:
    if config['SUBS']['subs_lang'] in SUBS_LANGS_LIST:
        menu.set(config['SUBS']['subs_lang'])
    else:
        menu.set(SUBS_LANGS_LIST[0])
except KeyError:
    menu.set(SUBS_LANGS_LIST[0])
menu.place(relx=0.5, rely=1.0, anchor="s", x=9, y=-424)
ToolTip(menu, HELP_DICT['subs_lang'], 1)

if __name__ == '__main__':
    freeze_support()
    is_reaper_run()
    master.focus_force()
    master.mainloop()
