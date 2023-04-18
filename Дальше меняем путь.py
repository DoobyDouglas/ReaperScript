import win32gui
import win32con
import win32api
from reapy import reascript_api as RPR
import reapy
import time
import ctypes
import win32gui
import win32con

import win32api
import win32con
import win32gui
import ctypes

import win32gui
import win32con


reapy.perform_action(40015)
parent_hwnd = win32gui.FindWindow('#32770', 'Render to File')
if parent_hwnd != 0:
    child_hwnd = win32gui.FindWindowEx(parent_hwnd, None, 'Static', 'File name:')
    if child_hwnd != 0:
        while child_hwnd != 0:
            class_name_buffer = ctypes.create_unicode_buffer(100)
            window_text_buffer = ctypes.create_unicode_buffer(100)
            ctypes.windll.user32.GetClassNameW(child_hwnd, class_name_buffer, 100)
            ctypes.windll.user32.GetWindowTextW(child_hwnd, window_text_buffer, 100)
            if window_text_buffer.value == 'File name:':
                # Нашли нужный элемент, получаем его значение
                file_name_hwnd = win32gui.GetWindow(child_hwnd, win32con.GW_HWNDNEXT)
                file_name_buffer = ctypes.create_unicode_buffer(1000)
                win32gui.SendMessage(file_name_hwnd, win32con.WM_GETTEXT, 1000, file_name_buffer)
                file_name = file_name_buffer.value
                
                # Устанавливаем новое значение
                new_file_name = 'C:\\path\\to\\your\\file.wav'
                new_file_name_buffer = ctypes.create_unicode_buffer(new_file_name)
                win32gui.SendMessage(file_name_hwnd, win32con.WM_SETTEXT, None, new_file_name_buffer)
                
                print(f'Render file name: {file_name} -> {new_file_name}')
                break
            child_hwnd = ctypes.windll.user32.GetWindow(child_hwnd, win32con.GW_HWNDNEXT)
render = win32gui.GetDlgItem(parent_hwnd, 1)
win32gui.SendMessage(render, win32con.BM_CLICK, 0, 0)




