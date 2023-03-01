import tkinter
import configparser


def save_options(checkboxes: dict, master):
    config = configparser.ConfigParser()
    config.read('config.ini')
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
        print(str(var.get()))
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def checkbox_window(master):
    master.geometry("400x110")
    master.title('Выберите нужные опции')
    OPTIONS = [
        'split',
        'normalize',
        'render',
    ]
    checkboxes = {}
    create_widgets(OPTIONS, checkboxes, master)


def create_widgets(OPTIONS: list, checkboxes: dict, master):
    config = configparser.ConfigParser()
    config.read('config.ini')
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
    save_options(checkboxes, master)


master = tkinter.Tk()
checkbox_window(master)
