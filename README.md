Для корректной работы всех функций, необходимо установить в систему python-reapy==0.10.0

Включаем REAPER, в консоли пишем python -c "import reapy; reapy.configure_reaper()"

После конфигурации REAPER, можно упаковать программу в .exe с помощью команды pyinstaller script.py
Файл script.exe будет по адресу dist\script\
