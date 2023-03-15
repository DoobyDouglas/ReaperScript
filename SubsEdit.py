import pysubs2
import re

path = 'Z:/testing/1.srt'


def subs_edit(path: str):
    subs = pysubs2.load(path)
    pattern_1 = r'\((.*?)\)'
    pattern_2 = r'\[.*?]$'
    to_delete = [
        i for i, line in enumerate(subs) if re.match(pattern_1, line.text)
        or re.match(pattern_2, line.text)
    ]
    for i in reversed(to_delete):
        del subs[i]

    subs.save(path)


subs_edit(path)
