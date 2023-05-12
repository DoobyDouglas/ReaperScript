Для корректной работы всех функций, необходимо установить в систему python-reapy==0.10.0 и ffmpeg

ffmpeg лучше сразу прописать в PATH, но это не обязательно

Включаем REAPER, в консоли (например CMD) пишем python -c "import reapy; reapy.configure_reaper()"

После конфигурации REAPER, можно упаковать программу в .exe

pyinstaller --noconfirm --onefile --noconsole --hidden-import=asstosrt --add-data 'background.png;.' ReaperScript.py

