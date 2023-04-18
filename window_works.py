from PIL import Image, ImageTk
from typing import Dict
import configparser
import tkinter


def get_config() -> configparser.ConfigParser:
    """Функция для создания/получения файла конфигураций"""
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config


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
    master.destroy()


def on_closing():
    raise SystemExit


def create_widgets(
        OPTIONS: list,
        master: tkinter.Tk,
        config: configparser.ConfigParser
        ) -> None:
    """Функция для создания списка конфигураций"""
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
            master,
            text=option,
            variable=var,
            background='#ffc0cb',
            bd=3,
            pady=3,
            activebackground='#ffc0cb'
        )
        checkbox.grid(
            row=i,
            column=0,
            sticky=tkinter.W
        )
        checkboxes[option] = var
    if 'OUTPUT' not in config:
        config['OUTPUT'] = {}
    label = tkinter.Label(
        master,
        text='Audio Output Format:',
        background='#ffc0cb',
    )
    label.grid(
        row=len(OPTIONS),
        column=0,
        sticky=tkinter.W,
        padx=3,
        pady=3
    )
    text_input = tkinter.Entry(
        master,
        width=6,
        background='#ffffff',
        bd=3
    )
    text_input.grid(
        row=len(OPTIONS),
        column=1,
        sticky=tkinter.W,
        padx=3,
        pady=3
        )
    if 'audio_output_format' in config['OUTPUT']:
        text_input.insert(tkinter.END, config['OUTPUT']['audio_output_format'])
    save_button = tkinter.Button(
        master,
        text='Сохранить',
        background='#9b93b3',
        activebackground='#9b93b3',
        command=lambda: save_options(checkboxes, master, config, text_input)
    )
    save_button.place(relx=0.5, rely=1.0, anchor="s", y=-9)
    master.mainloop()


def checkbox_window() -> None:
    """Функция для создания окна выбора конфигураций"""
    master = tkinter.Tk()
    width = 380
    height = 390
    s_width = master.winfo_screenwidth()
    s_height = master.winfo_screenheight()
    upper = s_height // 8
    x = (s_width - width) // 2
    y = (s_height - height) // 2
    master.geometry(f'{width}x{height}+{x}+{y - upper}')
    master.resizable(width=False, height=False)
    width = master.winfo_screenwidth()
    height = master.winfo_screenheight()
    x = (width - 380) // 2
    y = (height - 390) // 2
    master.title('Выберите нужные опции')
    img = Image.open('background.png')
    tk_img = ImageTk.PhotoImage(img)
    background_label = tkinter.Label(master, image=tk_img)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    master.protocol('WM_DELETE_WINDOW', on_closing)
    OPTIONS = [
        'split',
        'normalize',
        'normalize_dubbers',
        'normalize_video',
        'volume_up_dubbers',
        'sub_item',
        'sub_region',
        'fix_check',
        'render_audio',
        'render_video',
    ]
    config = get_config()
    create_widgets(OPTIONS, master, config)


def save_path_to_config(name: str, path: str) -> None:
    """Функция для сохранения пути в файл конфигурации"""
    config = get_config()
    if 'PATHS' not in config:
        config['PATHS'] = {}
    config['PATHS'][name] = path
    with open('config.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def load_path_from_config(name: str) -> str or None:
    """Функция для загрузки пути из файла конфигурации"""
    config = get_config()
    try:
        path = config['PATHS'][name]
    except KeyError:
        path = None
    return path


def get_value(name: str) -> str or bool:
    """Функция для загрузки значения из файла конфигурации"""
    config = get_config()
    if name == 'audio_output_format':
        return config['OUTPUT'][name]
    else:
        return config['OPTIONS'].getboolean(name)


if __name__ == '__main__':
    pass
