import multiprocessing as mp
import reapy
from typing import List, Tuple, Dict
from reapy import reascript_api as RPR
from multiprocessing import freeze_support
import pysubs2


def subs_generator(
        project: reapy.Project,
        sbttls: pysubs2.SSAFile,
        strt_idx: int,
        end_idx: int,
        list: List[List[float]],
        queue: mp.Queue,
        flag: str
        ) -> None:
    position = 0
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
        list[position] = [start, end]
        position += 1
    queue.put(list)


def import_subs(subs: str, project: reapy.Project) -> List[List[float]]:  # subs: List[str
    if subs and (True or True):
        sbttls = pysubs2.load(subs)  # subs[0]
        mid = len(sbttls) // 2
        sub_list_1 = [[float] * 2] * mid
        sub_list_2 = [[float] * 2] * (len(sbttls) - mid)
        queue_1 = mp.Queue()
        queue_2 = mp.Queue()
        if True:            
            subs_gen_1 = mp.Process(target=subs_generator, args=(project, sbttls, 0, mid, sub_list_1, queue_1, 'region'))
            subs_gen_2 = mp.Process(target=subs_generator, args=(project, sbttls, mid, len(sbttls), sub_list_2, queue_2, 'region'))
            subs_gen_1.start()
            subs_gen_2.start()
            sub_list_1 = queue_1.get()
            sub_list_2 = queue_2.get()
            subs_gen_1.join()
            subs_gen_2.join()
        if True:
            subs_gen_1 = mp.Process(target=subs_generator, args=(project, sbttls, 0, mid, sub_list_1, queue_1, 'item'))
            subs_gen_2 = mp.Process(target=subs_generator, args=(project, sbttls, mid, len(sbttls), sub_list_2, queue_2, 'item'))
            subs_gen_1.start()
            subs_gen_2.start()
            sub_list_1 = queue_1.get()
            sub_list_2 = queue_2.get()
            subs_gen_1.join()
            subs_gen_2.join()
        sub_list_1.extend(sub_list_2)
        return sub_list_1


if __name__ == '__main__':
    freeze_support()
    project = reapy.Project()
    subs = 'Z:/test/09/09.srt'
    import_subs(subs, project)
