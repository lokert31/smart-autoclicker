import config
import time
import random
import pyautogui
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller as KeyboardController, Listener
from datetime import datetime
import os
import json

# Управление мышью и клавиатурой
mouse = Controller()
keyboard = KeyboardController()

# Параметры из config.py
min_clicks = config.MIN_CLICKS
max_clicks = config.MAX_CLICKS

big_square_x_min = config.BIG_SQUARE_X_MIN
big_square_x_max = config.BIG_SQUARE_X_MAX
big_square_y_min = config.BIG_SQUARE_Y_MIN
big_square_y_max = config.BIG_SQUARE_Y_MAX
small_square_size = config.SMALL_SQUARE_SIZE

slow_down_enabled = config.SLOW_DOWN_ENABLED
slow_down_probability = config.SLOW_DOWN_PROBABILITY
slow_down_min_delay = config.SLOW_DOWN_MIN_DELAY
slow_down_max_delay = config.SLOW_DOWN_MAX_DELAY
slow_down_duration_min = config.SLOW_DOWN_DURATION_MIN
slow_down_duration_max = config.SLOW_DOWN_DURATION_MAX
slow_down_multiplier_min = config.SLOW_DOWN_MULTIPLIER_MIN
slow_down_multiplier_max = config.SLOW_DOWN_MULTIPLIER_MAX

cursor_change_probability = config.CURSOR_CHANGE_PROBABILITY

min_work_time = config.MIN_WORK_TIME
max_work_time = config.MAX_WORK_TIME
min_pause = config.MIN_PAUSE
max_pause = config.MAX_PAUSE

# Новые параметры из config.py
command_r_interval = config.COMMAND_R_INTERVAL
command_r_pause_range = config.COMMAND_R_PAUSE_RANGE

running = True
CLICKS_FILE = "clicks_data.json"
click_count_session = 0
click_count_total = 0

def load_click_count():
    global click_count_total
    if os.path.exists(CLICKS_FILE):
        with open(CLICKS_FILE, "r") as file:
            data = json.load(file)
            click_count_total = data.get("total_clicks", 0)
    else:
        click_count_total = 0

def save_click_count():
    global click_count_total
    with open(CLICKS_FILE, "w") as file:
        json.dump({"total_clicks": click_count_total}, file)

def get_random_small_square():
    x_min_square = random.randint(big_square_x_min, big_square_x_max - small_square_size)
    y_min_square = random.randint(big_square_y_min, big_square_y_max - small_square_size)
    x_max_square = x_min_square + small_square_size
    y_max_square = y_min_square + small_square_size
    return x_min_square, y_min_square, x_max_square, y_max_square

def move_cursor_smoothly(target_x, target_y, duration=0.5, steps=50):
    """
    Плавное перемещение курсора к указанным координатам.
    """
    start_x, start_y = mouse.position
    step_time = duration / steps

    for step in range(steps):
        current_x = start_x + (target_x - start_x) * (step + 1) / steps
        current_y = start_y + (target_y - start_y) * (step + 1) / steps
        mouse.position = (current_x, current_y)
        time.sleep(step_time)

def press_and_hold():
    hold_duration = random.uniform(0.03, 0.1)
    mouse.press(Button.left)
    time.sleep(hold_duration)
    mouse.release(Button.left)

def perform_command_r():
    print("Нажимаем Command + R через pyautogui")
    pyautogui.hotkey('command', 'r')  # Используем комбинацию клавиш
    pause_duration = random.uniform(*command_r_pause_range)  # Диапазон паузы
    print(f"Пауза после Command + R: {pause_duration:.2f} секунд")
    time.sleep(pause_duration)

def auto_clicker():
    global running, click_count_session, click_count_total
    load_click_count()
    print("Общее количество кликов (загружено):", click_count_total)
    
    current_square = get_random_small_square()
    next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)

    start_time = time.time()
    work_duration = random.randint(config.MIN_WORK_TIME, config.MAX_WORK_TIME)

    clicks_until_command_r = random.randint(*command_r_interval)  # Случайное количество кликов до Command + R
    slow_down_active = False
    slow_down_end_time = 0

    while running and (time.time() - start_time) < work_duration:
        # Проверяем необходимость смены квадрата
        if time.time() > next_square_change_time:
            new_square = get_random_small_square()
            target_x = random.randint(new_square[0], new_square[2])
            target_y = random.randint(new_square[1], new_square[3])

            print(f"Перемещение курсора в новый квадрат: ({target_x}, {target_y})")
            move_cursor_smoothly(target_x, target_y, duration=random.uniform(0.5, 1.5))

            current_square = new_square
            next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)
            pause_duration = random.randint(config.SQUARE_PAUSE_MIN_TIME, config.SQUARE_PAUSE_MAX_TIME)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Скрипт уходит на паузу перед продолжением кликов: {pause_duration} секунд.")
            time.sleep(pause_duration)

        # Проверяем вероятность активации замедления
        if slow_down_enabled and not slow_down_active and random.random() < slow_down_probability:
            slow_down_active = True
            slow_down_end_time = time.time() + random.uniform(slow_down_duration_min, slow_down_duration_max)
            slow_down_multiplier = random.uniform(slow_down_multiplier_min, slow_down_multiplier_max)
            print(f"Замедление активировано на {slow_down_end_time - time.time():.2f} секунд с множителем {slow_down_multiplier:.2f}.")

        # Отключаем замедление, если время истекло
        if slow_down_active and time.time() >= slow_down_end_time:
            slow_down_active = False
            print("Замедление деактивировано.")

        # Перемещаем курсор с вероятностью
        if random.random() < config.CURSOR_CHANGE_PROBABILITY:
            x = random.randint(current_square[0], current_square[2])
            y = random.randint(current_square[1], current_square[3])
            move_cursor_smoothly(x, y, duration=random.uniform(0.3, 0.7))

        # Нажимаем и отпускаем мышь
        press_and_hold()
        click_count_session += 1
        click_count_total += 1

        # Проверяем необходимость нажатия Command + R
        if click_count_session % clicks_until_command_r == 0:
            perform_command_r()
            clicks_until_command_r = random.randint(*command_r_interval)  # Пересчитываем до следующего раза

        # Печатаем количество кликов каждые 100
        if click_count_session % 100 == 0:
            print(f"Клики за сессию: {click_count_session}, общее количество кликов: {click_count_total}")

        # Рассчитываем задержку между кликами
        if slow_down_active:
            time.sleep(slow_down_multiplier / random.randint(min_clicks, max_clicks))
        else:
            time.sleep(1 / random.randint(min_clicks, max_clicks))

    print(f"Скрипт завершил работу. Клики за сессию: {click_count_session}")
    print(f"Общее количество кликов: {click_count_total}")
    save_click_count()

    # Пауза между подходами
    pause_duration = random.randint(min_pause, max_pause)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Пауза перед следующим подходом: {pause_duration} секунд.")
    time.sleep(pause_duration)

    # Запускаем следующий подход
    if running:
        main_thread()

def on_press(key):
    global running
    if key == Key.ctrl:  # Используем Control (не ctrl_l)
        running = False
        print(f"Скрипт остановлен. Клики за сессию: {click_count_session}")
        print(f"Общее количество кликов: {click_count_total}")
        save_click_count()
        return False  # Завершаем слушатель

def main_thread():
    t = threading.Thread(target=auto_clicker)
    t.start()

if __name__ == "__main__":
    while running:
        main_thread()  # Запуск следующего подхода
        with Listener(on_press=on_press) as listener:
            listener.join()
