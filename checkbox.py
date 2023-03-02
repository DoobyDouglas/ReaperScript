import tkinter
import configparser


def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def save_options(
        checkboxes: dict,
        master: tkinter.Tk,
        config: configparser.ConfigParser
        ):
    save_button = tkinter.Button(
        master,
        text='Сохранить',
        command=master.destroy
    )
    save_button.grid(
        row=len(checkboxes),
        column=0
    )
    master.mainloop()
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def checkbox_window():
    master = tkinter.Tk()
    master.geometry("450x210")
    master.title('Выберите нужные опции')
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
    checkboxes = create_widgets(OPTIONS, master, config)
    save_options(checkboxes, master, config)


def create_widgets(
        OPTIONS: list,
        master: tkinter.Tk,
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
            master,
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


checkbox_window()
