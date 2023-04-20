# Команду ниже нужно ввести один раз в консоли с включенным Reaper.
# python -c "import reapy; reapy.configure_reaper()"
# pyinstaller --onefile --noconsole --hidden-import=asstosrt
from file_works import file_works, get_path_to_files
from multiprocessing import freeze_support
from reapy import reascript_api as RPR
from tkinter import filedialog
from typing import List, Dict
from PIL import Image, ImageTk
from config_works import (
    get_config,
    load_path,
    save_path,
    get_option,
    save_options,
)
import multiprocessing as mp
import tkinter.messagebox
import subprocess
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


def reaper_check() -> None:
    """Функция для создания путей к компонентам REAPER"""
    reaper_path = load_path('reaper_path')
    if not reaper_path:
        reaper_path = filedialog.askopenfilename(
            title='Выберите файл reaper.exe'
        )
        save_path('reaper_path', reaper_path)
    project_path = load_path('project_path')
    if not project_path:
        project_path = filedialog.askopenfilename(
            title='Выберите файл шаблона проекта REAPER'
        )
        save_path('project_path', project_path)
    fx_chains_folder = load_path('fx_chains_folder')
    if not fx_chains_folder:
        fx_chains_folder = filedialog.askdirectory(
            title='Выберите папку с цепями эффектов'
        )
        save_path('fx_chains_folder', fx_chains_folder)


def choice_folder() -> str:
    """Функция для выбора рабочей папки с эпизодом"""
    folder = filedialog.askdirectory(
        title='Выберите рабочую папку с эпизодом'
    )
    return folder


# Если имена состоят из нескольких слов, названия цепей нужно писать через "_"
def get_fx_chains() -> Dict[str, str]:
    """Функция создания словаря из дабберов и названий их цепей эффектов"""
    fx_dict = {}
    fx_chains_folder = load_path('fx_chains_folder')
    fx_chains = get_path_to_files(fx_chains_folder, '*.RfxChain')
    for chain in fx_chains:
        fx_chain_name = chain.split('\\')[-1]
        dubber_name = fx_chain_name.split('.')[-2].lower()
        fx_dict[dubber_name] = fx_chain_name
    return fx_dict


def audio_select(audio: List[str]) -> None:
    """Функция для добавления аудио"""
    fx_chains_dict = get_fx_chains()
    for file in audio:
        RPR.InsertMedia(file, 1)
        track = reapy.get_last_touched_track()
        if get_option('volume_up_dubbers'):
            track.items[0].set_info_value('D_VOL', 1.5)
        for name in fx_chains_dict:
            if name in file.split('\\')[-1].lower():
                track.add_fx(fx_chains_dict[name])
                track.set_info_string('P_NAME', name.upper())


# Использует послендий пресет сплита
def split(project: reapy.Project) -> None:
    """Функция для разделения дорог на айтемы"""
    project.select_all_items()
    RPR.SetMediaItemSelected(project.items[0].id, False)
    reapy.perform_action(40760)
    hwnd = win32gui.FindWindow(
        '#32770',
        'Dynamic split items'
    )
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
    win32gui.ShowWindow(hwnd, 2)  # 0 полностью, 2 свернуть


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
        start = sbttls[i].start / 1000
        end = sbttls[i].end / 1000
        if flag == 'region':
            project.add_region(
                start, end, sbttls[i].text, (147, 112, 219)
            )
        elif flag == 'item':
            item = project.tracks[1].add_item(start, end)
            RPR.ULT_SetMediaItemNote(item.id, sbttls[i].text)


def import_subs(subs: List[str], project: reapy.Project) -> None:
    sbttls = pysubs2.load(subs[0])
    mid = len(sbttls) // 2
    if get_option('sub_region'):
        subs_gen_1 = (
            mp.Process(
                target=subs_generator,
                args=(
                    project, sbttls, 0, mid,
                    'region'
                )
            )
        )
        subs_gen_2 = (
            mp.Process(
                target=subs_generator,
                args=(
                    project, sbttls, mid, len(sbttls),
                    'region'
                )
            )
        )
        subs_gen_1.start()
        subs_gen_2.start()
        subs_gen_1.join()
        subs_gen_2.join()
    if get_option('sub_item'):
        subs_gen_1 = (
            mp.Process(
                target=subs_generator,
                args=(
                    project, sbttls, 0, mid,
                    'item'
                )
            )
        )
        subs_gen_2 = (
            mp.Process(
                target=subs_generator,
                args=(
                    project, sbttls, mid, len(sbttls),
                    'item'
                )
            )
        )
        subs_gen_1.start()
        subs_gen_2.start()
        subs_gen_1.join()
        subs_gen_2.join()


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


def fix_check(project: reapy.Project) -> None:
    """Функция для проверки на пропуски и наложения"""
    if get_option('fix_check'):
        subs_enum = project.tracks[1].n_items
        items_enum = project.n_items
        subs_list = [[float] * 2] * subs_enum
        items_list = [[float] * 2] * (items_enum - subs_enum - 1)
        queue_subs = mp.Queue()
        queue_items = mp.Queue()
        checked_subs = []
        dubbles_items = []
        subs_list_gen = mp.Process(
            target=list_generator,
            args=(0, 1, (subs_enum + 1), subs_list, queue_subs)
        )
        items_list_gen = mp.Process(
            target=list_generator,
            args=(0, (subs_enum + 1), items_enum,
                  items_list, queue_items)
        )
        subs_list_gen.start()
        items_list_gen.start()
        subs_list = queue_subs.get()
        items_list = queue_items.get()
        subs_list_gen.join()
        items_list_gen.join()
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


def project_save(folder: str, title: str, number: str) -> str:
    """Функция для сохранения проекта"""
    project_path = load_path('project_path')
    new_path = f'{folder}/{title} {number}.rpp'
    copy = ''
    while os.path.exists(new_path):
        copy += '_copy'
        new_path = f'{folder}/{title} {number}{copy}.rpp'
    shutil.copy(project_path, new_path)
    return new_path


# Используется последний пресет рендера
def render(folder: str) -> None:
    """Функция для рендеринга файла"""
    if get_option('render_audio'):
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


def back_up(project: reapy.Project, new_path: str) -> None:
    back_up_path = os.path.splitext(new_path)[-2]
    back_up_path += '_back_up.rpp'
    copy = ''
    while os.path.exists(back_up_path):
        copy += '_copy'
        back_up_path = f'{back_up_path}_back_up{copy}.rpp'
    RPR.Main_SaveProjectEx(project, back_up_path, 0)


def reaper_close(folder: str) -> None:
    """Функция для закрытия REAPER"""
    if get_option('render_audio'):
        time.sleep(2)
        audio = f'{folder}/audio.wav'
        old_file_size = os.path.getsize(audio)
        time.sleep(3)
        new_file_size = os.path.getsize(audio)
        while old_file_size < new_file_size:
            old_file_size = os.path.getsize(audio)
            time.sleep(3)
            new_file_size = os.path.getsize(audio)
        time.sleep(2)
        reapy.perform_action(40004)


def make_episode(
        video: List[str],
        folder: str,
        title: str,
        number: str,
        ext: str
        ) -> None:
    """Функция для создания видео с озвучкой"""
    audio_ext = get_option('audio_output_format')
    if get_option('render_video') and ext:
        video_path = video[0].replace('\\', '/')
        audio_path = f'{folder}/audio.{audio_ext}'
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
        text_input: tkinter.Entry
        ) -> None:
    """Основная функция"""
    save_options(checkboxes, text_input)
    reaper_check()
    folder = filedialog.askdirectory(
        title='Выберите рабочую папку с эпизодом'
    )
    subs, audio, video, title, number, ext = file_works(folder)
    if audio and video:
        master.withdraw()
    new_path = project_save(folder, title, number)
    reaper_path = load_path('reaper_path')
    subprocess.run([reaper_path, new_path])
    project = reapy.Project()
    audio_select(audio)
    RPR.InsertMedia(video[0], 512 | 0)
    project.save(False)
    if get_option('split'):
        split(project)
    if subs and (get_option('sub_region') or get_option('sub_item')):
        import_subs(subs, project)
    project.save(False)
    hidden_normalize(project)
    back_up(project, new_path)
    fix_check(project)
    project.save(False)
    render(folder)
    project.save(False)
    reaper_close(folder)
    make_episode(video, folder, title, number, ext)
    master.wm_deiconify()


def on_closing():
    raise SystemExit


master = tkinter.Tk()
width = 380
height = 390
s_width = master.winfo_screenwidth()
s_height = master.winfo_screenheight()
upper = s_height // 8
x = (s_width - width) // 2
y = (s_height - height) // 2
master.geometry(f'{width}x{height}+{x}+{y - upper}')
master.resizable(width=False, height=False)
width = master.winfo_screenwidth()
height = master.winfo_screenheight()
x = (width - 380) // 2
y = (height - 390) // 2
master.title('Выберите нужные опции')
img = Image.open('background.png')
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
    'fix_check',
    'render_audio',
    'render_video',
]
config = get_config()
checkboxes = {}
if 'OPTIONS' not in config:
    config['OPTIONS'] = {}
for i, option in enumerate(OPTIONS):
    var = tkinter.BooleanVar()
    if option in config['OPTIONS']:
        var.set(config['OPTIONS'].getboolean(option))
    else:
        var.set(False)
    checkbox = tkinter.Checkbutton(
        master,
        text=option,
        variable=var,
        background='#ffc0cb',
        bd=3,
        pady=3,
        activebackground='#ffc0cb'
    )
    checkbox.grid(
        row=i,
        column=0,
        sticky=tkinter.W
    )
    checkboxes[option] = var
if 'OUTPUT' not in config:
    config['OUTPUT'] = {}
label = tkinter.Label(
    master,
    text='Audio Output Format:',
    background='#ffc0cb',
)
label.grid(
    row=len(OPTIONS),
    column=0,
    sticky=tkinter.W,
    padx=3,
    pady=3
)
text_input = tkinter.Entry(
    master,
    width=6,
    background='#ffffff',
    bd=3
)
text_input.grid(
    row=len(OPTIONS),
    column=1,
    sticky=tkinter.W,
    padx=3,
    pady=3
    )
if 'audio_output_format' in config['OUTPUT']:
    text_input.insert(tkinter.END, config['OUTPUT']['audio_output_format'])
save_button = tkinter.Button(
    master,
    text='Сохранить',
    background='#9b93b3',
    activebackground='#9b93b3',
    command=lambda: reaper_main(checkboxes, master, text_input)
)
save_button.place(relx=0.5, rely=1.0, anchor="s", y=-9)


# Чтобы Reaper API подгрузился, Reaper должен быть включен при запуске скрипта
if __name__ == '__main__':
    freeze_support()
    master.mainloop()
