from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication
import configparser

import os
import subprocess
import time
import os
import glob
import pyautogui
import configparser
import reapy
import tkinter
import tkinter.messagebox
import py_win_keyboard_layout as pwkl
from typing import List
from reapy import reascript_api as RPR


#настройка конфига
def create_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not os.path.exists('config.ini'):
        config = configparser.ConfigParser()
        config.add_section("PATHS")
        config.set("PATHS", "fx_chains_folder", "")
        config.set("PATHS", "reaper_path", "")
        config.set("PATHS", "project_path", "") 
        config.set("PATHS", "folder_file", "") 
        config.add_section("OPTIONS")
        config.set("OPTIONS", "split", "")
        config.set("OPTIONS", "normalize", "")
        config.set("OPTIONS", "normalize_video", "")
        config.set("OPTIONS", "volume", "")
        config.set("OPTIONS", "sub_item", "")
        config.set("OPTIONS", "sub_region", "")
        config.set("OPTIONS", "render_audio", "")
        config.set("OPTIONS", "render_video", "")
        with open('config.ini', "w") as config_file:
            config.write(config_file)
    return config

def save_path_to_config(name, path):
    """Функция для сохранения пути в файл конфигурации"""
    config = create_config()
    if 'PATHS' not in config:
        config['PATHS'] = {}
    config['PATHS'][name] = path
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def load_path_from_config(name):
    """Функция для загрузки пути из файла конфигурации"""
    config = create_config()
    try:
        path = config['PATHS'][name]
    except KeyError:
        path = None
    return path

def start():
    Form, Window = uic.loadUiType("MainWindow.ui")

    app = QApplication([])
    window = Window()
    form = Form()
    form.setupUi(window)
    window.show()




    form.lineEdit_3.setText(load_path_from_config('reaper_path'))   
    form.lineEdit_2.setText(load_path_from_config('project_path'))  
    form.lineEdit.setText(load_path_from_config('fx_chains_folder'))    
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
        
    form.pushButton_2.clicked.connect(project_folder)

    #FX
                
    def fx_folder():
        fx_chains_folder = load_path_from_config('fx_chains_folder')
        fx_chains_folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Выбор FX')
        if not fx_chains_folder:
            pass
        save_path_to_config('fx_chains_folder', fx_chains_folder)
        form.lineEdit.setText(fx_chains_folder)
        
    form.pushButton.clicked.connect(fx_folder)

    #Рабочая папка
    def choice_folder():
        set_file = load_path_from_config('folder_file')
        global folder
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Рабочая папка', set_file)
        form.lineEdit_4.setText(folder)
        return folder
    form.pushButton_4.clicked.connect(choice_folder)

    #Настройка сохранение рабочей папки
    def setting_folder():
        const_workfolder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Рабочая папка')
        save_path_to_config('folder_file', const_workfolder)
        
    form.pushButton_6.clicked.connect(setting_folder)


    #чекбоксы

    #считывание и расстановка чекбоксов
    config = create_config()
    form.checkBox.setChecked(bool(config['OPTIONS']['split']))
    form.checkBox_2.setChecked(bool(config['OPTIONS']['normalize']))
    form.checkBox_3.setChecked(bool(config['OPTIONS']['normalize_video']))
    form.checkBox_4.setChecked(bool(config['OPTIONS']['volume']))
    form.checkBox_5.setChecked(bool(config['OPTIONS']['sub_item']))
    form.checkBox_6.setChecked(bool(config['OPTIONS']['sub_region']))
    form.checkBox_7.setChecked(bool(config['OPTIONS']['render_audio']))
    form.checkBox_8.setChecked(bool(config['OPTIONS']['render_video']))


    #'dubbers_volume_up',
    #'item_subs',
    #'region_subs',
    #'split', +
    #'normalize', +
    #'render_audio',
    #'make_video'
    

    def checkboxUI():

        #запись чекбоксов
        config = create_config()
     
        if form.checkBox.isChecked():
            config['OPTIONS']['split'] = '1'
            #функция сплита
        else:
            config['OPTIONS']['split'] = ' '
            print("Не сплитую")

        if form.checkBox_2.isChecked():
            config['OPTIONS']['normalize'] = '1'
            #функция нормалайза
        else:
            config['OPTIONS']['normalize'] = ' '
            print("Не нормальизую")

        if form.checkBox_3.isChecked():
            config['OPTIONS']['normalize_video'] = '1'
            #функция нормалайза видео
        else:
            config['OPTIONS']['normalize_video'] = ' '
            print("Не нормальизую")
        
        if form.checkBox_4.isChecked():
            config['OPTIONS']['volume'] = '1'
            #функция громкости
        else:
            config['OPTIONS']['volume'] = ' '
            print("Не нормальизую")

        if form.checkBox_5.isChecked():
            config['OPTIONS']['sub_item'] = '1'
            #функция субтитров айтем
        else:
            config['OPTIONS']['sub_item'] = ' '
            print("Не нормальизую")
        
        if form.checkBox_6.isChecked():
            config['OPTIONS']['sub_region'] = '1'
            #функция субтитров регион
        else:
            config['OPTIONS']['sub_region'] = ' '
            print("Не нормальизую")
        
        if form.checkBox_7.isChecked():
            config['OPTIONS']['render_audio'] = '1'
            #функция рендер аудио
        else:
            config['OPTIONS']['render_audio'] = ' '
            print("Не нормальизую")
        
        if form.checkBox_8.isChecked():
            config['OPTIONS']['render_video'] = '1'
            #функция рендер видео
        else:
            config['OPTIONS']['render_video'] = ' '
            print("Не нормальизую")

        with open('config.ini', 'w') as config_file:
            config.write(config_file)



    form.pushButton_5.clicked.connect(checkboxUI)
    
    app.exec()
    return folder
