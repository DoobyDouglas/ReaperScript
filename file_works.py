from typing import List, Tuple
import tkinter.messagebox
import asstosrt
import pysubs2
import tkinter
import ffmpeg
import glob
import re
import os


MANY_VIDEOS = 'Оставьте в рабочей папке только нужный видеофайл'
NO_AUDIO = 'В рабочей папке нет аудиофайлов подходящего формата'
MANY_SUBS = 'Оставьте в рабочей папке только нужный файл субтитров'
IN_USE = 'Закройте приложения использующие рабочие файлы'


def get_path_to_files(folder: str, extension: str) -> List[str]:
    """Функция для получения пути к файлу"""
    return glob.glob(os.path.join(folder, extension))


def subs_rename(folder: str, subs: List[str], number: str) -> List[str]:
    """Функция для изменения имени субтитров"""
    filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
    new_name = f'{filenamae}/{number}.srt'
    os.rename(subs[0], new_name)
    subs = get_path_to_files(folder, '*.srt')
    return subs


def subs_extract(
        folder: str, video: List[str], param: str, mapping: str
        ) -> None:
    """Функция для извлечения субтитров из видео"""
    video_path = video[0].replace('\\', '/')
    input_file = ffmpeg.input(video_path)
    output_file = f'{folder}/subs.{param}'
    output = ffmpeg.output(input_file, output_file, map=mapping)
    ffmpeg.run(output)


def ass_sub_convert(folder: str, subs: List[str]) -> None:
    """Функция для конвертирования ass субтитров"""
    with open(subs[0], 'r', encoding='utf-8') as ass_file:
        srt_sub = asstosrt.convert(ass_file)
    with open(f'{folder}/subs.srt', 'w', encoding='utf-8') as srt_file:
        srt_file.write(srt_sub)
    os.remove(os.path.join(subs[0]))


def vtt_sub_convert(folder: str, subs: List[str]) -> None:
    """Функция для конвертирования vtt субтитров"""
    new_name = f'{folder}/subs.vtt'
    os.rename(subs[0], new_name)
    input_file = ffmpeg.input(new_name)
    output_file = f'{folder}/subs.srt'
    output = ffmpeg.output(input_file, output_file)
    ffmpeg.run(output)
    os.remove(os.path.join(new_name))


def video_rename(
        folder: str,
        video: List[str]
    ) -> Tuple[List[str], str, str, str]:
    """Функция для изменения имени видео"""
    number = os.path.basename(folder)
    title = folder.split('/')[-2]
    ext = os.path.splitext(video[0])[-1]
    filename = os.path.splitext(video[0])[0].split('\\')[-2]
    new_name = f'{filename}/{title} {number}{ext}'
    try:
        os.rename(video[0], new_name)
        video = get_path_to_files(folder, f'*{ext}')
        return video, title, number, ext
    except PermissionError:
        tkinter.messagebox.showerror('Файл используется', IN_USE)
        raise SystemExit


def audio_rename(folder: str, audio: List[str], ext: str) -> List[str]:
    """Функция для изменения нечитаемых расширений"""
    for file in audio:
        file_ext = os.path.splitext(file)[-1]
        if file_ext == ext:
            continue
        elif '.reapeaks' not in file.lower():
            try:
                filename = os.path.splitext(file)[0]
                new_name = f'{filename}{ext}'
                copy = ''
                while os.path.exists(new_name):
                    copy += '_copy'
                    new_name = f'{filename}{copy}{ext}'
                os.rename(file, new_name)
            except PermissionError:
                tkinter.messagebox.showerror('Файл используется', IN_USE)
                raise SystemExit
    fixed_audio = get_path_to_files(folder, f'*{ext}')
    return fixed_audio


def comparator(sub: str) -> bool:
    """Функция для проверки субтитра"""
    if (
        (
            'text' in sub
            or 'sign' in sub
            or 'надпись' in sub
            or 'caption' in sub
            or 'title' in sub
            or 'song' in sub
            or 'screen' in sub
            or 'typedigital' in sub
        ) and 'subtitle' not in sub
    ):
        return True
    return False


def subs_edit(subs: List[str], flag: str) -> None:
    """Функция для удаления из субтитров надписей и песен"""
    subtitles = pysubs2.load(subs[0])
    if flag == 'srt':
        pattern_1 = r'\((.*?)\)'
        pattern_2 = r'\[.*?]$'
        pattern_3 = '♫'
        pattern_4 = '♪'
        to_delete = [
            i for i, line in enumerate(subtitles) if (
                re.match(pattern_1, line.text)
                or re.match(pattern_2, line.text)
                or pattern_3 in line.text
                or pattern_4 in line.text
            )
        ]
    elif flag == 'ass':
        to_delete = []
        search_char = '{'
        if subtitles.events[0].name and subtitles.events[0].style:
            for i, sub in enumerate(subtitles.events):
                if (
                    comparator(sub.name.lower())
                    or comparator(sub.style.lower())
                ) and search_char in sub.text:
                    to_delete.append(i)
        elif subtitles.events[0].name:
            for i, sub in enumerate(subtitles.events):
                if comparator(sub.name.lower()) and search_char in sub.text:
                    to_delete.append(i)
        elif subtitles.events[0].style:
            for i, sub in enumerate(subtitles.events):
                if comparator(sub.style.lower()) and search_char in sub.text:
                    to_delete.append(i)
        else:
            return
    for i in reversed(to_delete):
        del subtitles[i]
    subtitles.save(subs[0])


def file_works(folder: str) -> (
        Tuple[List[str], List[str], List[str], str, str, str]
        ):
    """Функция для подготовки файлов к работе"""
    mkv_video = get_path_to_files(folder, '*.mkv')
    mp4_video = get_path_to_files(folder, '*.mp4')
    if (mkv_video and mp4_video) or len(mkv_video) > 1 or len(mp4_video) > 1:
        tkinter.messagebox.showerror('Много видеофайлов', MANY_VIDEOS)
        raise SystemExit
    if mkv_video:
        video, title, number, ext = video_rename(folder, mkv_video)
    elif mp4_video:
        video, title, number, ext = video_rename(folder, mp4_video)
    flac_audio = get_path_to_files(folder, '*.flac*')
    wav_audio = get_path_to_files(folder, '*.wav*')
    if not flac_audio and not wav_audio:
        tkinter.messagebox.showerror('Нет аудиофайлов', NO_AUDIO)
        raise SystemExit
    if flac_audio:
        flac_audio = audio_rename(folder, flac_audio, '.flac')
    if wav_audio:
        wav_audio = audio_rename(folder, wav_audio, '.wav')
    audio = list(flac_audio + wav_audio)
    subs = get_path_to_files(folder, '*.srt')
    if len(subs) > 1:
        tkinter.messagebox.showerror('Много файлов субтитров', MANY_SUBS)
        raise SystemExit
    if subs:
        subs = subs_rename(folder, subs, number)
        subs_edit(subs, 'srt')
    else:
        ass_subs = get_path_to_files(folder, '*.ass')
        vtt_subs = get_path_to_files(folder, '*.vtt')
        if (ass_subs and vtt_subs) or len(ass_subs) > 1 or len(vtt_subs) > 1:
            tkinter.messagebox.showerror('Много файлов субтитров', MANY_SUBS)
            raise SystemExit
        if vtt_subs:
            vtt_sub_convert(folder, vtt_subs)
        elif ass_subs:
            subs_edit(ass_subs, 'ass')
            ass_sub_convert(folder, ass_subs)
        elif not ass_subs:
            if os.path.splitext(video[0])[-1] == '.mkv':
                subs_extract(folder, video, 'ass', '0:s:m:language:eng')
                ass_subs = get_path_to_files(folder, '*.ass')
                if not ass_subs:
                    subs_extract(folder, video, 'ass', '0:s:m:language:?')
                    ass_subs = get_path_to_files(folder, '*.ass')
                if ass_subs:
                    subs_edit(ass_subs, 'ass')
                    ass_sub_convert(folder, ass_subs)
        srt_subs = get_path_to_files(folder, '*.srt')
        if srt_subs:
            subs = subs_rename(folder, srt_subs, number)
            subs_edit(subs, 'srt')
        else:
            try:
                if os.path.splitext(video[0])[-1] == '.mkv':
                    subs_extract(folder, video, 'srt', '0:s:m:language:?')
                    subs = get_path_to_files(folder, '*.srt')
                    subs = subs_rename(folder, subs, number)
                    subs_edit(subs, 'srt')
            except IndexError:
                pass
    return subs, audio, video, title, number, ext


if __name__ == '__main__':
    pass
