HOW_TO_USE = (
    'REAPERSCRIPT работает с оригинальной версией REAPER без русификатора.\n'
    '\n'
    'В окне REAPER\'а нажимите "Options" → "Preferences...".\n'
    'Откроется окно "REAPER Preferences". В окне "REAPER Preferences":\n'
    'Во вкладке "Media" уберите чекбокс "show status window",\n'
    'уберите чекбокс '
    '"set media items offline when application is not active".\n'
    'Нажмите "ОК".\n'
    '\n'
    'Создайте шаблон проекта, в нём должно быть только 2 трека:\n'
    '1) обычный трек, на который будет загружаться видео\n'
    '2) трек "folder", в который будут складываться все дороги дабберов\n'
    '\n'
    'Добавьте необходимые посылы и эффекты на эти 2 трека.\n'
    'Если планируете использовать функцию рендера,\n'
    'нужно выполнить рендер из этого проекта с настройками,\n'
    'которые будут использоваться в дальнейшем.\n'
    'Обязательно выделите только 2-ой трек, затем:\n'
    '"File" → "Project templates" → "Save project as template...".\n'
    'Сохраните шаблон в любое удобное место.\n'
    'С помощью кнопки "TEMPLATE" выберите этот шаблон.\n'
    '\n'
    'Нажав на кнопку "RFXCHAINS" можно выбрать папку с цепями эффектов.\n'
    'Имена цепей должны находиться в названиях дорог,\n'
    'без учёта регистра и пробелов.\n'
    'Например:\n'
    'Если файл называется "что-то_там озвучил_ЧеловЕк_ПАук и_вот.wave",\n'
    'то на эту дорогу добавится цепь с именем "ЧеЛОвек ПауК.RfxChain".\n'
    'На дорогу с названием "озвучил ЧелОвЕк ПАук и вот.flac" - тоже.\n'
    '\n'
    'Теперь REAPERSCRIPT запомнил пути к шаблону и цепям эффектов,\n'
    'при повторном запуске, нажимать на соответствующие кнопки,\n'
    'нужно только если изменились места хранения шаблона или цепей.\n'
    '\n'
    'Путь от корня локального диска до папки с материалами для серии,\n'
    'должен включать в себя как минимум ещё одну промежуточную папку.\n'
    'Например:\n'
    '"A:/название тайтла/номер серии/<тут файлы>".\n'
    '\n'
    'Это нужно для изменения имени видео, REAPER часто не загружает файлы,\n'
    'если они называются только на незнакомом ему языке.\n'
    'Таким образом, файл "A:/Гайвер/09/強殖装甲ガイバー.mkv",\n'
    'превратится в "A:/Гайвер/09/Гайвер 09.mkv".\n'
    '\n'
    'После расстановки нужных чекбоксов,\n'
    'нажмите на "START" и выберите папку с материалами для серии.\n'
    'Выбранные ранее чекбоксы, останутся такими при повторном запуске.\n'
    '\n'
    'Кнопка "FIXCHECK" проверяет проект в активной вкладке.\n'
    'Как и в случае с чекбоксом "fix_check",\n'
    'для корректной работы нужно использовать "split" на дорогах дабберов.\n'
    '\n'
    'Шаблон "NR TEMPLATE", для функции "noise_reduction",\n'
    'должен содержать только "мастер трек" '
    'с Вашим пресетом для удаления шума.\n'
    'Рекомендуется:\n'
    'В меню "File" → "Render...", в окне "Render to File",\n'
    'установить чекбокс "silently internet file names to avoid overwriting".\n'
    '\n'
    'REAPERSCRIPT принимает на вход:\n'
    'аудио в форматах ".flac" и ".wave"\n'
    'видео в форматах ".mkv" и ".mp4"\n'
    'субтитры в форматах ".ass", ".srt", "vtt"\n'
    '\n'
    'Нечитаемые расширения для аудио преобразуются в читаемые.\n'
    'Например:\n'
    'Файл с расширением ".flac420BPM" станет обычным ".flac".\n'
    '\n'
    'Если внутри видео есть субтитры,\n'
    'REAPERSCRIPT их достанет и добавит в проект.\n'
    'Сначала извлекаются субтитры из меню '
    '"Select subtitles to extract:",\n'
    'если их нет - то английские.\n'
    'В случае, когда нет ни того, ни другого - извлекаются первые доступные.\n'
    'Для работы этой функции в системе должен быть ffmpeg.\n'
    '\n'
    'Для работы функции "render_video" в системе должен быть ffmpeg.\n'
    '\n'
    'Для работы функций нормализации нужно "SWS/S&M EXTENSION".\n'
    '\n'
    'Подробности об отдельных функциях можно узнать во всплывающем тексте.'
)
NOIZE_REDUCTION = ('Очищает дороги дабберов от шума. '
                   'Для корректной работы нужно выбрать шаблон в "NR TEMP".')
SPLIT = 'Использует последний пресет Dynamic split items'
NORM_D = ('Использует SWS/BR: Normalize loudness of selected items to -23 '
          'LUFS для айтемов дабберов')
NORM_V = ('Использует SWS/BR: Normalize loudness of selected items to -23 '
          'LUFS для видео айтема')
VOLUME_UP = 'Поднимает громкость дабберов на 3.5 дБ'
SUB_ITEM = 'Добавляет субтитры айтемы'
SUB_REGION = 'Добавляет субтитры регионы'
SUBS_CLEANER = 'Удаляет из субтитров надписи и песни'
FIX_CHECK = ('Проверяет проект на наличие пропусков и даблов. '
             'Для корректной работы необходимо использовать "split"')
RENDER_A = 'Рендерит звук, используя пресет рендера сохранённый в шаблоне'
RENDER_V = ('Создаёт видео с исходным расширением и отрендеринным звуком, '
            'конвертируя его в ".aac"')
START = 'Выбрать папку и начать работу'
TEMPLATE = 'Выбрать шаблон проекта REAPER'
RFXCHAINS = 'Выбрать папку с цепями эффектов'
FIXCHECK_SRANDALONE = 'Проверить на фиксы активный проект'
NR_TEMP = 'Выбрать шаблон проекта REAPER для удаления шума'
SUBS_LANG = 'Язык субтитров'
ADD_TRACK_FOR_SUBS = 'Добавляет отдельный трек для субтитров'
HIDE_REAPER = 'Сворачивает основное окно REAPER после начала работы'
HELP = 'Помощь'
HELP_DICT = {
    'split': SPLIT,
    'normalize_dubbers': NORM_D,
    'normalize_video': NORM_V,
    'volume_up_dubbers': VOLUME_UP,
    'sub_item': SUB_ITEM,
    'sub_region': SUB_REGION,
    'subs_cleaner': SUBS_CLEANER,
    'fix_check': FIX_CHECK,
    'render_audio': RENDER_A,
    'render_video': RENDER_V,
    'start': START,
    'template': TEMPLATE,
    'rfx': RFXCHAINS,
    'fixcheck_standalone': FIXCHECK_SRANDALONE,
    'help': HELP,
    'noise_reduction': NOIZE_REDUCTION,
    'nrtemplate': NR_TEMP,
    'subs_lang': SUBS_LANG,
    'add_track_for_subs': ADD_TRACK_FOR_SUBS,
    'hide_reaper': HIDE_REAPER,
}
MANY_VIDEO = 'Оставьте в рабочей папке только нужный видеофайл'
MANY_SUBS = 'Оставьте в рабочей папке только нужный файл субтитров'
NO_VIDEO = 'В рабочей папке нет видеофайлов подходящего формата'
NO_AUDIO = 'В рабочей папке нет аудиофайлов подходящего формата'
NO_FOLDER = 'Рабочая папка не выбрана'
IN_USE = 'Закройте приложения использующие рабочие файлы'
