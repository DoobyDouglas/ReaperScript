from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication
from nufile import (
    keyboard_check,
    reaper_run,
    file_works,
    project_save,
    import_subs_items,
    audio_select,
    video_select,
    import_subs,
    get_info_values,
    split,
    normalize,
    render,
    reaper_close,
    audio_convert,
    make_episode,
    save_path_to_config,
    load_path_from_config,
    )
import configparser
import os
import reapy
import tkinter


# настройка конфига
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

    # рипер ехе
    def repear_exe():
        reaper_path = load_path_from_config('reaper_path')
        reaper_path = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Выбрать reaper.exe',
            r'C:\Program Files',
            'Exe file (reaper.exe)'
        )[0]
        if not reaper_path:
            pass
        else:
            save_path_to_config('reaper_path', reaper_path)
            form.lineEdit_3.setText(reaper_path)

    form.pushButton_3.clicked.connect(repear_exe)

    # шаблон
    def project_folder():
        project_path = load_path_from_config('project_path')
        project_path = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Выберите файл шаблона проекта REAPER',
            None,
            'RPP file (*.rpp)'
        )[0]
        if not project_path:
            pass
        save_path_to_config('project_path', project_path)
        form.lineEdit_2.setText(project_path)

    form.pushButton_2.clicked.connect(project_folder)

    # FX
    def fx_folder():
        fx_chains_folder = load_path_from_config('fx_chains_folder')
        fx_chains_folder = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            'Выбор FX'
        )
        if not fx_chains_folder:
            pass
        save_path_to_config('fx_chains_folder', fx_chains_folder)
        form.lineEdit.setText(fx_chains_folder)

    form.pushButton.clicked.connect(fx_folder)

    # Рабочая папка
    def choice_folder():
        set_file = load_path_from_config('folder_file')
        global folder
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            'Рабочая папка',
            set_file
        )
        form.lineEdit_4.setText(folder)
        return folder

    form.pushButton_4.clicked.connect(choice_folder)

    # Настройка сохранение рабочей папки
    def setting_folder():
        const_workfolder = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            'Рабочая папка'
        )
        save_path_to_config('folder_file', const_workfolder)

    form.pushButton_6.clicked.connect(setting_folder)

    # считывание и расстановка чекбоксов
    config = create_config()
    form.checkBox.setChecked(bool(config['OPTIONS']['split']))
    form.checkBox_2.setChecked(bool(config['OPTIONS']['normalize']))
    form.checkBox_3.setChecked(bool(config['OPTIONS']['normalize_video']))
    form.checkBox_4.setChecked(bool(config['OPTIONS']['volume']))
    form.checkBox_5.setChecked(bool(config['OPTIONS']['sub_item']))
    form.checkBox_6.setChecked(bool(config['OPTIONS']['sub_region']))
    form.checkBox_7.setChecked(bool(config['OPTIONS']['render_audio']))
    form.checkBox_8.setChecked(bool(config['OPTIONS']['render_video']))

    def checkboxUI():
        config = create_config()
        flac_audio, wav_audio, mkv_video, mp4_video, subs = file_works(folder)
        reaper_run()
        project = reapy.Project()
        project_save(folder)

        if form.checkBox_5.isChecked():
            config['OPTIONS']['sub_item'] = '1'
            import_subs_items(subs)
        else:
            config['OPTIONS']['sub_item'] = ' '

        if form.checkBox_4.isChecked():
            config['OPTIONS']['volume'] = '1'
        else:
            config['OPTIONS']['volume'] = ' '

        audio_select(flac_audio, wav_audio)
        video_select(mkv_video, mp4_video)

        if form.checkBox_6.isChecked():
            config['OPTIONS']['sub_region'] = '1'
            import_subs(subs)
        else:
            config['OPTIONS']['sub_region'] = ' '

        project.save(False)
        video_item, split_sleep, lenght = get_info_values()

        if form.checkBox.isChecked():
            config['OPTIONS']['split'] = '1'
            split(video_item, split_sleep)
        else:
            config['OPTIONS']['split'] = ' '

        if form.checkBox_2.isChecked():
            config['OPTIONS']['normalize'] = '1'
            normalize(video_item)
        else:
            config['OPTIONS']['normalize'] = ' '

        if form.checkBox_3.isChecked():
            config['OPTIONS']['normalize_video'] = '1'
            normalize(video_item)
        else:
            config['OPTIONS']['normalize_video'] = ' '

        project.save(False)

        if form.checkBox_7.isChecked():
            config['OPTIONS']['render_audio'] = '1'
            render(folder)
            reaper_close(lenght)
        else:
            config['OPTIONS']['render_audio'] = ' '

        if form.checkBox_8.isChecked():
            config['OPTIONS']['render_video'] = '1'
            audio_convert(folder)
            make_episode(folder, mkv_video, mp4_video)
        else:
            config['OPTIONS']['render_video'] = ' '

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    form.pushButton_5.clicked.connect(checkboxUI)
    app.exec()
    return folder


if __name__ == '__main__':
    tkinter.Tk().withdraw()
    keyboard_check()
    start()
