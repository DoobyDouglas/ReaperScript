import reapy
from reapy import reascript_api as RPR
import datetime
import multiprocessing as mp


def list_generator(position, strt_idx, end_idx, list, queue):
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


def fix_check():
    project = reapy.Project()
    track = RPR.GetTrack(0, 1)
    subs_enum = RPR.CountTrackMediaItems(track)
    items_enum = RPR.CountMediaItems(0)
    subs_list = [[float] * 2] * subs_enum
    items_list = [[float] * 2] * (items_enum - subs_enum)
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
        args=(0, (subs_enum + 1), (items_enum + 1), items_list, queue_items)
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


if __name__ == '__main__':
    fix_check()
