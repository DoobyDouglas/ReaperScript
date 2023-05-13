# Команду ниже нужно ввести один раз в консоли с включенным Reaper.
# python -c "import reapy; reapy.configure_reaper()"
# pyinstaller --noconfirm --onefile --noconsole --hidden-import=asstosrt --add-data 'background.png;.' --add-data 'ico.ico;.' --icon=ico.ico ReaperScript.py
from file_works import (
    file_works,
    path_choice,
    get_fx_chains,
    get_path_to_files,
)
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
import multiprocessing as mp
import tkinter.messagebox
import pysubs2
import tkinter
import ffmpeg
import ctypes
import shutil
import reapy
import time
import os
import win32gui
import win32con
import sys


def audio_select(audio: List[str]) -> None:
    """Функция для добавления аудио"""
    fx_chains_dict = get_fx_chains()
    for file in audio:
        RPR.InsertMedia(file, 1)
        track = reapy.get_last_touched_track()
        if get_option('volume_up_dubbers'):
            track.items[0].set_info_value('D_VOL', 1.5)
        if fx_chains_dict:
            for name in fx_chains_dict:
                if name in file.split('\\')[-1].lower():
                    track.add_fx(fx_chains_dict[name])
                    track.set_info_string('P_NAME', name.upper())


def split(project: reapy.Project) -> None:
    """Функция для разделения дорог на айтемы"""
    RPR.SetMediaItemSelected(project.items[0].id, False)
    reapy.perform_action(40760)
    hwnd = win32gui.FindWindow(
        '#32770',
        'Dynamic split items'
    )
    win32gui.ShowWindow(hwnd, 0)
    split = win32gui.GetDlgItem(hwnd, 1)
    if split != 0:
        status = win32gui.IsWindowEnabled(split)
    while not status:
        time.sleep(1)
        status = win32gui.IsWindowEnabled(split)
    win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 1, 0)


def hide_window():
    hwnd = win32gui.FindWindow(
        '#32770', 'SWS/BR - Normalizing loudness...'
    )
    while not hwnd:
        time.sleep(0.1)
        hwnd = win32gui.FindWindow(
            '#32770', 'SWS/BR - Normalizing loudness...'
        )
    win32gui.ShowWindow(hwnd, 0)  # 0 полностью, 2 свернуть


def normalize_all(command: int, project: reapy.Project) -> None:
    """Функция для нормализации всего по громкости"""
    project.select_all_items()
    reapy.perform_action(command)


def normalize_dubbers(command: int, project: reapy.Project) -> None:
    """Функция для нормализации дорог по громкости"""
    project.select_all_items()
    RPR.SetMediaItemSelected(project.items[0].id, False)
    reapy.perform_action(command)


def normalize_video(command: int, project: reapy.Project) -> None:
    """Функция для нормализации видео по громкости"""
    project.select_all_items(False)
    RPR.SetMediaItemSelected(project.items[0].id, True)
    reapy.perform_action(command)


def hidden_normalize(project: reapy.Project) -> None:
    command = RPR.NamedCommandLookup(
            '_BR_NORMALIZE_LOUDNESS_ITEMS23'
        )
    if get_option('normalize'):
        norm = mp.Process(
            target=normalize_all,
            args=(command, project)
        )
        hide = mp.Process(target=hide_window)
        norm.start()
        hide.start()
        norm.join()
        hide.join()
    if get_option('normalize_dubbers'):
        norm = mp.Process(
            target=normalize_dubbers,
            args=(command, project)
        )
        hide = mp.Process(target=hide_window)
        norm.start()
        hide.start()
        norm.join()
        hide.join()
    if get_option('normalize_video'):
        norm = mp.Process(
            target=normalize_video,
            args=(command, project)
        )
        hide = mp.Process(target=hide_window)
        norm.start()
        hide.start()
        norm.join()
        hide.join()


def subs_generator(
        project: reapy.Project,
        sbttls: pysubs2.SSAFile,
        strt_idx: int,
        end_idx: int,
        flag: str
        ) -> None:
    for i in range(strt_idx, end_idx):
        try:
            start = sbttls[i].start / 1000
            end = sbttls[i].end / 1000
            if flag == 'region':
                project.add_region(
                    start, end, sbttls[i].text, (147, 112, 219)
                )
            elif flag == 'item':
                item = project.tracks[1].add_item(start, end)
                RPR.ULT_SetMediaItemNote(item.id, sbttls[i].text)
        except IndexError:
            break


def import_subs(
        sbttls: pysubs2.SSAFile,
        project: reapy.Project,
        step: int,
        flag: str,
        strt_idx: int,
        end_idx: int
        ) -> None:
    if strt_idx >= len(sbttls):
        pass
    else:
        subs_gen = (
            mp.Process(
                target=subs_generator,
                args=(
                    project, sbttls, strt_idx, end_idx,
                    flag
                )
            )
        )
        subs_gen.start()
        import_subs(sbttls, project, step, flag, end_idx, (end_idx + step))
        subs_gen.join()


def list_generator(
        position: int,
        strt_idx: int,
        end_idx: int,
        list: List[List[float]],
        queue: mp.Queue
        ) -> None:
    """Функция для создания списка айтемов/субтитров"""
    for i in range(strt_idx, end_idx):
        item = RPR.GetMediaItem(0, i)
        start = RPR.GetMediaItemInfo_Value(
            item,
            'D_POSITION'
        )
        end = start + RPR.GetMediaItemInfo_Value(
            item,
            'D_LENGTH'
        )
        list[position] = [start, end]
        position += 1
    queue.put(list)


def fix_check(project: reapy.Project, subs: List[str]) -> None:
    """Функция для проверки на пропуски и наложения"""
    dbbl_sbs = {}
    subs_list = []
    if subs:
        sbttls = pysubs2.load(subs[0])
        pattern = '- '
        subs_enum = len(sbttls)
        subs_list = [[float] * 2] * subs_enum
        position = 0
        for i, sub in enumerate(sbttls):
            start = sub.start / 1000
            end = sub.end / 1000
            subs_list[position] = [start, end]
            if pattern in sub.text.lower():
                dbbl_sbs[i] = [(sub.start / 1000), (sub.end / 1000), 0]
            position += 1
    items_enum = project.n_items
    sub_items_enum = project.tracks[1].n_items
    voice_items = items_enum - sub_items_enum - 1
    items_mid = voice_items // 2
    items_list_1 = [[float] * 2] * items_mid
    items_list_2 = [[float] * 2] * (voice_items - items_mid)
    queue_1 = mp.Queue()
    queue_2 = mp.Queue()
    items_list_gen_1 = mp.Process(
        target=list_generator,
        args=(0, (sub_items_enum + 1), (sub_items_enum + 1 + items_mid),
              items_list_1, queue_1)
    )
    items_list_gen_2 = mp.Process(
        target=list_generator,
        args=(0, (sub_items_enum + 1 + items_mid), items_enum,
              items_list_2, queue_2)
    )
    items_list_gen_1.start()
    items_list_gen_2.start()
    items_list_1 = queue_1.get()
    items_list_2 = queue_2.get()
    items_list = list(items_list_1 + items_list_2)
    items_list_gen_1.join()
    items_list_gen_2.join()
    checked_subs = []
    dubbles_items = []
    for s in subs_list:
        lenght = s[1] - s[0]
        for i in items_list:
            middle = i[0] + ((i[1] - i[0]) / 2)
            if i[0] >= s[0] and i[1] <= s[1]:
                checked_subs.append(s)
                break
            elif i[0] <= s[0] and i[1] >= s[1]:
                checked_subs.append(s)
                break
            elif i[0] < s[0] and (
                    i[1] > s[0] and i[1] < s[1]
                    ):
                if i[1] - s[0] >= lenght / 2.2:
                    checked_subs.append(s)
                    break
                elif s[0] < middle < s[1]:
                    checked_subs.append(s)
                    break
            elif i[0] > s[0] and (
                    i[0] < s[1] and i[1] > s[1]
                    ):
                if s[1] - i[0] >= lenght / 2.2:
                    checked_subs.append(s)
                    break
                elif s[0] < middle < s[1]:
                    checked_subs.append(s)
                    break
    for i in items_list:
        if i not in dubbles_items:
            middle = i[0] + ((i[1] - i[0]) / 2)
            for j in items_list:
                if j != i and j not in dubbles_items:
                    if j[0] <= middle <= j[1]:
                        project.add_marker(j[0], 'DUBBLE', (128, 255, 255))
                        dubbles_items.append(j)
    for s in subs_list:
        if s not in checked_subs:
            project.add_marker(s[0], 'FIX', (255, 0, 255))
    for s in dbbl_sbs:
        lenght = dbbl_sbs[s][1] - dbbl_sbs[s][0]
        for i in items_list:
            middle = i[0] + ((i[1] - i[0]) / 2)
            if i[0] >= dbbl_sbs[s][0] and i[1] <= dbbl_sbs[s][1]:
                dbbl_sbs[s][2] += 1
            elif i[0] <= dbbl_sbs[s][0] and i[1] >= dbbl_sbs[s][1]:
                dbbl_sbs[s][2] += 1
            elif i[0] < dbbl_sbs[s][0] and (
                    i[1] > dbbl_sbs[s][0] and i[1] < dbbl_sbs[s][1]
                    ):
                if dbbl_sbs[s][0] < middle < dbbl_sbs[s][1]:
                    dbbl_sbs[s][2] += 1
                elif i[1] - dbbl_sbs[s][0] >= lenght / 3.3:
                    dbbl_sbs[s][2] += 1
            elif i[0] > dbbl_sbs[s][0] and (
                    i[0] < dbbl_sbs[s][1] and i[1] > dbbl_sbs[s][1]
                    ):
                if dbbl_sbs[s][0] < middle < dbbl_sbs[s][1]:
                    dbbl_sbs[s][2] += 1
                elif dbbl_sbs[s][1] - i[0] >= lenght / 3.3:
                    dbbl_sbs[s][2] += 1
    for s in dbbl_sbs:
        if dbbl_sbs[s][2] < 2:
            project.add_marker(dbbl_sbs[s][0], 'DUBBLE HERE', (255, 255, 0))


def project_save(
        folder: str,
        title: str,
        number: str,
        project_path: str
        ) -> str:
    """Функция для сохранения проекта"""
    new_path = f'{folder}/{title} {number}.rpp'
    copy = ''
    while os.path.exists(new_path):
        copy += '_copy'
        new_path = f'{folder}/{title} {number}{copy}.rpp'
    shutil.copy(project_path, new_path)
    return new_path


def render(folder: str) -> str:
    """Функция для рендеринга файла"""
    reapy.perform_action(40015)
    folder = os.path.normpath(folder)
    hwnd = win32gui.FindWindow('#32770', 'Render to File')
    while not hwnd:
        time.sleep(0.1)
        hwnd = win32gui.FindWindow('#32770', 'Render to File')
    child_hwnd = win32gui.FindWindowEx(hwnd, None, 'Static', 'File name:')
    file_name_hwnd = win32gui.GetWindow(child_hwnd, win32con.GW_HWNDNEXT)
    file_name_buffer = ctypes.create_unicode_buffer('audio')
    win32gui.SendMessage(
        file_name_hwnd, win32con.WM_SETTEXT, None, file_name_buffer
    )
    child_hwnd = win32gui.FindWindowEx(hwnd, None, 'Static', 'Directory:')
    directory_hwnd = win32gui.GetWindow(child_hwnd, win32con.GW_HWNDNEXT)
    directory_buffer = ctypes.create_unicode_buffer(folder)
    win32gui.SendMessage(
        directory_hwnd, win32con.WM_SETTEXT, None, directory_buffer
    )
    render = win32gui.GetDlgItem(hwnd, 1)
    win32gui.SendMessage(render, win32con.BM_CLICK, 0, 0)
    output_file = os.path.normpath(get_path_to_files(folder, 'audio.*')[0])
    return output_file


def back_up(project: reapy.Project, new_path: str) -> None:
    back_up_path = os.path.splitext(new_path)[-2]
    back_up_path += '_back_up.rpp'
    copy = ''
    while os.path.exists(back_up_path):
        copy += '_copy'
        back_up_path = f'{back_up_path}_back_up{copy}.rpp'
    RPR.Main_SaveProjectEx(project, back_up_path, 0)


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
    folder = path_choice('folder')
    if folder:
        buttons_freeze(master, BUTTONS)
    subs, audio, video, title, number, ext = file_works(folder)
    if audio and video:
        master.iconify()
        new_path = project_save(folder, title, number, project_path)
        hwnd = win32gui.FindWindow('REAPERwnd', None)
        win32gui.ShowWindow(hwnd, 2)
        reapy.open_project(new_path, in_new_tab=True)
        unsaved = reapy.Project(0)
        if unsaved.name == '' and unsaved.n_tracks == 0:
            unsaved.close()
        project = reapy.Project()
        RPR.MoveEditCursor(- project.cursor_position, False)
        audio_select(audio)
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
            output_file = render(folder)
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


def on_save_click(checkboxes: Dict, master: tkinter.Tk, BUTTONS: List):
    thread = Thread(target=reaper_main, args=(checkboxes, master, BUTTONS))
    thread.start()


def on_fix_check_click(master: tkinter.Tk, BUTTONS: List):
    thread = Thread(target=fix_checker, args=(master, BUTTONS))
    thread.start()


def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, path)


master = tkinter.Tk()
width = 380
height = 410
s_width = master.winfo_screenwidth()
s_height = master.winfo_screenheight()
upper = s_height // 8
x = (s_width - width) // 2
y = (s_height - height) // 2
master.geometry(f'{width}x{height}+{x}+{y - upper}')
master.resizable(width=False, height=False)
master.title('REAPERSCRIPT v3.09')
master.iconbitmap(default=resource_path('ico.ico'))
img = Image.open(resource_path('background.png'))
tk_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(master, image=tk_img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
master.protocol('WM_DELETE_WINDOW', on_closing)
OPTIONS = [
    'split',
    'normalize',
    'normalize_dubbers',
    'normalize_video',
    'volume_up_dubbers',
    'sub_item',
    'sub_region',
    'subs_cleaner',
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
]
start_bttn = ttk.Button(
    master,
    text='START',
    name='start',
    command=lambda: on_save_click(checkboxes, master, BUTTONS)
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
help_btn = ttk.Button(
    master,
    text='HELP',
    name='help',
    command=lambda: show_help_window(master),
)
help_btn.place(relx=0.5, rely=1.0, anchor="s", x=145, y=-377)
ToolTip(help_btn, HELP_DICT['help'], 1)

# Чтобы Reaper API подгрузился, Reaper должен быть включен при запуске скрипта
if __name__ == '__main__':
    freeze_support()
    is_reaper_run()
    master.focus_force()
    master.mainloop()
