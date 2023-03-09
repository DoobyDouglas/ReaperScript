import reapy
from reapy import reascript_api as RPR
import datetime


def fix_check():
    project = reapy.Project()
    track = RPR.GetTrack(0, 1)
    subs_enum = RPR.CountTrackMediaItems(track)
    items_enum = RPR.CountMediaItems(0)
    checked_subs_ids = set()
    previous_items_ids = set()
    start = datetime.datetime.now()
    for j in range(1, (subs_enum + 1)):
        sub_item = RPR.GetMediaItem(0, j)
        start_sub = RPR.GetMediaItemInfo_Value(
            sub_item,
            'D_POSITION'
        )
        end_sub = start_sub + RPR.GetMediaItemInfo_Value(
            sub_item,
            'D_LENGTH'
        )
        for i in range((subs_enum + 1), (items_enum + 1)):
            if i not in previous_items_ids:
                item = RPR.GetMediaItem(0, i)
                start_item = RPR.GetMediaItemInfo_Value(
                    item,
                    'D_POSITION'
                )
                end_item = start_item + RPR.GetMediaItemInfo_Value(
                    item,
                    'D_LENGTH'
                )
                if start_item >= start_sub and end_item <= end_sub:
                    previous_items_ids.add(i)
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
                elif start_item <= start_sub and end_item >= end_sub:
                    previous_items_ids.add(i)
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
                elif start_item < start_sub and (
                        end_item > start_sub and end_item < end_sub
                        ):
                    previous_items_ids.add(i)
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
                elif start_item > start_sub and (
                        start_item < end_sub and end_item > end_sub
                        ):
                    previous_items_ids.add(i)
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
    for j in range(1, (subs_enum + 1)):
        if j not in checked_subs_ids:
            sub_item = RPR.GetMediaItem(0, j)
            start_sub = RPR.GetMediaItemInfo_Value(
                sub_item,
                'D_POSITION'
            )
            end_sub = start_sub + RPR.GetMediaItemInfo_Value(
                sub_item,
                'D_LENGTH'
            )
            for i in previous_items_ids:
                item = RPR.GetMediaItem(0, i)
                start_item = RPR.GetMediaItemInfo_Value(
                    item,
                    'D_POSITION'
                )
                end_item = start_item + RPR.GetMediaItemInfo_Value(
                    item,
                    'D_LENGTH'
                )
                if start_item >= start_sub and end_item <= end_sub:
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
                elif start_item <= start_sub and end_item >= end_sub:
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
                elif start_item < start_sub and (
                        end_item > start_sub and end_item < end_sub
                        ):
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break
                elif start_item > start_sub and (
                        start_item < end_sub and end_item > end_sub
                        ):
                    checked_subs_ids.add(j)
                    print(f'Нашёл фразу для саба {j}')
                    break

    for j in range(1, (subs_enum + 1)):
        if j not in checked_subs_ids:
            sub_item = RPR.GetMediaItem(0, j)
            start_sub = RPR.GetMediaItemInfo_Value(sub_item, "D_POSITION")
            project.add_marker(start_sub)
    finish = datetime.datetime.now()
    runtime = finish - start
    print(runtime)


fix_check()
