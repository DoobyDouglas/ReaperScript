# Команду ниже нужно ввести один раз в консоли с включенным Reaper.
# python -c "import reapy; reapy.configure_reaper()"

import subprocess
import time
import os
import glob
import pyautogui
import configparser
import reapy
import tkinter
import tkinter.messagebox
import py_win_keyboard_layout as pwkl
from typing import List
from reapy import reascript_api as RPR
from tkinter import filedialog


def save_path_to_saved_location(name, path):
    """Функция для сохранения пути в файл конфигурации"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'PATHS' not in config:
        config['PATHS'] = {}
    config['PATHS'][name] = path
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def load_path_from_saved_location(name):
    """Функция для загрузки пути из файла конфигурации"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        path = config['PATHS'][name]
    except KeyError:
        path = None
    return path


# Функция меняет раскладку на нужную сама, но скрипт нужно перезапустить
def keyboard_check():
    """Функция для проверки раскладки клавиатуры"""
    current_layout = pwkl.get_foreground_window_keyboard_layout()
    if current_layout != 67699721:
        pwkl.change_foreground_window_keyboard_layout(0x00000409)
        tkinter.messagebox.showinfo(
            'Неправильная раскладка',
            'Если раскладнка не поменялась сама'
            ' - поменяйте вручную и перезапустите скрипт'
        )
        raise SystemExit


def reaper_check():
    """Функция для создания путей к компонентам REAPER"""
    reaper_path = load_path_from_saved_location('reaper_path')
    if not reaper_path:
        reaper_path = filedialog.askopenfilename(
            title='Выберите файл reaper.exe'
        )
        save_path_to_saved_location('reaper_path', reaper_path)
    project_path = load_path_from_saved_location('project_path')
    if not project_path:
        project_path = filedialog.askopenfilename(
            title='Выберите файл шаблона проекта REAPER'
        )
        save_path_to_saved_location('project_path', project_path)
    fx_chains_folder = load_path_from_saved_location('fx_chains_folder')
    if not fx_chains_folder:
        fx_chains_folder = filedialog.askdirectory(
            title='Выберите папку с цепями эффектов'
        )
    save_path_to_saved_location('fx_chains_folder', fx_chains_folder)


def reaper_nun():
    """Функция для запуска REAPER"""
    reaper_path = load_path_from_saved_location('reaper_path')
    project_path = load_path_from_saved_location('project_path')
    subprocess.run([reaper_path, project_path])


def subs_rename(folder: str, subs: List[str]):
    filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
    s_number = os.path.basename(folder)
    os.rename(subs[0], filenamae + '/' + s_number + '.srt')
    subs = glob.glob(os.path.join(folder, '*.srt'))
    return subs


# Для корректной работы ffmpeg из кода,
# путь до рабочей папки не должен содержать пробелов,
# их можно заменить на "_"
def subs_extract(folder: str, mkv_video: List[str], param: str):
    if param == 'ass':
        command = f'ffmpeg -i {mkv_video[0]} {folder}/subs.ass'
        subprocess.call(command, shell=True)
    if param == 'srt':
        command = f'ffmpeg -i {mkv_video[0]} {folder}/subs.srt'
        subprocess.call(command, shell=True)


def sub_convert(folder: str):
    disk = folder.split(':')[0].lower()
    folder_path = folder.split(':')[1]
    command = f'{disk}: && cd {folder_path} && asstosrt'
    subprocess.call(command, shell=True)


def video_rename(folder: str, video: List[str]):
    title = folder.split('/')[-2]
    video_type = video[0].split('.')[-1]
    filename = os.path.splitext(video[0])[0].split('\\')[-2]
    s_number = os.path.basename(folder)
    if video_type == 'mkv':
        os.rename(video[0], filename + '/' + title + s_number + '.mkv')
        video = glob.glob(os.path.join(folder, '*.mkv'))
    if video_type == 'mp4':
        os.rename(video[0], filename + '/' + title + s_number + '.mp4')
        video = glob.glob(os.path.join(folder, '*.mp4'))
    return video


def file_works(folder: str):
    files = glob.glob(os.path.join(folder, '*.flac*'))
    mkv_video = glob.glob(os.path.join(folder, '*.mkv'))
    if mkv_video:
        mkv_video = video_rename(folder, mkv_video)
        subs_extract(folder, mkv_video, 'ass')
    mp4_video = glob.glob(os.path.join(folder, '*.mp4'))
    if mp4_video:
        mp4_video = video_rename(folder, mp4_video)
    subs = glob.glob(os.path.join(folder, '*.ass'))
    if subs:
        sub_convert(folder)
    subs = glob.glob(os.path.join(folder, '*.srt'))
    if subs:
        subs = subs_rename(folder, subs)
    else:
        try:
            subs_extract(folder, mkv_video, 'srt')
            subs = glob.glob(os.path.join(folder, '*.srt'))
            subs = subs_rename(folder, subs)
        except IndexError:
            pass
    return files, mkv_video, mp4_video, subs


def choice_folder():
    """Функция для выбора рабочей папки с эпизодом"""
    folder = filedialog.askdirectory(
        title='Выберите рабочую папку с эпизодом'
    )
    return folder


def flac_rename(files: List[str]):
    """Функция для изменения нечитаемых расширений"""
    for file in files:
        if '.reapeaks' not in file.lower():
            try:
                filename = os.path.splitext(file)[0]
                os.rename(file, filename + '.flac')
            except FileExistsError:
                reapy.print('Файл уже существует')
                raise SystemExit
            except PermissionError:
                reapy.print('Файл используется')
                raise SystemExit
        else:
            pass


# Если имена состоят из нескольких слов, названия цепей нужно писать через "_"
def get_fx_chains():
    """Функция создания словаря из дабберов и названий их цепей эффектов"""
    fx_dict = {}
    fx_chains_folder = load_path_from_saved_location('fx_chains_folder')
    fx_chains = glob.glob(os.path.join(fx_chains_folder, '*.RfxChain'))
    for chain in fx_chains:
        fx_chain_name = chain.split('\\')[-1]
        dubber_name = fx_chain_name.split('.')[-2].lower()
        fx_dict[dubber_name] = fx_chain_name
    return fx_dict


def video_select(
        mkv_video: List[str],
        mp4_video: List[str],
        ):
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
        RPR.InsertMedia(mkv_video[0], (1 << 9) | 0)
    elif mp4_video:
        if len(mp4_video) > 1:
            tkinter.messagebox.showinfo(
                'Много видео',
                'В рабочей папке есть несколько видео одного формата'
            )
            raise SystemExit
        RPR.InsertMedia(mp4_video[0], (1 << 9) | 0)


# Полезно, если используется сплит,
# в остальных случаях лучше закомментировать 2 раза ниже в коде
def volume_up(track):
    """Функция для увеличения исходной громкости дорог"""
    item = RPR.GetTrackMediaItem(track, 0)
    RPR.SetMediaItemInfo_Value(item, 'D_VOL', 2.82)


def audio_select(folder: str):
    """Функция для добавления аудио"""
    fx_chains_dict = get_fx_chains()
    fixed_files = glob.glob(os.path.join(folder, '*.flac'))
    wav_files = glob.glob(os.path.join(folder, '*.wav'))
    for file in fixed_files:
        RPR.InsertMedia(file, 1)
        track = RPR.GetLastTouchedTrack()
        for name in fx_chains_dict:
            if name in file.split('\\')[-1].lower():
                RPR.TrackFX_AddByName(track, fx_chains_dict[name], 0, -1)
                RPR.GetSetMediaTrackInfo_String(
                    track, 'P_NAME', name.upper(), True
                )
        volume_up(track)  # Первый раз
    for file in wav_files:
        RPR.InsertMedia(file, 1)
        track = RPR.GetLastTouchedTrack()
        for name in fx_chains_dict:
            if name in file.split('\\')[-1].lower():
                RPR.TrackFX_AddByName(track, fx_chains_dict[name], 0, -1)
                RPR.GetSetMediaTrackInfo_String(
                    track, 'P_NAME', name.upper(), True
                )
        volume_up(track)  # Второй раз
    if not fixed_files and not wav_files:
        reapy.print('В рабочей папке нет аудио, подходящего формата')
        raise SystemExit


# Можно дать больше времени на работу сплита, если увеличить значение X_FILE
def get_info_values():
    """Функция для получения значений видео и сна"""
    X_FILE = 5
    video_item = RPR.GetSelectedMediaItem(0, 0)
    all_tracks = RPR.GetNumTracks()
    dub_tracks = all_tracks - 2
    split_sleep = dub_tracks * X_FILE
    return video_item, split_sleep


# Использует послендий пресет сплита
def split(video_item, split_sleep):
    """Функция для разделения дорог на айтемы"""
    RPR.SetMediaItemSelected(video_item, False)
    RPR.Main_OnCommand(40760, 0)
    time.sleep(split_sleep)
    pyautogui.press('enter')
    time.sleep(1)


def normalize():
    """Функция для нормализации айтемов по громкости"""
    RPR.SelectAllMediaItems(0, True)
    normalize_loudness = RPR.NamedCommandLookup(
        '_BR_NORMALIZE_LOUDNESS_ITEMS23'
    )
    RPR.Main_OnCommand(normalize_loudness, 0)


# Чтобы функция работала корректно,
# нужно повесить метод загрузки субтитров на шорткат, например "i"
# Важно переключиться на EN раскладку, иначе шорткаты не сработают
# и все пути к рабочей папке должны быть на английском
def import_subs(subs: List[str]):
    """Функция для добавления субтитров"""
    if len(subs) > 1:
        tkinter.messagebox.showinfo(
                'Много Субтитров',
                'В рабочей папке есть несколько субтитров. Выберите вручную'
            )
        manual_import = RPR.NamedCommandLookup('_S&M_IMPORT_SUBTITLE')
        RPR.Main_OnCommand(manual_import, 0)
    else:
        try:
            if subs[0]:
                pyautogui.press('i')
                time.sleep(1)
                fix_path = subs[0].replace('/', '\\')
                pyautogui.typewrite(fix_path)
                pyautogui.press('enter')
        except IndexError:
            pass


# В качестве имени сессии использует имя видео
def project_save(folder: str):
    """Функция для сохранения проекта"""
    s_number = os.path.basename(folder)
    title = folder.split('/')[-2]
    project_name = f'{title} {s_number}'
    new_porject_path = folder.replace('/', '\\') + '\\' + f'{project_name}'
    pyautogui.hotkey('ctrl', 'alt', 's')
    time.sleep(1)
    pyautogui.typewrite(new_porject_path)
    pyautogui.press('enter')


# Используется последний пресет рендера
def render(folder: str):
    """Функция для рендеринга файла"""
    RPR.Main_OnCommand(40015, 0)
    time.sleep(1)
    for i in range(35):
        pyautogui.press('tab')
    render_path = folder.replace('/', '\\') + '\\'
    pyautogui.typewrite(render_path)
    pyautogui.press('enter')


# Чтобы Reaper API подгрузился он должен быть включен при запуске скрипта
def main():
    """Основная функция создания проекта"""
    tkinter.Tk().withdraw()
    keyboard_check()
    reaper_check()
    folder = choice_folder()
    files, mkv_video, mp4_video, subs = file_works(folder)
    reaper_nun()
    flac_rename(files)
    project = reapy.Project()
    audio_select(folder)
    video_select(mkv_video, mp4_video)
    video_item, split_sleep = get_info_values()
    split(video_item, split_sleep)
    import_subs(subs)
    project_save(folder)
    normalize()
    project.save(False)
    render(folder)  # Эту функцию можно закомментировать или удалить


if __name__ == '__main__':
    main()
