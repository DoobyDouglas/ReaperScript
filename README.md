Конфигурация REAPER API

1) В консоли: pip instal lpython-reapy==0.10.0

2) Включаем REAPER, в консоли: python -c "import reapy; reapy.configure_reaper()"

Если падает DisabledDistAPIWarning, выключаем REAPER и повторяем шаг 2.

Если консоль зависает - попытайтесь сделать конфигурацию из самого REAPER.

Если консоль перешла на новую строку - значит всё ок.

Для проверки: 
1) Перезапустите REAPER
2) Войдите в оболочку python
3) import reapy
4) reapy.test_api()

Приложение упаковано в ReaperScript.exe и для его работы не нужны дополнительные файлы.

