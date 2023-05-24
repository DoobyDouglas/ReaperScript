Конфигурация REAPER API:

1) В консоли: pip install python-reapy==0.10.0

2) Включаем REAPER, в консоли: python -c "import reapy; reapy.configure_reaper()"

Если падает DisabledDistAPIWarning, выключаем REAPER и повторяем шаг 2.

Если консоль зависает - попытайтесь сделать конфигурацию из самого REAPER.

Если падает UnicodeDecodeError:

Выключаем REAPER, находим файл конфигурации "REAPER.ini", по умолчанию он находится в "<Ваш локальный диск:> \Users\ <Ваше имя пользователя> \AppData\Roaming\REAPER".

Открываем файл в редакторе с кодировкой "utf-8", находим все строки с нечитаемыми символами и заменяем их на читаемые, можно парралельно открыть файл в обычном блокноте или редакторе с другой кодировкой, например windows-1251 и скопировать оттуда нужные строки. Сохраняем файл, включаем REAPER и повторяем шаг 2.

Если консоль перешла на новую строку - значит всё ок.

Для проверки: 
1) Перезапустите REAPER
2) Войдите в оболочку python
3) import reapy
4) reapy.test_api()

Приложение упаковано в ReaperScript.exe и для его работы не нужны дополнительные файлы.

Подробности о функионале можно узнать нажав на конпку "HELP".

