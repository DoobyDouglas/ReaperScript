# Команду ниже нужно ввести один раз в консоли с включенным Reaper.
# python -c "import reapy; reapy.configure_reaper()"

import ffmpeg
import asstosrt
import pyperclip
import keyboard
import pysubs2
import re
import subprocess
import time
import os
import shutil
import glob
import ctypes
import configparser
import reapy
import tkinter
import tkinter.messagebox
import multiprocessing as mp
from typing import List, Tuple, Dict
from reapy import reascript_api as RPR
from tkinter import filedialog
from multiprocessing import freeze_support
from PIL import Image, ImageTk


def get_config() -> configparser.ConfigParser:
    """Функция для создания/получения файла конфигураций"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def save_options(
        checkboxes: Dict[str, str],
        master: tkinter.Tk,
        config: configparser.ConfigParser,
        text_input: tkinter.Entry
        ) -> None:
    """Функция для сохранения конфигураций"""
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    config['OUTPUT']['audio_output_format'] = text_input.get()
    with open('config.ini', 'w') as config_file:
        config.write(config_file)
    master.destroy()


def create_widgets(
        OPTIONS: list,
        master: tkinter.Tk,
        config: configparser.ConfigParser
        ) -> None:
    """Функция для создания списка конфигураций"""
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
        command=lambda: save_options(checkboxes, master, config, text_input)
    )
    save_button.place(relx=0.5, rely=1.0, anchor="s", y=-9)
    master.mainloop()


def checkbox_window() -> None:
    """Функция для создания окна выбора конфигураций"""
    master = tkinter.Tk()
    master.geometry('380x390')
    master.resizable(width=False, height=False)
    master.title('Выберите нужные опции')
    img = Image.open("background.png")
    tk_img = ImageTk.PhotoImage(img)
    background_label = tkinter.Label(master, image=tk_img)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
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
    create_widgets(OPTIONS, master, config)


def save_path_to_config(name: str, path: str) -> None:
    """Функция для сохранения пути в файл конфигурации"""
    config = get_config()
    if 'PATHS' not in config:
        config['PATHS'] = {}
    config['PATHS'][name] = path
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def load_path_from_config(name: str) -> str or None:
    """Функция для загрузки пути из файла конфигурации"""
    config = get_config()
    try:
        path = config['PATHS'][name]
    except KeyError:
        path = None
    return path


def get_value(name: str) -> str or bool:
    """Функция для загрузки значения из файла конфигурации"""
    config = get_config()
    if name == 'audio_output_format':
        return config['OUTPUT'][name]
    else:
        return config['OPTIONS'].getboolean(name)


def reaper_check() -> None:
    """Функция для создания путей к компонентам REAPER"""
    reaper_path = load_path_from_config('reaper_path')
    if not reaper_path:
        reaper_path = filedialog.askopenfilename(
            title='Выберите файл reaper.exe'
        )
        save_path_to_config('reaper_path', reaper_path)
    project_path = load_path_from_config('project_path')
    if not project_path:
        project_path = filedialog.askopenfilename(
            title='Выберите файл шаблона проекта REAPER'
        )
        save_path_to_config('project_path', project_path)
    fx_chains_folder = load_path_from_config('fx_chains_folder')
    if not fx_chains_folder:
        fx_chains_folder = filedialog.askdirectory(
            title='Выберите папку с цепями эффектов'
        )
        save_path_to_config('fx_chains_folder', fx_chains_folder)


def get_path_to_files(folder: str, extension: str) -> List[str]:
    """Функция для получения пути к файлу"""
    return glob.glob(os.path.join(folder, extension))


def subs_rename(folder: str, subs: List[str]) -> List[str]:
    """Функция для изменения имени субтитров"""
    filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
    s_number = os.path.basename(folder)
    os.rename(subs[0], filenamae + '/' + s_number + '.srt')
    subs = get_path_to_files(folder, '*.srt')
    return subs


def subs_extract(
        folder: str, mkv_video: List[str], param: str, mapping: str
        ) -> None:
    """Функция для извлечения субтитров из видео"""
    video_path = mkv_video[0].replace('\\', '/')
    input_file = ffmpeg.input(video_path)
    output_file = f'{folder}/subs.{param}'
    output = ffmpeg.output(input_file, output_file, map=mapping)
    ffmpeg.run(output)


def ass_sub_convert(folder: str, subs: List[str]) -> None:
    """Функция для конвертирования ass субтитров"""
    with open(subs[0], 'r', encoding='utf-8') as ass_file:
        srt_sub = asstosrt.convert(ass_file)
    with open(f'{folder}/subs.srt', 'w', encoding='utf-8') as srt_file:
        srt_file.write(srt_sub)


def vtt_sub_convert(folder: str, subs: List[str]) -> None:
    """Функция для конвертирования vtt субтитров"""
    filename = os.path.splitext(subs[0])[0].split('\\')[-2]
    os.rename(subs[0], filename + '/' + 'subs.vtt')
    subs = get_path_to_files(folder, '*.vtt')
    subs_path = subs[0].replace('\\', '/')
    input_file = ffmpeg.input(subs_path)
    output_file = f'{folder}/subs.srt'
    output = ffmpeg.output(input_file, output_file)
    ffmpeg.run(output)


def video_rename(folder: str, video: List[str]) -> List[str]:
    """Функция для изменения имени видео"""
    title = folder.split('/')[-2]
    video_type = video[0].split('.')[-1]
    filename = os.path.splitext(video[0])[0].split('\\')[-2]
    s_number = os.path.basename(folder)
    if video_type == 'mkv':
        os.rename(video[0], filename + '/' + title + f'_{s_number}' + '.mkv')
        video = get_path_to_files(folder, '*.mkv')
    if video_type == 'mp4':
        os.rename(video[0], filename + '/' + title + f'_{s_number}' + '.mp4')
        video = get_path_to_files(folder, '*.mp4')
    return video


def flac_rename(folder: str, flac_audio: List[str]) -> List[str]:
    """Функция для изменения нечитаемых расширений"""
    for file in flac_audio:
        if '.reapeaks' not in file.lower():
            try:
                filename = os.path.splitext(file)[0]
                os.rename(file, filename + '.flac')
            except FileExistsError:
                reapy.print('Файл уже существует')  # Добавить while
                raise SystemExit
            except PermissionError:
                reapy.print('Файл используется')  # заменить на окно
                raise SystemExit
    fixed_flac = get_path_to_files(folder, '*.flac')
    return fixed_flac


def comparator(sub: str) -> bool:
    """Функция для проверки субтитра"""
    if (
        (
            'text' in sub
            or 'sign' in sub
            or 'надпись' in sub
            or 'caption' in sub
            or 'title' in sub
            or 'song' in sub
            or 'screen' in sub
            or 'typedigital' in sub
        ) and 'subtitle' not in sub
    ):
        return True
    return False


def subs_edit(subs: List[str], flag: str) -> None:
    """Функция для удаления из субтитров надписей и песен"""
    subtitles = pysubs2.load(subs[0])
    if flag == 'srt':
        pattern_1 = r'\((.*?)\)'
        pattern_2 = r'\[.*?]$'
        pattern_3 = '♫'
        pattern_4 = '♪'
        to_delete = [
            i for i, line in enumerate(subtitles) if (
                re.match(pattern_1, line.text)
                or re.match(pattern_2, line.text)
                or pattern_3 in line.text
                or pattern_4 in line.text
            )
        ]
    elif flag == 'ass':
        to_delete = []
        search_char = '{'
        if subtitles.events[0].name and subtitles.events[0].style:
            for i, sub in enumerate(subtitles.events):
                if (
                    comparator(sub.name.lower())
                    or comparator(sub.style.lower())
                ) and search_char in sub.text:
                    to_delete.append(i)
        elif subtitles.events[0].name:
            for i, sub in enumerate(subtitles.events):
                if comparator(sub.name.lower()) and search_char in sub.text:
                    to_delete.append(i)
        elif subtitles.events[0].style:
            for i, sub in enumerate(subtitles.events):
                if comparator(sub.style.lower()) and search_char in sub.text:
                    to_delete.append(i)
        else:
            return
    for i in reversed(to_delete):
        del subtitles[i]
    subtitles.save(subs[0])


def file_works(folder: str) -> (
        Tuple[List[str], List[str], List[str], List[str], List[str]]
        ):
    """Функция для подготовки файлов к работе"""
    flac_audio = get_path_to_files(folder, '*.flac*')
    if flac_audio:
        flac_audio = flac_rename(folder, flac_audio)
    wav_audio = get_path_to_files(folder, '*.wav')
    mkv_video = get_path_to_files(folder, '*.mkv')
    if mkv_video:
        mkv_video = video_rename(folder, mkv_video)
    mp4_video = get_path_to_files(folder, '*.mp4')
    if mp4_video:
        mp4_video = video_rename(folder, mp4_video)
    subs = get_path_to_files(folder, '*.srt')
    if subs:
        subs = subs_rename(folder, subs)
        subs_edit(subs, 'srt')
    else:
        ass_subs = get_path_to_files(folder, '*.ass')
        if not ass_subs:
            if mkv_video:
                subs_extract(folder, mkv_video, 'ass', '0:s:m:language:eng')
                ass_subs = get_path_to_files(folder, '*.ass')
                if not ass_subs:
                    subs_extract(folder, mkv_video, 'ass', '0:s:m:language:?')
                    ass_subs = get_path_to_files(folder, '*.ass')
        if ass_subs:
            subs_edit(ass_subs, 'ass')
            ass_sub_convert(folder, ass_subs)
        vtt_subs = get_path_to_files(folder, '*.vtt')
        if vtt_subs:
            vtt_sub_convert(folder, vtt_subs)
        srt_subs = get_path_to_files(folder, '*.srt')
        if srt_subs:
            subs = subs_rename(folder, srt_subs)
            subs_edit(subs, 'srt')
        else:
            try:
                if mkv_video:
                    subs_extract(folder, mkv_video, 'srt', '0:s:m:language:?')
                    subs = get_path_to_files(folder, '*.srt')
                    subs = subs_rename(folder, subs)
                    subs_edit(subs, 'srt')
            except IndexError:
                pass
    return flac_audio, wav_audio, mkv_video, mp4_video, subs


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
    fx_chains_folder = load_path_from_config('fx_chains_folder')
    fx_chains = get_path_to_files(fx_chains_folder, '*.RfxChain')
    for chain in fx_chains:
        fx_chain_name = chain.split('\\')[-1]
        dubber_name = fx_chain_name.split('.')[-2].lower()
        fx_dict[dubber_name] = fx_chain_name
    return fx_dict


def video_select(
        mkv_video: List[str],
        mp4_video: List[str],
        ) -> None:
    """Функция для добавления видео"""
    if mkv_video and mp4_video:
        tkinter.messagebox.showinfo(
            'Разные видео',
            'В рабочей папке есть несколько видео разного формата'
        )
        raise SystemExit
    if mkv_video:
        if len(mkv_video) > 1:
            tkinter.messagebox.showinfo(
                'Много видео',
                'В рабочей папке есть несколько видео одного формата'
            )
            raise SystemExit
        RPR.InsertMedia(mkv_video[0], 512 | 0)
    elif mp4_video:
        if len(mp4_video) > 1:
            tkinter.messagebox.showinfo(
                'Много видео',
                'В рабочей папке есть несколько видео одного формата'
            )
            raise SystemExit
        RPR.InsertMedia(mp4_video[0], 512 | 0)


def volume_up(track) -> None:
    """Функция для увеличения исходной громкости дорог"""
    value = get_value('volume_up_dubbers')
    if value:
        item = RPR.GetTrackMediaItem(track, 0)
        RPR.SetMediaItemInfo_Value(item, 'D_VOL', 1.5)


def audio_select(
        flac_audio: List[str],
        wav_audio: List[str]
        ) -> None:
    """Функция для добавления аудио"""
    fx_chains_dict = get_fx_chains()
    for file in flac_audio:
        RPR.InsertMedia(file, 1)
        track = RPR.GetLastTouchedTrack()
        for name in fx_chains_dict:
            if name in file.split('\\')[-1].lower():
                RPR.TrackFX_AddByName(track, fx_chains_dict[name], 0, -1)
                RPR.GetSetMediaTrackInfo_String(
                    track, 'P_NAME', name.upper(), True
                )
        volume_up(track)
    for file in wav_audio:
        RPR.InsertMedia(file, 1)
        track = RPR.GetLastTouchedTrack()
        for name in fx_chains_dict:
            if name in file.split('\\')[-1].lower():
                RPR.TrackFX_AddByName(track, fx_chains_dict[name], 0, -1)
                RPR.GetSetMediaTrackInfo_String(
                    track, 'P_NAME', name.upper(), True
                )
        volume_up(track)
    if not flac_audio and not wav_audio:  # Заменить на окно
        reapy.print('В рабочей папке нет аудио, подходящего формата')
        raise SystemExit


# Использует послендий пресет сплита
def split(video_item: str) -> None:
    """Функция для разделения дорог на айтемы"""
    value = get_value('split')
    if value:
        RPR.SelectAllMediaItems(0, True)
        RPR.SetMediaItemSelected(video_item, False)
        RPR.Main_OnCommand(40760, 0)
        hwnd = ctypes.windll.user32.FindWindowW(
            '#32770',
            'Dynamic split items'
        )
        button_id = 1
        button_hwnd = ctypes.windll.user32.GetDlgItem(hwnd, button_id)
        if button_hwnd != 0:
            button_status = ctypes.windll.user32.IsWindowEnabled(button_hwnd)
        while not button_status:
            time.sleep(1)
            button_status = ctypes.windll.user32.IsWindowEnabled(button_hwnd)
        ctypes.windll.user32.SendMessageW(hwnd, 0x111, 1, 0)


def hide_window():
    hwnd = ctypes.windll.user32.FindWindowW(
        '#32770', 'SWS/BR - Normalizing loudness...'
    )
    while not hwnd:
        time.sleep(0.1)
        hwnd = ctypes.windll.user32.FindWindowW(
            '#32770', 'SWS/BR - Normalizing loudness...'
        )
    ctypes.windll.user32.ShowWindow(hwnd, 0)  # 0 полностью, 2 свернуть


def normalize_all(command: int) -> None:
    """Функция для нормализации всего по громкости"""
    RPR.SelectAllMediaItems(0, True)
    RPR.Main_OnCommand(command, 0)


def normalize_dubbers(command: int, video_item: str) -> None:
    RPR.SelectAllMediaItems(0, True)
    RPR.SetMediaItemSelected(video_item, False)
    RPR.Main_OnCommand(command, 0)


def normalize_video(command: int, video_item: str) -> None:
    RPR.SelectAllMediaItems(0, False)
    RPR.SetMediaItemSelected(video_item, True)
    RPR.Main_OnCommand(command, 0)


def hidden_normalize(video_item: str) -> None:
    normalize = RPR.NamedCommandLookup(
            '_BR_NORMALIZE_LOUDNESS_ITEMS23'
        )
    if get_value('normalize'):
        norm = mp.Process(target=normalize_all, args=(normalize,))
        hide = mp.Process(target=hide_window)
        norm.start()
        hide.start()
        norm.join()
        hide.join()
    if get_value('normalize_dubbers'):
        norm = mp.Process(
            target=normalize_dubbers,
            args=(normalize, video_item)
        )
        hide = mp.Process(target=hide_window)
        norm.start()
        hide.start()
        norm.join()
        hide.join()
    if get_value('normalize_video'):
        norm = mp.Process(
            target=normalize_video,
            args=(normalize, video_item)
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


def import_subs(subs: List[str], project: reapy.Project) -> List[List[float]]:
    if subs and (get_value('sub_region') or get_value('sub_item')):
        sbttls = pysubs2.load(subs[0])
        mid = len(sbttls) // 2
        if get_value('sub_region'):
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
        if get_value('sub_item'):
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
    value = get_value('fix_check')
    if value:
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


def project_save(folder: str) -> str:
    """Функция для сохранения проекта"""
    project_path = load_path_from_config('project_path')
    s_number = os.path.basename(folder)
    title = folder.split('/')[-2]
    project_name = f'{title} {s_number}.rpp'
    new_path = folder + '/' + project_name
    shutil.copy(project_path, new_path)
    return new_path


# Используется последний пресет рендера
def render(folder: str) -> None:
    """Функция для рендеринга файла"""
    value = get_value('render_audio')
    if value:
        RPR.Main_OnCommand(40015, 0)
        time.sleep(1)
        keyboard.write('audio')
        time.sleep(1)
        for _ in range(34):
            keyboard.send('tab')
            time.sleep(0.01)
        render_path = folder.replace('/', '\\') + '\\'
        pyperclip.copy(render_path)
        keyboard.press_and_release('ctrl+v')
        time.sleep(0.5)
        keyboard.send('enter')


def reaper_close(folder: str) -> None:
    """Функция для закрытия REAPER"""
    value = get_value('render_audio')
    if value:
        time.sleep(3)
        audio = f'{folder}/audio.wav'
        old_file_size = os.path.getsize(audio)
        time.sleep(3)
        new_file_size = os.path.getsize(audio)
        while old_file_size < new_file_size:
            old_file_size = os.path.getsize(audio)
            time.sleep(3)
            new_file_size = os.path.getsize(audio)
        time.sleep(3)
        RPR.Main_OnCommand(40004, 0)


def make_episode(
        folder: str,
        mkv_video: List[str],
        mp4_video: List[str]
        ) -> None:
    """Функция для создания видео с озвучкой"""
    value = get_value('render_video')
    ext = get_value('audio_output_format')
    if value and ext:
        title = folder.split('/')[-2]
        s_number = os.path.basename(folder)
        if mkv_video:
            param = 'mkv'
            video_path = mkv_video[0].replace('\\', '/')
        elif mp4_video:
            param = 'mp4'
            video_path = mp4_video[0].replace('\\', '/')
        audio_path = f'{folder}/audio.{ext}'
        output_file = f'{folder}/{title}_{s_number}_DUB.{param}'
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


# Чтобы Reaper API подгрузился он должен быть включен при запуске скрипта
def main():
    """Основная функция"""
    freeze_support()
    checkbox_window()
    tkinter.Tk().withdraw()
    reaper_check()
    folder = choice_folder()
    flac_audio, wav_audio, mkv_video, mp4_video, subs = file_works(folder)
    new_path = project_save(folder)
    reaper_path = load_path_from_config('reaper_path')
    subprocess.run([reaper_path, new_path])
    project = reapy.Project()
    audio_select(flac_audio, wav_audio)
    video_select(mkv_video, mp4_video)
    split(project.items[0].id)
    import_subs(subs, project)
    project.save(False)
    hidden_normalize(project.items[0].id)
    project.save(False)
    fix_check(project)
    render(folder)
    project.save(False)
    reaper_close(folder)
    make_episode(folder, mkv_video, mp4_video)


if __name__ == '__main__':
    main()
