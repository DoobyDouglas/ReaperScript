from typing import Dict
import configparser
import tkinter


def get_config() -> configparser.ConfigParser:
    """Функция для создания/получения файла конфигураций"""
    config = configparser.ConfigParser()
    config.read('REAPERSCRIPT.ini', encoding='utf-8')
    if 'PATHS' not in config:
        config['PATHS'] = {}
    if 'OPTIONS' not in config:
        config['OPTIONS'] = {}
    if 'SUBS' not in config:
        config['SUBS'] = {}
    return config


def save_path(name: str, path: str) -> None:
    """Функция для сохранения пути в файл конфигурации"""
    config = get_config()
    config['PATHS'][name] = path
    with open('REAPERSCRIPT.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def load_path(name: str) -> str or None:
    """Функция для загрузки пути из файла конфигурации"""
    config = get_config()
    try:
        path = config['PATHS'][name]
    except KeyError:
        path = None
    return path


def save_options(
        master: tkinter.Tk,
        checkboxes: Dict[str, str]
        ) -> None:
    """Функция для сохранения конфигураций"""
    config = get_config()
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    config['SUBS']['subs_lang'] = master.nametowidget('subs_lang').get()
    with open('REAPERSCRIPT.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def get_option(name: str) -> str or bool:
    """Функция для загрузки значения из файла конфигурации"""
    config = get_config()
    return config['OPTIONS'].getboolean(name)


if __name__ == '__main__':
    pass
