from reapy import reascript_api as RPR
import reapy
import time
import ctypes
import win32gui
import win32con

def render(folder: str) -> None:
    """Функция для рендеринга файла"""
    if True:
        reapy.perform_action(40015)
        parent_hwnd = win32gui.FindWindow('#32770', 'Render to File')
        while not parent_hwnd:
            time.sleep(0.1)
            parent_hwnd = win32gui.FindWindow('#32770', 'Render to File')
        child_hwnd = win32gui.FindWindowEx(parent_hwnd, None, 'Static', 'File name:')
        file_name_hwnd = win32gui.GetWindow(child_hwnd, win32con.GW_HWNDNEXT)
        new_file_name_buffer = ctypes.create_unicode_buffer('audio')
        win32gui.SendMessage(file_name_hwnd, win32con.WM_SETTEXT, None, new_file_name_buffer)
        child_hwnd = win32gui.FindWindowEx(parent_hwnd, None, 'Static', 'Directory:')
        file_name_hwnd = win32gui.GetWindow(child_hwnd, win32con.GW_HWNDNEXT)
        new_file_name_buffer = ctypes.create_unicode_buffer(folder)
        win32gui.SendMessage(file_name_hwnd, win32con.WM_SETTEXT, None, new_file_name_buffer)
    
    render = win32gui.GetDlgItem(parent_hwnd, 1)
    #win32gui.SendMessage(render, win32con.BM_CLICK, 0, 0)

render('Z:\\test\\')