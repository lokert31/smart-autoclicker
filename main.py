import config  # Импортируем настройки из config.py
import time
import random
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key
from datetime import datetime, timedelta
import os  # Для работы с файлом
import json  # Для сохранения данных в файл



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

# Добавляем вероятность смены позиции курсора
cursor_change_probability = config.CURSOR_CHANGE_PROBABILITY

# Параметры работы автокликера
min_work_time = config.MIN_WORK_TIME
max_work_time = config.MAX_WORK_TIME
min_pause = config.MIN_PAUSE
max_pause = config.MAX_PAUSE

# Флаг для работы автокликера
running = True

# Файл для хранения общего количества кликов
CLICKS_FILE = "clicks_data.json"

# Глобальные переменные для подсчета кликов
click_count_session = 0  # Количество кликов за текущий запуск
click_count_total = 0  # Общее количество кликов

# Функция для загрузки общего количества кликов из файла
def load_click_count():
    global click_count_total
    if os.path.exists(CLICKS_FILE):
        with open(CLICKS_FILE, "r") as file:
            data = json.load(file)
            click_count_total = data.get("total_clicks", 0)
    else:
        click_count_total = 0

# Функция для сохранения общего количества кликов в файл
def save_click_count():
    global click_count_total
    with open(CLICKS_FILE, "w") as file:
        json.dump({"total_clicks": click_count_total}, file)

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

# Обновленная функция автокликера
def auto_clicker():
    global running, click_count_session, click_count_total
    # Загрузка общего количества кликов
    load_click_count()
    print("Общее количество кликов (загружено):", click_count_total)

    # Генерация первого маленького квадрата
    current_square = get_random_small_square()
    print(f"Первый квадрат выбран: {current_square}")

    # Устанавливаем время до следующей смены квадрата
    next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)

    # Время работы автокликера
    start_time = time.time()
    work_duration = random.randint(config.MIN_WORK_TIME, config.MAX_WORK_TIME)

    # Флаг для контроля обновления позиции курсора
    cursor_position = None  # Начальная позиция не установлена

    # Основной цикл автокликера
    while running and (time.time() - start_time) < work_duration:
        # Проверяем, нужно ли менять квадрат
        if time.time() > next_square_change_time:
            # Смена квадрата
            current_square = get_random_small_square()
            next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)
            print(f"Квадрат изменен на: {current_square}")

            # Пауза перед началом кликов
            pause_duration = random.randint(config.SQUARE_PAUSE_MIN_TIME, config.SQUARE_PAUSE_MAX_TIME)
            print(f"Скрипт уходит на паузу перед продолжением кликов: {pause_duration} секунд.")
            time.sleep(pause_duration)

        # Вероятность изменения позиции курсора
        if random.random() < config.CURSOR_CHANGE_PROBABILITY:
            # Случайные координаты внутри текущего квадрата
            x = random.randint(current_square[0], current_square[2])
            y = random.randint(current_square[1], current_square[3])
            cursor_position = (x, y)
            mouse.position = cursor_position

        # Если курсор не изменился, используем последнюю известную позицию
        if cursor_position:
            mouse.click(Button.left, 1)

            # Увеличение счетчиков кликов
            click_count_session += 1
            click_count_total += 1

        # Выводим прогресс работы (можно убрать или настроить)
        if click_count_session % 100 == 0:
            print(f"Клики за сессию: {click_count_session}, общее количество кликов: {click_count_total}")

        # Задержка между кликами
        time.sleep(1 / random.randint(config.MIN_CLICKS, config.MAX_CLICKS))

    # Работа завершена, выводим итог и уходим на общую паузу
    print(f"Скрипт завершил работу. Клики за сессию: {click_count_session}")
    print(f"Общее количество кликов: {click_count_total}")

    # Сохраняем общий счетчик кликов
    save_click_count()

    # Пауза между подходами
    pause_duration = random.randint(config.MIN_PAUSE, config.MAX_PAUSE)
    print(f"Пауза перед следующим подходом: {pause_duration} секунд.")
    time.sleep(pause_duration)




# Функция для отслеживания сочетания клавиш
def on_press(key):
    global running
    if key == Key.ctrl_l:  # Проверяем нажатие Ctrl (левая клавиша)
        running = False  # Останавливаем программу
        print(f"Скрипт остановлен. Клики за сессию: {click_count_session}")
        print(f"Общее количество кликов: {click_count_total}")
        save_click_count()  # Сохраняем общее количество кликов
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
