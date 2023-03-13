import reapy
from reapy import reascript_api as RPR


def fix_check():
    project = reapy.Project()
    track = RPR.GetTrack(0, 1)
    subs_enum = RPR.CountTrackMediaItems(track)
    items_enum = RPR.CountMediaItems(0)
    subs_list = [[float] * 2] * subs_enum
    items_list = [[float] * 2] * (items_enum - subs_enum)
    checked_subs = []
    dubbles_items = []
    position = 0
    for i in range(1, (subs_enum + 1)):
        sub_item = RPR.GetMediaItem(0, i)
        start_sub = RPR.GetMediaItemInfo_Value(
            sub_item,
            'D_POSITION'
        )
        end_sub = start_sub + RPR.GetMediaItemInfo_Value(
            sub_item,
            'D_LENGTH'
        )
        subs_list[position] = [start_sub, end_sub]
        position += 1
    position = 0
    for i in range((subs_enum + 1), (items_enum + 1)):
        item = RPR.GetMediaItem(0, i)
        start_item = RPR.GetMediaItemInfo_Value(
            item,
            'D_POSITION'
        )
        end_item = start_item + RPR.GetMediaItemInfo_Value(
            item,
            'D_LENGTH'
        )
        items_list[position] = [start_item, end_item]
        position += 1
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
