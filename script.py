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


def reaper_nun():
    """Функция для запуска REAPER"""
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
    subprocess.run([reaper_path, project_path])


def choice_folder():
    folder = filedialog.askdirectory(title='Выберите рабочую папку с эпизодом')
    files = glob.glob(os.path.join(folder, '*.flac*'))
    mkv_video = glob.glob(os.path.join(folder, '*.mkv'))
    mp4_video = glob.glob(os.path.join(folder, '*.mp4'))
    subs = glob.glob(os.path.join(folder, '*.srt'))
    return folder, files, mkv_video, mp4_video, subs


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
    for file in wav_files:
        RPR.InsertMedia(file, 1)
        track = RPR.GetLastTouchedTrack()
        for name in fx_chains_dict:
            if name in file.split('\\')[-1].lower():
                RPR.TrackFX_AddByName(track, fx_chains_dict[name], 0, -1)
                RPR.GetSetMediaTrackInfo_String(
                    track, 'P_NAME', name.upper(), True
                )
    if not fixed_files and not wav_files:
        reapy.print('В рабочей папке нет аудио, подходящего формата')


def split():
    item = RPR.GetSelectedMediaItem(0, 0)
    RPR.SetMediaItemSelected(item, False)
    RPR.Main_OnCommand(40760, 0)
    time.sleep(10)
    pyautogui.press('enter')
    time.sleep(1)


def normalize():
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
    pyautogui.press('i')
    time.sleep(1)
    fix_path = subs[0].replace('/', '\\')
    pyautogui.typewrite(fix_path)
    pyautogui.press('enter')


def project_save(
        mkv_video: List[str],
        mp4_video: List[str],
        folder: str
        ):
    pyautogui.hotkey('ctrl', 'alt', 's')
    if mkv_video:
        project_name = mkv_video[0].split('\\')[-1].replace('mkv', 'rpp')
        new_porject_path = folder.replace('/', '\\') + '\\' + f'{project_name}'
    elif mp4_video:
        project_name = mp4_video[0].split('\\')[-1].replace('mp4', 'rpp')
        new_porject_path = folder.replace('/', '\\') + '\\' + f'{project_name}'
    time.sleep(1)
    pyautogui.typewrite(new_porject_path)
    pyautogui.press('enter')


def render(folder: str):
    RPR.Main_OnCommand(40015, 0)
    time.sleep(1)
    for i in range(35):
        pyautogui.press('tab')
    render_path = folder.replace('/', '\\') + '\\'
    pyautogui.typewrite(render_path)
    pyautogui.press('enter')
    time.sleep(180)


# Чтобы Reaper API подгрузился он должен быть включен при запуске скрипта
def main():
    """Основная функция создания проекта"""
    tkinter.Tk().withdraw()
    keyboard_check()
    folder, files, mkv_video, mp4_video, subs = choice_folder()
    reaper_nun()
    flac_rename(files)
    audio_select(folder)
    video_select(mkv_video, mp4_video)
    split()
    import_subs(subs)
    project_save(mkv_video, mp4_video, folder)
    normalize()
    project = reapy.Project()
    project.save(False)
    render(folder)
    pyautogui.hotkey('ctrl', 'q')
    time.sleep(1)
    pyautogui.press('enter')


if __name__ == '__main__':
    main()
