Для создания exe файла следуй пошаговой инструкции:

1) скопируй gascontrol в корень C:/
и запусти в CMD команду pyinstaller gascontrol.py в папке его нахождения
2) скопируй из C:\gascontrol\dist\gascontrol\PyQt5\Qt\plugins\platforms файл qwindows.dll 
и помести в C:\gascontrol\dist\gascontrol\platforms (созадв при необходимости папку platforms)
3) скопируй и помести ui_gascontrol.ui и ui_gc_settings.ui в C:\gascontrol\dist\gascontrol
4) скопируй папку artsrc с содержимым в C:\gascontrol\artsrc

затем можно запускать программу gascontrol.exe из C:\gascontrol\dist\gascontrol