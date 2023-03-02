from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication
import configparser
from tkinter import filedialog
import os


Form, Window = uic.loadUiType("MainWindow.ui")

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
window.show()

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not os.path.exists('config.ini'):
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

#рипер ехе
form.lineEdit_3.setText(load_path_from_config('reaper_path'))                   
def repear_exe():
    reaper_path = load_path_from_config('reaper_path')
    reaper_path = QtWidgets.QFileDialog.getOpenFileName(None,
        'Выбрать reaper.exe',
        'C:\Program Files',        
        'Exe file (reaper.exe)'
    )[0]
    save_path_to_config('reaper_path', reaper_path)
    form.lineEdit_3.setText(reaper_path)
    
form.pushButton_3.clicked.connect(repear_exe)

#шаблон
form.lineEdit_2.setText(load_path_from_config('project_path'))                
def project_folder():
    project_path = load_path_from_config('project_path')
    project_path = QtWidgets.QFileDialog.getOpenFileName(None,
        'Выберите файл шаблона проекта REAPER',
        None,
        'RPP file (*.rpp)'
    )[0]
    save_path_to_config('project_path', project_path)
    form.lineEdit_2.setText(project_path)
    
form.pushButton_2.clicked.connect(project_folder)

#FX
form.lineEdit.setText(load_path_from_config('fx_chains_folder'))                
def fx_folder():
    fx_chains_folder = load_path_from_config('fx_chains_folder')
    fx_chains_folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Выбор FX')
    save_path_to_config('fx_chains_folder', fx_chains_folder)
    form.lineEdit.setText(fx_chains_folder)
    
form.pushButton.clicked.connect(fx_folder)

#чекбоксы
def checkboxUI():

    config = get_config()
    config['OPTIONS'] = {}
    config['OPTIONS']['split'] = str(form.split.isChecked())
    config['OPTIONS']['normalize'] = str(form.normalize.isChecked())
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


form.pushButton_5.clicked.connect(checkboxUI)

app.exec()