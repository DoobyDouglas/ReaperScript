import configparser
import os


def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not os.path.exists('config.ini'):
        with open('config.ini', "w") as config_file:
            config.write(config_file)
    return config


def get_value_from_config(name: str):
    """Функция для загрузки значения из файла конфигурации"""
    config = get_config()
    try:
        value = config['OPTIONS'][name]
    except KeyError:
        value = None
    return value


value = get_value_from_config('dubbers_volume_up')
if value == 'True':
    print(value)

value = get_value_from_config('item_subs')
if value == 'True':
    print(value)
else:
    print(value)
