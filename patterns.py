import random
import math

LED_ROWS = 2
LED_COLS = 16

MIN_ALPHA = 5
MAX_ALPHA = 30

# Brain entrainment frequencies (Hz)
BRAIN_FREQUENCIES = {
    'delta': 0.5,      # Deep sleep
    'theta': 4.0,      # Meditation, creativity
    'alpha': 8.0,      # Relaxation, calm
    'beta': 13.0,      # Focus, alertness
    'gamma': 40.0      # High-level processing
}

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

def pattern_brain_entrainment(step, brightness_scale=1.0, frequency_type='alpha', tempo_bpm=120):
    """Brain entrainment pattern using specific frequencies"""
    frame = []
    
    # Convert BPM to Hz for tempo sync
    tempo_hz = tempo_bpm / 60.0
    brain_freq = BRAIN_FREQUENCIES[frequency_type]
    
    # Combine brain frequency with tempo
    combined_freq = brain_freq + (tempo_hz * 0.1)
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            # Create pulsing wave that moves across the strip
            wave_pos = (col + step * 0.5) / LED_COLS
            pulse = (math.sin(combined_freq * step * 0.1 + wave_pos * 2 * math.pi) + 1) / 2
            
            # Add cross-pattern for enhanced entrainment
            cross_pattern = (math.sin((row + col) * 0.5 + step * 0.2) + 1) / 2
            
            # Combine patterns
            brightness = (pulse * 0.7 + cross_pattern * 0.3) * brightness_scale
            
            # Use colors that enhance brain entrainment
            if frequency_type == 'alpha':
                # Blue-green for relaxation
                val_r = int(50 * brightness)
                val_g = int(200 * brightness)
                val_b = int(255 * brightness)
            elif frequency_type == 'beta':
                # Yellow-orange for focus
                val_r = int(255 * brightness)
                val_g = int(200 * brightness)
                val_b = int(50 * brightness)
            elif frequency_type == 'theta':
                # Purple for creativity
                val_r = int(150 * brightness)
                val_g = int(50 * brightness)
                val_b = int(255 * brightness)
            else:
                # White for other frequencies
                val_r = val_g = val_b = int(255 * brightness)
            
            alpha = int(MIN_ALPHA + (MAX_ALPHA - MIN_ALPHA) * brightness)
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_tempo_sync_pulse(step, brightness_scale=1.0, tempo_bpm=120):
    """Pulse pattern synchronized with audio tempo"""
    frame = []
    
    # Convert BPM to frame rate (assuming 50fps)
    frames_per_beat = int(3000 / tempo_bpm)  # 50fps * 60s / BPM
    beat_phase = (step % frames_per_beat) / frames_per_beat
    
    # Create strong pulse on beat
    beat_pulse = math.exp(-10 * (beat_phase - 0.5)**2)  # Gaussian pulse
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            # Add spatial variation
            spatial_phase = (col / LED_COLS + row * 0.5) % 1.0
            spatial_pulse = math.sin(spatial_phase * 2 * math.pi + step * 0.3)
            
            # Combine beat pulse with spatial pattern
            brightness = (beat_pulse * 0.8 + (spatial_pulse + 1) * 0.1) * brightness_scale
            
            # Use warm colors for tempo sync
            val_r = int(255 * brightness)
            val_g = int(150 * brightness)
            val_b = int(50 * brightness)
            
            alpha = int(MIN_ALPHA + (MAX_ALPHA - MIN_ALPHA) * brightness)
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_mood_amplitude_wave(step, brightness_scale=1.0, mood_intensity=0.5, tempo_bpm=120):
    """Wave pattern that responds to song mood and amplitude"""
    frame = []
    
    # Mood affects color temperature and wave speed
    mood_speed = 0.2 + mood_intensity * 0.3
    mood_hue_offset = mood_intensity * 0.3  # 0 = cool, 1 = warm
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            # Create multiple overlapping waves
            wave1 = math.sin((col + step * mood_speed) * 0.5)
            wave2 = math.sin((col - step * mood_speed * 0.7) * 0.3)
            wave3 = math.sin((row + step * mood_speed * 0.5) * 0.4)
            
            # Combine waves
            combined_wave = (wave1 + wave2 + wave3) / 3
            brightness = ((combined_wave + 1) / 2) * brightness_scale
            
            # Mood affects color - intensity controls warm/cool balance
            if mood_intensity < 0.3:
                # Cool colors (calm)
                val_r = int(50 * brightness)
                val_g = int(150 * brightness)
                val_b = int(255 * brightness)
            elif mood_intensity < 0.7:
                # Neutral colors (balanced)
                val_r = int(150 * brightness)
                val_g = int(150 * brightness)
                val_b = int(150 * brightness)
            else:
                # Warm colors (energetic)
                val_r = int(255 * brightness)
                val_g = int(100 * brightness)
                val_b = int(50 * brightness)
            
            alpha = int(MIN_ALPHA + (MAX_ALPHA - MIN_ALPHA) * brightness)
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_photic_stimulation(step, brightness_scale=1.0, frequency_hz=10.0):
    """Classic photic stimulation for brain entrainment"""
    frame = []
    
    # Calculate flash timing based on frequency
    flash_interval = int(50 / frequency_hz)  # 50fps / frequency
    is_flash_on = (step % flash_interval) < (flash_interval // 2)
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            if is_flash_on:
                # Strong white flash
                brightness = brightness_scale
                val_r = val_g = val_b = int(255 * brightness)
                alpha = MAX_ALPHA
            else:
                # Complete darkness
                val_r = val_g = val_b = 0
                alpha = 0
            
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_theta_flow(step, brightness_scale=1.0, tempo_bpm=120):
    """Theta wave pattern for meditation and creativity"""
    frame = []
    
    # Theta frequency (4-8 Hz) with tempo influence
    theta_freq = 6.0 + (tempo_bpm - 120) * 0.02
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            # Create flowing wave pattern
            flow_pos = (col + step * 0.3) / LED_COLS
            flow_wave = math.sin(flow_pos * 4 * math.pi + step * theta_freq * 0.1)
            
            # Add depth with multiple frequencies
            depth_wave = math.sin((row + col) * 0.5 + step * 0.2) * 0.3
            
            brightness = ((flow_wave + depth_wave + 1) / 2) * brightness_scale
            
            # Purple-blue gradient for theta
            val_r = int(100 * brightness)
            val_g = int(50 * brightness)
            val_b = int(200 * brightness)
            
            alpha = int(MIN_ALPHA + (MAX_ALPHA - MIN_ALPHA) * brightness)
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_alpha_relaxation(step, brightness_scale=1.0, tempo_bpm=120):
    """Alpha wave pattern for relaxation and calm"""
    frame = []
    
    # Alpha frequency (8-13 Hz)
    alpha_freq = 10.0
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            # Gentle breathing pattern
            breath_cycle = math.sin(step * alpha_freq * 0.1)
            
            # Spatial wave
            spatial_wave = math.sin((col / LED_COLS) * 2 * math.pi + step * 0.2)
            
            # Combine for gentle pulsing
            brightness = ((breath_cycle + spatial_wave + 2) / 4) * brightness_scale
            
            # Soft blue-green for relaxation
            val_r = int(30 * brightness)
            val_g = int(120 * brightness)
            val_b = int(180 * brightness)
            
            alpha = int(MIN_ALPHA + (MAX_ALPHA - MIN_ALPHA) * brightness)
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
        frame.append(row_colors)
    return frame

def pattern_beta_focus(step, brightness_scale=1.0, tempo_bpm=120):
    """Beta wave pattern for focus and alertness"""
    frame = []
    
    # Beta frequency (13-30 Hz)
    beta_freq = 20.0
    
    for row in range(LED_ROWS):
        row_colors = []
        for col in range(LED_COLS):
            # Sharp, focused pattern
            focus_pattern = math.sin((col + step * 0.5) * 0.8) * math.cos(step * beta_freq * 0.05)
            
            # Add tempo sync
            tempo_sync = math.sin(step * (tempo_bpm / 60.0) * 0.1) * 0.3
            
            brightness = ((focus_pattern + tempo_sync + 1) / 2) * brightness_scale
            
            # Bright yellow-orange for focus
            val_r = int(255 * brightness)
            val_g = int(200 * brightness)
            val_b = int(50 * brightness)
            
            alpha = int(MIN_ALPHA + (MAX_ALPHA - MIN_ALPHA) * brightness)
            row_colors.append({"r": val_r, "g": val_g, "b": val_b, "a": alpha})
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
