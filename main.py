import config
import time
import random
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key
from datetime import datetime, timedelta
import os
import json

# Управление мышью
mouse = Controller()

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

def slow_down():
    if random.random() < slow_down_probability:
        slow_down_duration = random.randint(slow_down_duration_min, slow_down_duration_max)
        slow_down_delay = random.uniform(slow_down_min_delay, slow_down_max_delay)
        return slow_down_delay, slow_down_duration
    return 0, 0

def press_and_hold():
    hold_duration = random.uniform(0.03, 0.1)
    mouse.press(Button.left)
    time.sleep(hold_duration)
    mouse.release(Button.left)

def auto_clicker():
    global running, click_count_session, click_count_total
    load_click_count()
    print("Общее количество кликов (загружено):", click_count_total)
    
    current_square = get_random_small_square()
    next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)

    start_time = time.time()
    work_duration = random.randint(config.MIN_WORK_TIME, config.MAX_WORK_TIME)

    cursor_position = None

    while running and (time.time() - start_time) < work_duration:
        if time.time() > next_square_change_time:
            current_square = get_random_small_square()
            next_square_change_time = time.time() + random.randint(config.SQUARE_CHANGE_MIN_TIME, config.SQUARE_CHANGE_MAX_TIME)
            pause_duration = random.randint(config.SQUARE_PAUSE_MIN_TIME, config.SQUARE_PAUSE_MAX_TIME)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Скрипт уходит на паузу перед продолжением кликов: {pause_duration} секунд.")
            time.sleep(pause_duration)

        if random.random() < config.CURSOR_CHANGE_PROBABILITY:
            x = random.randint(current_square[0], current_square[2])
            y = random.randint(current_square[1], current_square[3])
            cursor_position = (x, y)
            mouse.position = cursor_position

        if cursor_position:
            press_and_hold()
            click_count_session += 1
            click_count_total += 1

        if click_count_session % 100 == 0:
            print(f"Клики за сессию: {click_count_session}, общее количество кликов: {click_count_total}")

        time.sleep(1 / random.randint(config.MIN_CLICKS, config.MAX_CLICKS))

    print(f"Скрипт завершил работу. Клики за сессию: {click_count_session}")
    print(f"Общее количество кликов: {click_count_total}")
    save_click_count()

    pause_duration = random.randint(config.MIN_PAUSE, config.MAX_PAUSE)
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
