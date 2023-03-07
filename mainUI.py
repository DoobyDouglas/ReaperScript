from PyQt5.QtWidgets import QApplication, QMessageBox
from MainWindow import *
import configparser

from pathlib import Path
import psutil
import asstosrt
import sys
import os
import keyboard
import subprocess
import time
import os
import glob
import configparser
import reapy
import py_win_keyboard_layout as pwkl
from typing import List
from reapy import reascript_api as RPR


PATHS = [
    'fx_chains_folder',
    'reaper_path',
    'project_path',
    'folder_file',
]

OPTIONS = [
        'split',
        'normalize',
        'normalize_video',
        'volume',
        'sub_item',
        'sub_region',
        'render_audio',
        'render_video',
        'newfolder',
        'changename'
        'runtime'
        'savetime'
    ]


# настройка конфига
def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not os.path.exists('config.ini'):
        config.add_section('PATHS')
        for path in PATHS:
            config.set('PATHS', path, '')
        config.add_section('OPTIONS')
        for option in OPTIONS:
            config.set('OPTIONS', option, '')
        with open('config.ini', "w") as config_file:
            config.write(config_file)
    return config


def save_path_to_config(name, path):
    """Функция для сохранения пути в файл конфигурации"""
    config = get_config()
    if 'PATHS' not in config:
        config['PATHS'] = {}
    config['PATHS'][name] = path
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def load_path_from_config(name):
    """Функция для загрузки пути из файла конфигурации"""
    config = get_config()
    try:
        path = config['PATHS'][name]
    except KeyError:
        path = None
    return path


def start():

    '''Form, Window = uic.loadUiType("MainWindow.ui")
    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)
    window.show()'''



    form.lineEdit_3.setText(load_path_from_config('reaper_path'))   
    form.lineEdit_2.setText(load_path_from_config('project_path'))  
    form.lineEdit.setText(load_path_from_config('fx_chains_folder'))    
    
    #провекра на запущенный рипер, выполняется только если есть путь к риперу
    if load_path_from_config('reaper_path'):
        for proc in psutil.process_iter():
            name = proc.name()
            if name == 'reaper.exe':
                break
        if name != 'reaper.exe':
            msgBox = QMessageBox()
            msgBox.setWindowTitle("ВАЖНО")
            msgBox.setText('Для работы программы reaper должен быть открыт, запустить reaper? После запуска нужно перезапустить программу.')
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            if msgBox.exec_() == QMessageBox.Yes:
                subprocess.Popen(load_path_from_config('reaper_path'))
                os.execl(sys.executable, sys.executable, *sys.argv)
   
    #рипер ехе      
    def repear_exe():
        reaper_path = load_path_from_config('reaper_path')
        reaper_path = QtWidgets.QFileDialog.getOpenFileName(None,
            'Выбрать reaper.exe',
            'C:\Program Files',        
            'Exe file (reaper.exe)'
        )[0]
        if not reaper_path:
            pass
        else:
            save_path_to_config('reaper_path', reaper_path)
            form.lineEdit_3.setText(reaper_path)
        return reaper_path
        
    form.pushButton_3.clicked.connect(repear_exe)

    #шаблон   
    def project_folder():
        project_path = load_path_from_config('project_path')
        project_path = QtWidgets.QFileDialog.getOpenFileName(None,
            'Выберите файл шаблона проекта REAPER',
            None,
            'RPP file (*.rpp)'
        )[0]
        if not project_path:
            pass
        save_path_to_config('project_path', project_path)
        form.lineEdit_2.setText(project_path)
        return project_path
        
    form.pushButton_2.clicked.connect(project_folder)

    #FX        
    def fx_folder():
        fx_chains_folder = load_path_from_config('fx_chains_folder')
        fx_chains_folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Выбор FX')
        if not fx_chains_folder:
            pass
        save_path_to_config('fx_chains_folder', fx_chains_folder)
        form.lineEdit.setText(fx_chains_folder)
        return fx_chains_folder
        
    form.pushButton.clicked.connect(fx_folder)

    #Рабочая папка
    def choice_folder():
        set_file = load_path_from_config('folder_file')
        global folder
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Рабочая папка', set_file)
        form.lineEdit_4.setText(folder)
    form.pushButton_4.clicked.connect(choice_folder)

    #Настройка сохранение рабочей папки
    def setting_folder():
        const_workfolder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Рабочая папка')
        save_path_to_config('folder_file', const_workfolder)
        
    form.pushButton_6.clicked.connect(setting_folder)

    #считывание и расстановка чекбоксов
    config = get_config()
    form.checkBox.setChecked(bool(config['OPTIONS']['split']))
    form.checkBox_2.setChecked(bool(config['OPTIONS']['normalize']))
    form.checkBox_3.setChecked(bool(config['OPTIONS']['normalize_video']))
    form.checkBox_4.setChecked(bool(config['OPTIONS']['volume']))
    form.checkBox_5.setChecked(bool(config['OPTIONS']['sub_item']))
    form.checkBox_6.setChecked(bool(config['OPTIONS']['sub_region']))
    form.checkBox_7.setChecked(bool(config['OPTIONS']['render_audio']))
    form.checkBox_8.setChecked(bool(config['OPTIONS']['render_video']))
    form.checkBox_9.setChecked(bool(config['OPTIONS']['newfolder']))

    def checkboxUI(param: str):
        config = get_config()

        #если пользователь написал свои числа в задержу(для регулировки работы приложения), то принимаются его значения в sleep, если нет, то наши стандарт 1с
        if form.lineEdit_5.text():
            if form.lineEdit_5.text().replace(".", "", 1).isdigit():
                if float(form.lineEdit_5.text()) < 11 :
                    runtime = float(form.lineEdit_5.text()) 
                    save_path_to_config('runtime', runtime)
                else:
                    QMessageBox.about(None, "Ошибка", "Задержка при открытии слишком большая(max. 10)")
                    return       
            else:
                QMessageBox.about(None, "Ошибка", "В задержку можно ввести только число от 0 до 10")
                return
        else:
            runtime = 1

        if form.lineEdit_6.text():
            if form.lineEdit_6.text().replace(".", "", 1).isdigit():
                if float(form.lineEdit_6.text()) < 11 :
                    savetime = float(form.lineEdit_6.text())
                    save_path_to_config('savetime', savetime)
                else:
                    QMessageBox.about(None, "Ошибка", "Задержка при сохранении слишком большая(max. 10)")
                    return       
            else:
                QMessageBox.about(None, "Ошибка", "В задержку можно ввести только число от 0 до 10")
                return
        else:
            savetime = 1


        #addfxtime = form.lineEdit_7.text()

        #проверяем выбраны ли все рабочие папки
        if bool(load_path_from_config('fx_chains_folder')) == False or bool(load_path_from_config('project_path')) == False or bool(load_path_from_config('reaper_path')) == False or bool(form.lineEdit_4.text()) == False:
            QMessageBox.about(None, "Ошибка", "Вы не выбрали все рабочие папки")
            return

        s_number = os.path.basename(folder)
        fileExtMp4 = r".mp4"
        fileExtMkv = r".mkv"
        videonamemp4 = ''.join(([_ for _ in os.listdir(folder) if _.endswith(fileExtMp4)]))
        videonamemkv = ''.join(([_ for _ in os.listdir(folder) if _.endswith(fileExtMkv)]))

        #Проверяем на все аудио
        if bool(glob.glob(os.path.join(folder, '*.flac*'))) == False and bool(glob.glob(os.path.join(folder, '*.flac'))) == False and bool(glob.glob(os.path.join(folder, '*.wav*'))) == False and bool(glob.glob(os.path.join(folder, '*.wav'))) == False:
            QMessageBox.about(None, "Ошибка", "В папке нет ни одного аудио файла")
            return
        
        #Получает List мп4 и мкв
        count_mkv = glob.glob(os.path.join(folder, '*.mkv'))
        count_mp4 = glob.glob(os.path.join(folder, '*.mp4'))

        #Проверка на видеофайлы
        if bool(count_mp4) == False and bool(count_mkv) == False: #если нет ни одного
            QMessageBox.about(None, "Ошибка", "В папке нет видеофайлов")
            return
        elif len(count_mkv) > 1: #если мкв больше одного
            QMessageBox.about(None, "Ошибка", "В папке несколько видео формата MKV")
            return
        elif len(count_mp4) > 1: #если мп4 больше одного
            QMessageBox.about(None, "Ошибка", "В папке несколько видео формата MP4")
            return
        elif count_mkv and count_mp4: #если есть и мп4 и мкв
            QMessageBox.about(None, "Ошибка", "В папке несколько видео")
            return

        #Функция для проверки раскладки клавиатуры
        current_layout = pwkl.get_foreground_window_keyboard_layout()
        if current_layout != 67699721:
            pwkl.change_foreground_window_keyboard_layout(0x00000409)
            QMessageBox.about(None, "Ошибка", "Неправильная раскладка. Если раскладнка не поменялась сама - поменяйте вручную. Нажмите на кнопку еще раз")
            

        #Функция для изменения имени видео, создание папки, вытаскивание субтитров, конвертация субтитров vtt
        if bool(videonamemp4) == True:
            try:
                videoname = os.rename(folder + "/" + videonamemp4, folder + "/" + s_number + fileExtMp4)
            except OSError:
                QMessageBox.about(None, "Ошибка", "Видеофайл используется")
                return
            videoname = ''.join(([_ for _ in os.listdir(folder) if _.endswith(fileExtMp4)]))
            if form.checkBox_10.isChecked():
                title = folder.split('/')[-2]
                os.rename(folder + "/" + videoname, folder + '/' + title + '_' + videoname)
                videoname = ''.join(([_ for _ in os.listdir(folder) if _.endswith(fileExtMp4)]))
            videofolder = f'{folder}/{videoname}'

            if glob.glob(os.path.join(folder, '*.srt')):
                subs = glob.glob(os.path.join(folder, '*.srt'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.srt')
            elif glob.glob(os.path.join(folder, '*.vtt')):
                subs = glob.glob(os.path.join(folder, '*.vtt'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.vtt')
                command = f'ffmpeg -i {subs[0]} {folder}/{s_number}.srt'
                subprocess.call(command, shell=True)
            elif glob.glob(os.path.join(folder, '*.ass')): #нахождение ASS
                subs = glob.glob(os.path.join(folder, '*.ass'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.ass')
                disk = folder.split(':')[0].lower()
                folder_path = folder.split(':')[1]
                command1 = f'{disk}: && cd {folder_path} && asstosrt -e utf-8'
                subprocess.call(command1, shell=True)
            else:
                command = f'ffmpeg -i {folder}/{videoname} {folder}/{s_number}.ass'
                subprocess.call(command, shell=True)
                if glob.glob(os.path.join(folder, '*.ass')): #если достал ASS конверт в SRT
                    disk = folder.split(':')[0].lower()
                    folder_path = folder.split(':')[1]
                    command1 = f'{disk}: && cd {folder_path} && asstosrt -e utf-8'
                    subprocess.call(command1, shell=True)
                else: #если не достал ASS, пытается достать SRT
                    command = f'ffmpeg -i {folder}/{videoname} {folder}/{s_number}.srt'
                    subprocess.call(command, shell=True)
        else:
            try:
                videoname = os.rename(folder + "/" + videonamemkv, folder + "/" + s_number + fileExtMkv)
            except OSError:
                QMessageBox.about(None, "Ошибка", "Видеофайл используется")
                return
            videoname = ''.join(([_ for _ in os.listdir(folder) if _.endswith(fileExtMkv)]))
            if form.checkBox_10.isChecked():
                title = folder.split('/')[-2]
                os.rename(folder + "/" + videoname, folder + '/' + title + '_' + videoname)
                videoname = ''.join(([_ for _ in os.listdir(folder) if _.endswith(fileExtMkv)]))
            videofolder = f'{folder}/{videoname}'

            if glob.glob(os.path.join(folder, '*.srt')): #нахождение SRT
                subs = glob.glob(os.path.join(folder, '*.srt'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.srt')
            elif glob.glob(os.path.join(folder, '*.vtt')): #нахождение VTT
                subs = glob.glob(os.path.join(folder, '*.vtt'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.vtt')
                command = f'ffmpeg -i {subs[0]} {folder}/{s_number}.srt'
                subprocess.call(command, shell=True)
            elif glob.glob(os.path.join(folder, '*.ass')): #нахождение ASS
                subs = glob.glob(os.path.join(folder, '*.ass'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.ass')
                disk = folder.split(':')[0].lower()
                folder_path = folder.split(':')[1]
                command1 = f'{disk}: && cd {folder_path} && asstosrt -e utf-8'
                subprocess.call(command1, shell=True)
            else: #доставание ASS из MKV
                command = f'ffmpeg -i {folder}/{videoname} -map 0:s:m:language:eng -map -0:s:m:title:SDH {folder}/{s_number}.ass'
                subprocess.call(command, shell=True)
                if glob.glob(os.path.join(folder, '*.ass')): #если достал ASS конверт в SRT
                    disk = folder.split(':')[0].lower()
                    folder_path = folder.split(':')[1]
                    command1 = f'{disk}: && cd {folder_path} && asstosrt -e utf-8'
                    subprocess.call(command1, shell=True)
                else: #если не достал ASS, пытается достать SRT
                    command = f'ffmpeg -i {folder}/{videoname} -map 0:s:m:language:eng -map -0:s:m:title:SDH {folder}/{s_number}.srt'
                    subprocess.call(command, shell=True)
        if glob.glob(os.path.join(folder, '*.srt')): #если есть после всех манипуляций в папке есть SRT, то привязываем полный путь к переменной
            if glob.glob(os.path.join(folder, '*.ass')):
                subs = glob.glob(os.path.join(folder, '*.ass'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.ass')
                os.remove(f'{folder}/{s_number}.ass')
            elif glob.glob(os.path.join(folder, '*.vtt')):
                subs = glob.glob(os.path.join(folder, '*.vtt'))
                filenamae = os.path.splitext(subs[0])[0].split('\\')[-2]
                os.rename(subs[0], filenamae + '/' + s_number + '.vtt')
                os.remove(glob.glob(os.path.join(folder, '*.vtt')))
            localsub = f'{folder}/{s_number}.srt'
        else: 
            localsub = 'NotFound'
        #localsub - путь к файлу сабов, videofolder - путь к видеофайлу 

        #нахождение неправильных форматов и переименовка
        if glob.glob(os.path.join(folder, '*.flac*')):
            flac_audio = glob.glob(os.path.join(folder, '*.flac*'))
            if flac_audio:
                for file in flac_audio:
                    if '.reapeaks' not in file.lower():
                        filename = os.path.splitext(file)[0]
                        ext = os.path.splitext(file)[-1]
                        if ext != '.flac':
                            try:
                                os.rename(file, filename + '.flac')
                            except OSError:
                                QMessageBox.about(None, "Ошибка", "Аудиофайл используется")
                                return
                    else:
                        pass
        # находить нормальные файла
        flac_audio = glob.glob(os.path.join(folder, '*.flac'))
        # изменение на нормальный путь
        flac_audio = list(map(lambda x: x.replace('\\', '/'), flac_audio))

        if glob.glob(os.path.join(folder, '*.wav*')):
            wav_audio = glob.glob(os.path.join(folder, '*.wav*'))
            if flac_audio:
                for file in flac_audio:
                    if '.reapeaks' not in file.lower():
                        filename = os.path.splitext(file)[0]
                        ext = os.path.splitext(file)[-1]
                        if ext != '.wav':
                            try:
                                os.rename(file, filename + '.wav')
                            except OSError:
                                QMessageBox.about(None, "Ошибка", "Аудиофайл используется")
                                return
                    else:
                        pass
        # находить нормальные файла
        wav_audio = glob.glob(os.path.join(folder, '*.wav'))
        # изменение на нормальный путь
        wav_audio = list(map(lambda x: x.replace('\\', '/'), wav_audio))

        # настройка чейнов
        fx_dict = {}
        fx_chains_folder = load_path_from_config('fx_chains_folder')
        fx_chains = glob.glob(os.path.join(fx_chains_folder, '*.RfxChain'))
        for chain in fx_chains:
            fx_chain_name = chain.split('\\')[-1]
            dubber_name = fx_chain_name.split('.')[-2].lower()
            fx_dict[dubber_name] = fx_chain_name

        # загрузка
        subprocess.run([load_path_from_config('reaper_path'), load_path_from_config('project_path')])
        time.sleep(runtime)

        # Проверка на папку
        if form.checkBox_9.isChecked():
            config['OPTIONS']['newfolder'] = '1'
            if os.path.exists(f'{folder}/{s_number}') == False:  # если нет внутри такой папки то создает её и сохраняет
                os.mkdir(folder + "/" + s_number)
                new_folder = f'{folder}/{s_number}'
                new_porject_path = new_folder.replace('/', '\\') + '\\' + f'{s_number}'
                time.sleep(savetime)
                keyboard.send('ctrl+alt+s')
                time.sleep(savetime)
                keyboard.write(new_porject_path)
                keyboard.send('enter')

            #если есть, то просто сохраняет туда
            else:
                new_folder = f'{folder}/{s_number}'
                new_porject_path = new_folder.replace('/', '\\') + '\\' + f'{s_number}'
                time.sleep(savetime)
                keyboard.send('ctrl+alt+s')
                time.sleep(savetime)
                keyboard.write(new_porject_path)
                keyboard.send('enter')
        else:
            config['OPTIONS']['newfolder'] = ' '
            new_porject_path = folder.replace('/', '\\') + '\\' + f'{s_number}'
            time.sleep(savetime)
            keyboard.send('ctrl+alt+s')
            time.sleep(savetime)
            keyboard.write(new_porject_path)
            keyboard.send('enter')

        #project = reapy.Project() чекнуть потом

        # Добавляем аудио и FX к ним
        for file in flac_audio:
            RPR.InsertMedia(file, 1)
            track = RPR.GetLastTouchedTrack()
            for name in fx_dict:
                if name in file.split('\\')[-1].lower():
                    RPR.TrackFX_AddByName(track, fx_dict[name], 0, -1)
                    #я бы сюда поставил слип, потому что бывает тяжелые пресеты для дабберов
                    RPR.GetSetMediaTrackInfo_String(
                        track, 'P_NAME', name.upper(), True)
                    if form.checkBox_4.isChecked():
                        config['OPTIONS']['volume'] = '1'
                        item = RPR.GetTrackMediaItem(track, 0)
                        RPR.SetMediaItemInfo_Value(item, 'D_VOL', 1.5)
                    else:
                        config['OPTIONS']['volume'] = ' '
        for file in wav_audio:
            RPR.InsertMedia(file, 0)
            track = RPR.GetLastTouchedTrack()
            for name in fx_dict:
                if name in file.split('\\')[-1].lower():
                    RPR.TrackFX_AddByName(track, fx_dict[name], 0, -1)
                    #я бы сюда поставил слип, потому что бывает тяжелые пресеты для дабберов
                    RPR.GetSetMediaTrackInfo_String(
                        track, 'P_NAME', name.upper(), True)
                    if form.checkBox_4.isChecked():
                        config['OPTIONS']['volume'] = '1'
                        item = RPR.GetTrackMediaItem(track, 0)
                        RPR.SetMediaItemInfo_Value(item, 'D_VOL', 1.5)
                    else:
                        config['OPTIONS']['volume'] = ' '

        #Добавляем видео
        RPR.InsertMedia(videofolder, (1 << 9) | 0)

        # Добавляем сабы айтемы
        if form.checkBox_5.isChecked():
            config['OPTIONS']['sub_item'] = '1'
            if localsub == 'NotFound':
                pass
            else:
                keyboard.send('ctrl+t')
                time.sleep(1)
                keyboard.send('ctrl+0')
                time.sleep(1)
                fix_path = localsub.replace('/', '\\')
                keyboard.write(fix_path)
                keyboard.send('enter')
        else:
            config['OPTIONS']['sub_item'] = ' '

        # Добавляем сабы регионы
        if form.checkBox_6.isChecked():
            config['OPTIONS']['sub_region'] = '1'
            if localsub == 'NotFound':
                pass
            else:
                keyboard.send('i')
                time.sleep(1)
                fix_path = localsub.replace('/', '\\')
                keyboard.write(fix_path)
                keyboard.send('enter')
        else:
            config['OPTIONS']['sub_region'] = ' '

        # Можно дать больше времени на работу сплита,
        # если уменьшить значение X_FILE
        # Значения пригодятся и в других функциях
        X_FILE = 5
        video_item = RPR.GetMediaItem(0, 0)
        lenght = RPR.GetMediaItemInfo_Value(video_item, "D_LENGTH") / 60
        sleep = lenght / X_FILE
        all_tracks = RPR.GetNumTracks()
        dub_tracks = all_tracks - 2
        split_sleep = dub_tracks * sleep

        # Сплит
        if form.checkBox.isChecked():
            config['OPTIONS']['split'] = '1'
            RPR.SetMediaItemSelected(video_item, False)
            RPR.Main_OnCommand(40760, 0)
            time.sleep(split_sleep)
            keyboard.send('enter')
            time.sleep(1)
        else:
            config['OPTIONS']['split'] = ' '

        normalize_loudness = RPR.NamedCommandLookup(
            '_BR_NORMALIZE_LOUDNESS_ITEMS23'
        )
        
        #нормалайз
        if form.checkBox_3.isChecked() and form.checkBox_2.isChecked():
            config['OPTIONS']['normalize'] = '1'
            config['OPTIONS']['normalize_video'] = '1'
            RPR.SelectAllMediaItems(0, True)
            RPR.Main_OnCommand(normalize_loudness, 0)
        else:
            if form.checkBox_2.isChecked():
                config['OPTIONS']['normalize'] = '1'
                RPR.SelectAllMediaItems(0, True)
                RPR.SetMediaItemSelected(video_item, False)
                RPR.Main_OnCommand(normalize_loudness, 0)
            else:
                config['OPTIONS']['normalize'] = ' '

            if form.checkBox_3.isChecked():
                config['OPTIONS']['normalize_video'] = '1'
                RPR.SelectAllMediaItems(0, False)
                RPR.SetMediaItemSelected(video_item, True)
                RPR.Main_OnCommand(normalize_loudness, 0)
            else:
                config['OPTIONS']['normalize_video'] = ' '

        if form.checkBox_7.isChecked():
            config['OPTIONS']['render_audio'] = '1'
            RPR.Main_OnCommand(40015, 0)
            time.sleep(1)
            keyboard.write(s_number)
            time.sleep(1)
            for i in range(34):
                keyboard.press('tab')
            keyboard.write(new_porject_path)
            keyboard.press('enter')
        else:
            config['OPTIONS']['render_audio'] = ' '

        if form.checkBox_8.isChecked():
            config['OPTIONS']['render_video'] = '1'
            if glob.glob(os.path.join(new_folder, '*.flac')):
                print('Я НАЧАЛ РЕНДЕРИТЬ ВИДОСИК')
                command = f'ffmpeg -i {new_folder}/{s_number}.flac -ab 256k {new_folder}/coder{s_number}.aac'
                subprocess.call(command, shell=True)
                command = (
                f'ffmpeg -i {videofolder} -i {new_folder}/coder{s_number}.aac -c copy '
                f'-map 0:v:0 -map 1:a:0 {folder}/{videoname[0]}_DUB.mkv'
                )
                subprocess.call(command, shell=True)
            elif glob.glob(os.path.join(new_folder, '*.wav')):
                print('Я НАЧАЛ РЕНДЕРИТЬ ВИДОСИК')
                command = f'ffmpeg -i {new_folder}/{s_number}.wav -ab 256k {new_folder}/coder{s_number}.aac'
                subprocess.call(command, shell=True)
                command = (
                f'ffmpeg -i {videofolder} -i {new_folder}/coder{s_number}.aac -c copy '
                f'-map 0:v:0 -map 1:a:0 {folder}/{videoname[0]}_DUB.mkv'
                )
                subprocess.call(command, shell=True)
            else: 
                QMessageBox.about(None, "Ошибка", "В рабочей папки нет аудио файла FLAC или WAV")
        else:
            config['OPTIONS']['render_video'] = ' '

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    form.pushButton_5.clicked.connect(checkboxUI)
    app.exec()




app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
form = Ui_MainWindow()
form.setupUi(MainWindow)
MainWindow.show()
start()
