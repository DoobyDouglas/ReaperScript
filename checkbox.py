import tkinter
from tkinter import filedialog
import configparser
import os


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


def save_options(
        checkboxes: dict,
        window: tkinter.Tk,
        config: configparser.ConfigParser
        ):
    save_button = tkinter.Button(
        window,
        text='Сохранить',
        command=window.destroy
    )
    save_button.grid(
        row=len(checkboxes),
        column=0
    )
    window.mainloop()
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def create_widgets(
        OPTIONS: list,
        window: tkinter.Tk,
        config: configparser.ConfigParser
        ):
    checkboxes = {}
    if 'OPTIONS' not in config:
        config['OPTIONS'] = {}
    for i, option in enumerate(OPTIONS):
        var = tkinter.BooleanVar()
        if option in config['OPTIONS']:
            var.set(config['OPTIONS'].getboolean(option))
        else:
            var.set(False)
        checkbox = tkinter.Checkbutton(
            window,
            text=option,
            variable=var
        )
        checkbox.grid(
            row=i,
            column=0,
            sticky=tkinter.W
        )
        checkboxes[option] = var
    return checkboxes


def checkbox_window():
    window = tkinter.Tk()
    window.geometry('450x210')
    window.title('Выберите нужные опции')
    OPTIONS = [
        'dubbers_volume_up',
        'item_subs',
        'region_subs',
        'split',
        'normalize',
        'render_audio',
        'make_video',
    ]
    config = get_config()
    checkboxes = create_widgets(OPTIONS, window, config)
    save_options(checkboxes, window, config)


def reaper_check():
    """Функция для создания путей к компонентам REAPER"""
    reaper_path = load_path_from_config('reaper_path')
    if not reaper_path:
        reaper_path = filedialog.askopenfilename(
            title='Выберите файл reaper.exe'
        )
        save_path_to_config('reaper_path', reaper_path)
    project_path = load_path_from_config('project_path')
    if not project_path:
        project_path = filedialog.askopenfilename(
            title='Выберите файл шаблона проекта REAPER'
        )
        save_path_to_config('project_path', project_path)
    fx_chains_folder = load_path_from_config('fx_chains_folder')
    if not fx_chains_folder:
        fx_chains_folder = filedialog.askdirectory(
            title='Выберите папку с цепями эффектов'
        )
    save_path_to_config('fx_chains_folder', fx_chains_folder)


def choice_folder():
    """Функция для выбора рабочей папки с эпизодом"""
    folder = filedialog.askdirectory(
        title='Выберите рабочую папку с эпизодом'
    )
    return folder


checkbox_window()
tkinter.Tk().withdraw()
reaper_check()
choice_folder()
