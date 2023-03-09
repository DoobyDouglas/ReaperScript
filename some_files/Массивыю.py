import reapy
from reapy import reascript_api as RPR
import datetime


def fix_check():
    project = reapy.Project()
    track = RPR.GetTrack(0, 1)
    subs_enum = RPR.CountTrackMediaItems(track)
    items_enum = RPR.CountMediaItems(0)
    subs_list = []
    items_list = []
    checked_subs_ids = []
    previous_items_ids = []
    start = datetime.datetime.now()
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
        subs_list.append([start_sub, end_sub])
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
        items_list.append([start_item, end_item])
    for s in subs_list:
        for i in items_list:
            if i not in previous_items_ids:
                if i[0] >= s[0] and i[1] <= s[1]:
                    previous_items_ids.append(i)
                    checked_subs_ids.append(s)
                    break
                elif i[0] <= s[0] and i[1] >= s[1]:
                    previous_items_ids.append(i)
                    checked_subs_ids.append(s)
                    break
                elif i[0] < s[0] and (
                        i[1] > s[0] and i[1] < s[1]
                        ):
                    previous_items_ids.append(i)
                    checked_subs_ids.append(s)
                    break
                elif i[0] > s[0] and (
                        i[0] < s[1] and i[1] > s[1]
                        ):
                    previous_items_ids.append(i)
                    checked_subs_ids.append(s)
                    break
    for s in subs_list:
        if s not in checked_subs_ids:
            for i in previous_items_ids:
                if i[0] >= s[0] and i[1] <= s[1]:
                    checked_subs_ids.append(s)
                    break
                elif i[0] <= s[0] and i[1] >= s[1]:
                    checked_subs_ids.append(s)
                    break
                elif i[0] < s[0] and (
                        i[1] > s[0] and i[1] < s[1]
                        ):
                    checked_subs_ids.append(s)
                    break
                elif i[0] > s[0] and (
                        i[0] < s[1] and i[1] > s[1]
                        ):
                    checked_subs_ids.append(s)
                    break
    for s in subs_list:
        if s not in checked_subs_ids:
            project.add_marker(s[0])

    finish = datetime.datetime.now()
    runtime = finish - start
    print(runtime)


fix_check()
