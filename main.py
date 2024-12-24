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

# Диапазон координат для рандомизации из config.py
x_min, x_max = config.X_MIN, config.X_MAX
y_min, y_max = config.Y_MIN, config.Y_MAX

# Флаг для работы автокликера
running = True

# Диапазон времени работы из config.py (в секундах)
min_work_time = config.MIN_WORK_TIME
max_work_time = config.MAX_WORK_TIME

# Диапазон случайных пауз между подходами из config.py
min_pause = config.MIN_PAUSE
max_pause = config.MAX_PAUSE

# Параметры спячки из config.py
sleep_enabled = config.SLEEP_ENABLED
sleep_start_time_str = config.SLEEP_START_TIME
sleep_end_time_str = config.SLEEP_END_TIME
sleep_shift_start_min = config.SLEEP_SHIFT_START_MIN
sleep_shift_start_max = config.SLEEP_SHIFT_START_MAX
sleep_shift_end_min = config.SLEEP_SHIFT_END_MIN
sleep_shift_end_max = config.SLEEP_SHIFT_END_MAX
sleep_shift_enabled = config.SLEEP_SHIFT_ENABLED

# Параметры замедления кликов из config.py
slow_down_enabled = config.SLOW_DOWN_ENABLED
slow_down_probability = config.SLOW_DOWN_PROBABILITY
slow_down_min_delay = config.SLOW_DOWN_MIN_DELAY
slow_down_max_delay = config.SLOW_DOWN_MAX_DELAY
slow_down_duration_min = config.SLOW_DOWN_DURATION_MIN
slow_down_duration_max = config.SLOW_DOWN_DURATION_MAX

# Множитель для уменьшения кликов
slow_down_multiplier_min = config.SLOW_DOWN_MULTIPLIER_MIN
slow_down_multiplier_max = config.SLOW_DOWN_MULTIPLIER_MAX

# Преобразуем время из строкового формата в объект времени
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

# Функция для проверки, нужно ли уходить в спячку
def should_sleep():
    if not sleep_enabled:
        return False

    current_time = datetime.now()
    
    # Преобразуем время начала и конца спячки из строкового формата
    sleep_start_time = parse_time(sleep_start_time_str)
    sleep_end_time = parse_time(sleep_end_time_str)

    # Сдвигаем время начала и конца спячки, если это разрешено
    if sleep_shift_enabled:
        sleep_start_time += timedelta(hours=random.randint(sleep_shift_start_min, sleep_shift_start_max))
        sleep_end_time += timedelta(hours=random.randint(sleep_shift_end_min, sleep_shift_end_max))

    # Если текущее время попадает в диапазон спячки, то возвращаем True
    if sleep_start_time.time() <= current_time.time() <= sleep_end_time.time():
        print(f"Скрипт в спячке с {sleep_start_time.strftime('%H:%M')} до {sleep_end_time.strftime('%H:%M')}")
        return True
    return False

# Функция замедления кликов
def slow_down():
    if random.random() < slow_down_probability:
        # Выбираем случайную длительность замедления
        slow_down_duration = random.randint(slow_down_duration_min, slow_down_duration_max)
        # Выбираем случайную задержку
        slow_down_delay = random.uniform(slow_down_min_delay, slow_down_max_delay)
        # Выбираем случайный множитель уменьшения кликов
        slow_down_multiplier = random.uniform(slow_down_multiplier_min, slow_down_multiplier_max)
        
        print(f"Замедление кликов на {slow_down_duration} секунд с задержкой {slow_down_delay:.2f} секунд и множителем {slow_down_multiplier:.2f}.")
        
        return slow_down_delay, slow_down_multiplier, slow_down_duration
    return 0, 1, 0  # Возвращаем задержку и множитель 1 (без замедления)

# Функция автокликера
def auto_clicker():
    global running
    # Храним текущую позицию мыши
    current_x = (x_min + x_max) // 2
    current_y = (y_min + y_max) // 2

    # Время работы (в секундах)
    work_duration = random.randint(min_work_time, max_work_time)

    start_time = time.time()  # Запоминаем время начала работы

    slow_down_delay = 0
    slow_down_multiplier = 1
    slow_down_duration = 0

    while running and (time.time() - start_time) < work_duration:
        # 95% вероятность оставить координаты неизменными
        if random.random() > 0.95:  # 5% вероятность смены координат
            current_x = random.randint(x_min, x_max)
            current_y = random.randint(y_min, y_max)

        # Применяем замедление, если оно включено
        if slow_down_enabled and slow_down_duration == 0:
            slow_down_delay, slow_down_multiplier, slow_down_duration = slow_down()

        # Случайная задержка для 10-15 кликов в секунду
        delay = 1 / random.randint(min_clicks, max_clicks)

        # Увеличиваем задержку, если было замедление
        delay += slow_down_delay

        # Корректируем количество кликов в секунду в зависимости от множителя замедления
        clicks_per_second = int(random.randint(min_clicks, max_clicks) * slow_down_multiplier)

        # Выполнение клика
        mouse.position = (current_x, current_y)
        mouse.click(Button.left, 1)

        # Задержка
        time.sleep(1 / clicks_per_second)

        # Отсчитываем время замедления
        if slow_down_duration > 0:
            slow_down_duration -= 1
            if slow_down_duration == 0:
                print("Замедление завершено")

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
        if not should_sleep():  # Проверяем, нужно ли уходить в спячку
            main_thread()
            with Listener(on_press=on_press) as listener:
                listener.join()
        else:
            time.sleep(60)  # Если в спячке, то проверяем каждый минуту
