import random
import math

LED_ROWS = 2
LED_COLS = 16

MIN_ALPHA = 5
MAX_ALPHA = 20

def pattern_wave_vertical(step, brightness_scale=1.0):
    frame = []
    frequency = 2 * math.pi / LED_COLS
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            brightness = (math.sin(frequency * (col + step)) + 1) / 2  # 0..1 sine wave
            brightness *= brightness_scale
            val_r = int(255 * brightness)
            val_b = 255 - val_r
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if val_r > 0 else 0
            row_colors.append({"r": val_r, "g": 0, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_zigzag(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            on = ((row + col + step) % 4) < 2
            val = 255 if on else 0
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
            row_colors.append({"r": val, "g": val, "b": 0, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_strobe_random(step, brightness_scale=1.0):
    frame = []
    random.seed(step)
    for row in range(LED_ROWS):
        row_colors = []
        for _ in range(LED_COLS):
            on = random.random() > 0.5
            val = 255 if on else 0
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
            row_colors.append({"r": val, "g": val, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_spiral(step, brightness_scale=1.0):
    total_leds = LED_ROWS * LED_COLS
    frame = [[{"r":0, "g":0, "b":0, "a":0} for _ in range(LED_COLS)] for _ in range(LED_ROWS)]
    pos = step % total_leds
    row = pos // LED_COLS
    col = pos % LED_COLS
    alpha = random.randint(MIN_ALPHA, MAX_ALPHA)
    frame[row][col] = {"r": 255, "g": 0, "b": 255, "a": alpha}
    return frame

def pattern_gradient_rainbow(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            hue = ((col * 360 / LED_COLS) + (step * 10)) % 360
            r, g, b = hsv_to_rgb(hue, 1.0, brightness_scale)
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA)
            row_colors.append({"r": r, "g": g, "b": b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_bouncing_dot(step, brightness_scale=1.0):
    frame = [[{"r":0, "g":0, "b":0, "a":0} for _ in range(LED_COLS)] for _ in range(LED_ROWS)]
    period = 2 * (LED_COLS - 1)
    pos = step % period
    if pos >= LED_COLS:
        pos = period - pos
    for row in range(LED_ROWS):
        brightness = 255 if row == step % LED_ROWS else 0
        alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if brightness > 0 else 0
        frame[row][pos] = {"r": brightness, "g": brightness, "b": 0, "a": alpha}
    return frame

def pattern_fading_left_to_right(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            distance = (col - step) % LED_COLS
            brightness = max(0, 1 - distance / LED_COLS) * brightness_scale
            val = int(255 * brightness)
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if val > 0 else 0
            row_colors.append({"r": val, "g": val, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_fading_right_to_left(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            distance = (step - col) % LED_COLS
            brightness = max(0, 1 - distance / LED_COLS) * brightness_scale
            val = int(255 * brightness)
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if val > 0 else 0
            row_colors.append({"r": val, "g": val, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_alternating_rows(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        on = (step + row) % 2 == 0
        val = 255 if on else 0
        alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
        for _ in range(LED_COLS):
            row_colors.append({"r": val, "g": 0, "b": 255 - val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_checkerboard(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            on = ((row + col + step) % 2) == 0
            val = 255 if on else 0
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
            row_colors.append({"r": 0, "g": val, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_fading_center_out(step, brightness_scale=1.0):
    frame = []
    center = LED_COLS // 2
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            distance = abs(col - center)
            brightness = max(0, 1 - (distance + step) / LED_COLS) * brightness_scale
            val = int(255 * brightness)
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if val > 0 else 0
            row_colors.append({"r": val, "g": val // 2, "b": 0, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_snake(step, brightness_scale=1.0):
    frame = [[{"r":0, "g":0, "b":0, "a":0} for _ in range(LED_COLS)] for _ in range(LED_ROWS)]
    snake_length = 5
    pos = step % (LED_COLS + snake_length)
    for offset in range(snake_length):
        led_pos = pos - offset
        if 0 <= led_pos < LED_COLS:
            row = 0 if (led_pos // LED_COLS) % 2 == 0 else 1
            brightness = int(255 * brightness_scale * (1 - offset / snake_length))
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA)
            frame[row][led_pos] = {"r": 0, "g": brightness, "b": 0, "a": alpha}
    return frame

def pattern_flashing_all(step, brightness_scale=1.0):
    on = (step // 5) % 2 == 0
    val = 255 if on else 0
    alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
    frame = []
    for _ in range(LED_ROWS):
        row_colors = [{"r": val, "g": val, "b": val, "a": alpha} for _ in range(LED_COLS)]
        frame.append(row_colors)
    return frame

def pattern_cylon(step, brightness_scale=1.0):
    frame = [[{"r":0, "g":0, "b":0, "a":0} for _ in range(LED_COLS)] for _ in range(LED_ROWS)]
    period = 2 * (LED_COLS - 1)
    pos = step % period
    if pos >= LED_COLS:
        pos = period - pos
    for row in range(LED_ROWS):
        brightness = 255
        alpha = random.randint(MIN_ALPHA, MAX_ALPHA)
        frame[row][pos] = {"r": brightness, "g": 0, "b": 0, "a": alpha}
    return frame

def pattern_vertical_bars(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            on = ((col // 2 + step) % 2) == 0
            val = 255 if on else 0
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
            row_colors.append({"r": 0, "g": val, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_horizontal_bars(step, brightness_scale=1.0):
    frame = []
    on_row = (step // 3) % LED_ROWS
    for row in range(LED_ROWS):
        row_colors = []
        val = 255 if row == on_row else 0
        alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if val > 0 else 0
        for _ in range(LED_COLS):
            row_colors.append({"r": val, "g": val, "b": 0, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_diagonal_wave(step, brightness_scale=1.0):
    frame = []
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            brightness = (math.sin((col + row * 2 + step) * 0.5) + 1) / 2
            val = int(255 * brightness_scale * brightness)
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if val > 0 else 0
            row_colors.append({"r": val, "g": 0, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_random_pulses(step, brightness_scale=1.0):
    frame = []
    pulse_chance = 0.05 + 0.05 * math.sin(step * 0.2)
    random.seed(step)
    for row in range(LED_ROWS):
        row_colors = []
        for _ in range(LED_COLS):
            on = random.random() < pulse_chance
            val = 255 if on else 0
            alpha = random.randint(MIN_ALPHA, MAX_ALPHA) if on else 0
            row_colors.append({"r": val, "g": 0, "b": val, "a": alpha})
        frame.append(row_colors)
    return frame

# Helper function for hsv to rgb
def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r_, g_, b_ = c, x, 0
    elif h < 120:
        r_, g_, b_ = x, c, 0
    elif h < 180:
        r_, g_, b_ = 0, c, x
    elif h < 240:
        r_, g_, b_ = 0, x, c
    elif h < 300:
        r_, g_, b_ = x, 0, c
    else:
        r_, g_, b_ = c, 0, x
    r = int((r_ + m) * 255)
    g = int((g_ + m) * 255)
    b = int((b_ + m) * 255)
    return r, g, b
