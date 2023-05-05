Для корректной работы всех функций, необходимо установить в систему python-reapy==0.10.0 и ffmpeg

FFmpeg нужно прописать в PATH

Включаем REAPER, в консоли пишем python -c "import reapy; reapy.configure_reaper()"

После конфигурации REAPER, можно упаковать программу в .exe с помощью pyinstaller
pyinstaller --noconfirm --onefile --noconsole --hidden-import=asstosrt --add-data 'background.png;.' main.py

