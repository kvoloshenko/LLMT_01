'''
Перезапуск colab нотебука.

Предварительно:
   назначить комбинацию Ctrl+F7 на действие Restart runtime.

Использование:
   Colab нотебук должен быть открытым.
   Запускаем этот код Python и сразу переходим в окно браузера с открытым нотебуком.

'''

import time
import pyautogui
import datetime

# Функция для перезапуска сессии Colab
def restart_colab():
    time.sleep(20)

    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Format the date and time as a string
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    print(formatted_datetime)

    # Нажимаем на кнопку Ctrl+F7 "Restart runtime" - Эту комбинацию нужно назначить в нотебуке !!!
    pyautogui.hotkey('ctrl', 'F7')
    print('Ctrl+F7 "Restart runtime"')
    time.sleep(2)

    # Подтверждаем перезапуск
    pyautogui.press('enter')
    print('enter"')
    time.sleep(10)

    # Нажимаем на кнопку Ctrl+F9 "Run all"
    pyautogui.hotkey('ctrl', 'F9')
    print('Ctrl+F9 "Run all"')
    time.sleep(2)


# Задаем интервал перезапуска в секундах (например, каждые 12 часов)
# restart_interval = 12 * 60 * 60
restart_interval = 3 * 60 * 60
# restart_interval = 20

# Главный цикл, который будет перезапускать сессию каждые несколько часов
while True:
    restart_colab()
    time.sleep(restart_interval)
