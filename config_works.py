from typing import Dict
import configparser
import tkinter


def get_config() -> configparser.ConfigParser:
    """Функция для создания/получения файла конфигураций"""
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config


def save_path(name: str, path: str) -> None:
    """Функция для сохранения пути в файл конфигурации"""
    config = get_config()
    if 'PATHS' not in config:
        config['PATHS'] = {}
    config['PATHS'][name] = path
    with open('config.ini', 'w', encoding='utf-8') as config_file:
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
        checkboxes: Dict[str, str],
        master: tkinter.Tk,
        config: configparser.ConfigParser,
        text_input: tkinter.Entry
        ) -> None:
    """Функция для сохранения конфигураций"""
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    config['OUTPUT']['audio_output_format'] = text_input.get()
    with open('config.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)
    #master.destroy()


def get_option(name: str) -> str or bool:
    """Функция для загрузки значения из файла конфигурации"""
    config = get_config()
    if name == 'audio_output_format':
        return config['OUTPUT'][name]
    else:
        return config['OPTIONS'].getboolean(name)


if __name__ == '__main__':
    pass
