from reapy import reascript_api as RPR
from typing import List
import multiprocessing as mp
import reapy
import tkinter
from window_utils import buttons_freeze, buttons_active


def list_generator(position, strt_idx, end_idx, list, queue, flag):
    if flag == 'subs':
        dbbl_sbs = {}
        pattern = '- '
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
        if flag == 'subs':
            text = RPR.ULT_GetMediaItemNote(item)
            if pattern in text.lower():
                dbbl_sbs[i] = [start, end, 0]
        position += 1
    if flag == 'subs':
        queue.put([list, dbbl_sbs])
    else:
        queue.put(list)


def fix_checker(master: tkinter.Tk, BUTTONS: List):
    buttons_freeze(master, BUTTONS)
    project = reapy.Project()
    track = RPR.GetTrack(0, 1)
    subs_enum = RPR.CountTrackMediaItems(track)
    items_enum = RPR.CountMediaItems(0)
    subs_list = [[float] * 2] * subs_enum
    items_list = [[float] * 2] * (items_enum - subs_enum - 1)
    queue_subs = mp.Queue()
    queue_items = mp.Queue()
    checked_subs = []
    dubbles_items = []
    subs_list_gen = mp.Process(
        target=list_generator,
        args=(0, 1, (subs_enum + 1), subs_list, queue_subs, 'subs')
    )
    items_list_gen = mp.Process(
        target=list_generator,
        args=(0, (subs_enum + 1), items_enum, items_list, queue_items, 'items')
    )
    subs_list_gen.start()
    items_list_gen.start()
    all_subs_list = queue_subs.get()
    items_list = queue_items.get()
    subs_list_gen.join()
    items_list_gen.join()
    subs_list = all_subs_list[0]
    dbbl_sbs = all_subs_list[1]
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
                        project.add_marker(j[0], 'DUBBLE', (0, 255, 255))
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
    buttons_active(master, BUTTONS)
    master.focus_force()


if __name__ == '__main__':
    pass
