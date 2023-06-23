from reapy import reascript_api as RPR
from config_works import get_option, load_path
from file_works import get_fx_chains, glob_path
from typing import List
import multiprocessing as mp
import win32con
import win32gui
import pysubs2
import ctypes
import shutil
import reapy
import time
import re
import os
from threading import Thread


def create_project(new_path: str) -> reapy.Project:
    reapy.open_project(new_path, in_new_tab=True)
    unsaved = reapy.Project(0)
    if unsaved.name == '' and unsaved.n_tracks == 0:
        unsaved.close()
    project = reapy.Project()
    RPR.MoveEditCursor(- project.cursor_position, False)
    return project


def audio_select(audio: List[str], flag: str) -> None:
    """Функция для добавления аудио"""
    fx_chains_dict = get_fx_chains()
    for file in audio:
        RPR.InsertMedia(file, 1)
        track = reapy.get_last_touched_track()
        filename = os.path.splitext(file.split('\\')[-1])[0].replace(' ', '_')
        if get_option('volume_up_dubbers') and flag == 'main':
            track.items[0].set_info_value('D_VOL', 1.5)
        if fx_chains_dict:
            for name in fx_chains_dict:
                search_name = name.replace(' ', '_')
                if re.findall(rf'_{search_name}_', f'_{filename.lower()}_'):
                    if flag == 'main':
                        track.add_fx(fx_chains_dict[name])
                    track.set_info_string('P_NAME', name.upper())
        if flag == 'de_noize':
            max_peak = RPR.NF_AnalyzeTakeLoudness2(
                track.items[0].takes[0].id,
                False, 0, 0, 0, 0, 0, 0, 0, 0
            )[8]
            track.items[0].set_info_value('D_VOL', max_peak / -13)


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


def normalize_loudness(
        command: int,
        project: reapy.Project,
        flag: str
        ) -> None:
    """Функция для нормализации громкости"""
    if flag == 'all' or flag == 'dubbers':
        select_all = True
    else:
        select_all = False
    if flag == 'dubbers':
        select_item = False
    elif flag == 'video':
        select_item = True
    project.select_all_items(select_all)
    if flag == 'video' or flag == 'dubbers':
        RPR.SetMediaItemSelected(project.items[0].id, select_item)
    reapy.perform_action(command)


def normalize(project: reapy.Project, flag: str) -> None:
    command = RPR.NamedCommandLookup(
            '_BR_NORMALIZE_LOUDNESS_ITEMS23'
        )
    clsname, title = '#32770', 'SWS/BR - Normalizing loudness...'
    norm = mp.Process(
        target=normalize_loudness,
        args=(command, project, flag)
    )
    hide = mp.Process(
        target=hide_window,
        args=(clsname, title, 'normalize')
    )
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
                # RPR.NF_SetSWSMarkerRegionSub(sbttls[i].text, region.index)
                # Странно себя ведёт в потоке
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
                    project,
                    sbttls,
                    strt_idx,
                    end_idx,
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
    """Функция для создания списка айтемов"""
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
        project_path: str,
        flag: str,
        title: str = None,
        number: str = None,
        ) -> str:
    """Функция для сохранения проекта"""
    if flag == 'main':
        name = f'{title} {number}'
    elif flag == 'de_noize':
        name = 'De_NoIze'
    new_path = f'{folder}/{name}.rpp'
    copy = ''
    while os.path.exists(new_path):
        copy += '_copy'
        new_path = f'{folder}/{name}{copy}.rpp'
    shutil.copy(project_path, new_path)
    return new_path


def back_up(project: reapy.Project, new_path: str) -> None:
    back_up_path = os.path.splitext(new_path)[-2]
    back_up_path += '_back_up.rpp'
    copy = ''
    while os.path.exists(back_up_path):
        copy += '_copy'
        back_up_path = f'{back_up_path}_back_up{copy}.rpp'
    RPR.Main_SaveProjectEx(project, back_up_path, 0)


def render(folder: str, flag: str, tracks: int = None) -> str or None:
    """Функция для рендеринга"""
    reapy.perform_action(40015)
    folder = os.path.normpath(folder)
    clsname, title = '#32770', 'Render to File'
    hide_window(clsname, title, 'render_main')
    hwnd = win32gui.FindWindow(clsname, title)
    if flag == 'main':
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
    clsname, title = '#32770', 'Rendering to file...'
    if flag == 'main':
        hide = Thread(
            target=hide_window,
            args=(clsname, title, 'render_to_file')
        )
    elif flag == 'de_noize':
        hide = Thread(
            target=hide_window,
            args=(clsname, title, 'de_noize', tracks)
        )
    hide.start()
    win32gui.SendMessage(render, win32con.BM_CLICK, 0, 0)
    if flag == 'main':
        output_file = os.path.normpath(glob_path(folder, 'audio.*')[0])
        return output_file


def hide_window(clsname: str, title: str, flag: str, tracks: int = None):
    if flag == 'render_to_file' or flag == 'de_noize':
        time.sleep(1)
    hwnd = win32gui.FindWindow(clsname, title)
    if flag != 'de_noize':
        while not hwnd:
            time.sleep(0.1)
            hwnd = win32gui.FindWindow(clsname, title)
        win32gui.ShowWindow(hwnd, 0)
    else:
        if tracks == 1:
            while not hwnd:
                time.sleep(0.1)
                hwnd = win32gui.FindWindow(clsname, title)
            win32gui.ShowWindow(hwnd, 0)
        else:
            for i in range(1, tracks + 1):
                hwnd = win32gui.FindWindow(
                    clsname, f'Rendering region {i}/{tracks}...'
                )
                while not hwnd:
                    time.sleep(0.1)
                    hwnd = win32gui.FindWindow(
                        clsname, f'Rendering region {i}/{tracks}...'
                    )
                win32gui.ShowWindow(hwnd, 0)


def de_noizer(folder: str, audio) -> List[str]:
    project_path = load_path('nrtemplate')
    new_path = project_save(folder, project_path, 'de_noize')
    project = create_project(new_path)
    tracks = len(audio)
    audio_select(audio, 'de_noize')
    render(folder, 'de_noize', tracks)
    project.save()
    project.close()
    os.remove(new_path)
    os.remove(new_path.replace('.rpp', '.rpp-bak'))
    for file in audio:
        os.remove(file)
        os.remove(f'{file}.reapeaks')
    return list(glob_path(folder, '*.flac') + glob_path(folder, '*.wave'))


if __name__ == '__main__':
    pass
