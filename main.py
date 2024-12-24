import config  # Импортируем настройки из config.py
import time
import random
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key
from datetime import datetime, timedelta

# Управление мышью
mouse = Controller()

# Параметры кликов из config.py
min_clicks = config.MIN_CLICKS
max_clicks = config.MAX_CLICKS

# Параметры для случайной генерации координат
big_square_x_min = config.BIG_SQUARE_X_MIN
big_square_x_max = config.BIG_SQUARE_X_MAX
big_square_y_min = config.BIG_SQUARE_Y_MIN
big_square_y_max = config.BIG_SQUARE_Y_MAX
small_square_size = config.SMALL_SQUARE_SIZE  # Размер маленьких квадратов

# Параметры замедления кликов
slow_down_enabled = config.SLOW_DOWN_ENABLED
slow_down_probability = config.SLOW_DOWN_PROBABILITY
slow_down_min_delay = config.SLOW_DOWN_MIN_DELAY
slow_down_max_delay = config.SLOW_DOWN_MAX_DELAY
slow_down_duration_min = config.SLOW_DOWN_DURATION_MIN
slow_down_duration_max = config.SLOW_DOWN_DURATION_MAX
slow_down_multiplier_min = config.SLOW_DOWN_MULTIPLIER_MIN
slow_down_multiplier_max = config.SLOW_DOWN_MULTIPLIER_MAX

# Параметры работы автокликера
min_work_time = config.MIN_WORK_TIME
max_work_time = config.MAX_WORK_TIME
min_pause = config.MIN_PAUSE
max_pause = config.MAX_PAUSE

# Флаг для работы автокликера
running = True

# Функция для выбора случайного маленького квадрата внутри большого
def get_random_small_square():
    # Генерация случайных координат для маленького квадрата
    x_min_square = random.randint(big_square_x_min, big_square_x_max - small_square_size)
    y_min_square = random.randint(big_square_y_min, big_square_y_max - small_square_size)
    x_max_square = x_min_square + small_square_size
    y_max_square = y_min_square + small_square_size
    return x_min_square, y_min_square, x_max_square, y_max_square

# Функция замедления кликов
def slow_down():
    if random.random() < slow_down_probability:
        # Выбираем случайную длительность замедления
        slow_down_duration = random.randint(slow_down_duration_min, slow_down_duration_max)
        # Выбираем случайную задержку
        slow_down_delay = random.uniform(slow_down_min_delay, slow_down_max_delay)
        return slow_down_delay, slow_down_duration
    return 0, 0  # Без замедления

# Функция автокликера
def auto_clicker():
    global running
    start_time = time.time()  # Запоминаем время начала работы

    # Время работы (в секундах)
    work_duration = random.randint(min_work_time, max_work_time)

    # Таймер для смены маленького квадрата
    next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)
    current_square = get_random_small_square()

    # Время работы (в секундах)
    slow_down_delay, slow_down_duration = 0, 0

    while running and (time.time() - start_time) < work_duration:
        # Проверяем, нужно ли менять маленький квадрат
        if time.time() > next_square_change_time:
            # Сменить квадрат и установить время для следующей смены
            current_square = get_random_small_square()
            next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)
            print(f"Сменили квадрат на: {current_square}")
            
            # Пауза после смены квадрата
            pause_duration = random.randint(config.SQUARE_PAUSE_MIN_TIME, config.SQUARE_PAUSE_MAX_TIME)
            print(f"Пауза после смены квадрата: {pause_duration} секунд")
            time.sleep(pause_duration)
        
        # Выбираем случайные координаты внутри текущего маленького квадрата
        x = random.randint(current_square[0], current_square[2])
        y = random.randint(current_square[1], current_square[3])

        # Замедление, если оно включено
        slow_down_delay, slow_down_duration = slow_down()

        # Выполнение клика
        mouse.position = (x, y)
        mouse.click(Button.left, 1)

        # Задержка между кликами с учетом замедления
        time.sleep(1 / random.randint(min_clicks, max_clicks) + slow_down_delay)

        # Если время замедления истекло, то выключаем замедление
        if slow_down_duration > 0:
            slow_down_duration -= 1
            if slow_down_duration == 0:
                print("Замедление завершено.")

    # Пауза между подходами (в секундах)
    pause_duration = random.randint(min_pause, max_pause)
    print(f"Пауза перед следующим подходом: {pause_duration} секунд.")
    time.sleep(pause_duration)

# Функция для отслеживания сочетания клавиш
def on_press(key):
    global running
    if key == Key.ctrl_l:  # Проверяем нажатие Ctrl (левая клавиша)
        running = False  # Останавливаем программу
        print("Скрипт остановлен!")
        return False  # Завершаем слушатель клавиш

# Запуск автокликера в отдельном потоке
def main_thread():
    t = threading.Thread(target=auto_clicker)
    t.start()

# Основной код
if __name__ == "__main__":
    while running:
        main_thread()
        with Listener(on_press=on_press) as listener:
            listener.join()
