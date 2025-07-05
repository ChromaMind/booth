import sys
import random
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QSlider, QLabel, QColorDialog, QHBoxLayout, QComboBox, QDialog,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
import pygame
import threading
import time
import librosa
import websocket
import math
import numpy as np

from patterns import * 

ESP32_WS_URL = "ws://10.151.240.37:81"

LED_ROWS = 2
LED_COLS = 16


class ColorAlphaDialog(QDialog):
    def __init__(self, parent=None, initial_color=QColor(255, 255, 255), initial_alpha=100):
        super().__init__(parent)
        self.setWindowTitle("Select LED Color and Amplification")

        self.color = initial_color
        self.alpha = initial_alpha

        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)

        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(30)  # Your max threshold
        self.alpha_slider.setValue(self.alpha)
        self.alpha_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.alpha_slider.setTickInterval(5)

        self.alpha_label = QLabel(f"Amplification (Alpha): {self.alpha} (max: 30)")
        self.brightness_label = QLabel(f"Display Brightness: {int(self.alpha * 255 / 25)}%")

        self.alpha_slider.valueChanged.connect(self.update_alpha_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.color_button)
        layout.addWidget(self.alpha_label)
        layout.addWidget(self.brightness_label)
        layout.addWidget(self.alpha_slider)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.color, self, "Select LED Color")
        if color.isValid():
            self.color = color

    def update_alpha_label(self, value):
        self.alpha = value
        self.alpha_label.setText(f"Amplification (Alpha): {value} (max: 30)")
        self.brightness_label.setText(f"Display Brightness: {int(value * 255 / 25)}%")


class LEDVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LED Audio Visualizer Editor")
        self.setMinimumSize(900, 500)

        self.frames = []  # Each frame: {"time": ms, "leds": 2D list}
        self.total_duration_ms = 0
        self.audio_loaded = False
        self.selected_led = None
        self.playback_speed = 1.0
        self.tempo = 0.0

        self.label = QLabel("Upload an MP3 file")
        self.upload_button = QPushButton("Upload MP3")
        self.upload_button.clicked.connect(self.load_mp3)

        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.slider_changed)

        self.speed_box = QComboBox()
        self.speed_box.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_box.setCurrentText("1.0x")
        self.speed_box.currentTextChanged.connect(self.speed_changed)

        self.save_frames_button = QPushButton("Save Frames")
        self.save_frames_button.setEnabled(False)
        self.save_frames_button.clicked.connect(self.save_frames)

        self.stream_button = QPushButton("Stream Frames to Device")
        self.stream_button.setEnabled(False)
        self.stream_button.clicked.connect(self.on_stream_clicked)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.upload_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.save_frames_button)
        control_layout.addWidget(QLabel("Speed:"))
        control_layout.addWidget(self.speed_box)
        control_layout.addWidget(self.stream_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(control_layout)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        pygame.mixer.init()

    def load_mp3(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select MP3 File", "", "Audio Files (*.mp3 *.wav)"
        )
        if not file_path:
            return

        self.label.setText(f"Loaded: {file_path}")
        self.frames.clear()
        self.audio_loaded = False
        self.selected_led = None

        self.generate_led_frames_at_beats(file_path)

        pygame.mixer.music.load(file_path)
        self.slider.setMaximum(len(self.frames) - 1)
        self.slider.setEnabled(True)
        self.play_button.setEnabled(True)
        self.save_frames_button.setEnabled(True)
        self.stream_button.setEnabled(True)

        self.audio_loaded = True
        self.update()
    
    def generate_led_frames_fft_based(self, file_path):
        print(f"Loading audio file: {file_path}")
        y, sr = librosa.load(file_path, sr=None)

        print("Computing STFT...")
        hop_length = 256
        n_fft = 1024
        S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))  # Shape: (freq_bins, time_frames)
        S_db = librosa.amplitude_to_db(S, ref=np.max)

        times = librosa.frames_to_time(range(S.shape[1]), sr=sr, hop_length=hop_length)
        times_ms = (times * 1000).astype(int)

        freq_bins = S_db.shape[0]
        frames = S_db.shape[1]
        self.frames = []

        # Divide frequencies across LED rows
        bands_per_row = freq_bins // LED_ROWS

        for t_idx in range(frames):
            frame_leds = []

            for row in range(LED_ROWS):
                row_leds = []

                # Get average energy for this row's frequency band
                start_bin = row * bands_per_row
                end_bin = (row + 1) * bands_per_row
                band_energy = np.mean(S_db[start_bin:end_bin, t_idx])
                norm_energy = np.clip((band_energy + 80) / 80, 0.0, 1.0)  # Normalize to 0-1

                # Use norm_energy to drive brightness
                brightness = norm_energy

                # Randomized hue per row and frame for visual variety
                base_hue = (row / LED_ROWS + random.uniform(-0.1, 0.1)) % 1.0

                for col in range(LED_COLS):
                    hue = (base_hue + col / LED_COLS + random.uniform(-0.05, 0.05)) % 1.0
                    sat = 1.0
                    val = brightness
                    r, g, b = hsv_to_rgb(hue, sat, val)
                    a = int(255 * val)
                    row_leds.append({"r": r, "g": g, "b": b, "a": a})
                frame_leds.append(row_leds)

            self.frames.append({
                "time": int(times_ms[t_idx]),
                "leds": frame_leds
            })

        self.total_duration_ms = times_ms[-1] if len(times_ms) > 0 else 0
        self.label.setText(f"Generated {len(self.frames)} continuous FFT-based frames")

    
    def generate_led_frames_from_audio(self, file_path):
        print(f"Loading audio file: {file_path}")
        y, sr = librosa.load(file_path, sr=None)  # use native sample rate

        print("Detecting tempo and beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        if hasattr(tempo, '__len__') and not isinstance(tempo, str):
            tempo = float(tempo[0])
        self.tempo = tempo

        print(f"Estimated BPM: {tempo:.2f}")
        self.label.setText(f"BPM detected: {tempo:.2f}")

        # Extract features across the whole audio
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
        zero_crossings = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)

        # Normalize features
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
        centroid_norm = (spectral_centroid - spectral_centroid.min()) / (spectral_centroid.max() - spectral_centroid.min() + 1e-6)
        zc_norm = (zero_crossings - zero_crossings.min()) / (zero_crossings.max() - zero_crossings.min() + 1e-6)

        # Time for each feature frame (ms)
        frame_times_ms = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length) * 1000

        def get_feature_at_time(feature_array, times_array, t_ms):
            idx = min(range(len(times_array)), key=lambda i: abs(times_array[i] - t_ms))
            return feature_array[idx]

        # Frame rate settings
        target_fps = 50  # 50 Hz
        frame_interval_ms = int(1000 / target_fps)

        duration_ms = int(len(y) / sr * 1000)
        print(f"Audio duration: {duration_ms}ms")

        self.frames = []

        current_time = 0
        while current_time < duration_ms:
            rms_val = get_feature_at_time(rms_norm, frame_times_ms, current_time)
            centroid_val = get_feature_at_time(centroid_norm, frame_times_ms, current_time)
            zc_val = get_feature_at_time(zc_norm, frame_times_ms, current_time)

            frame_leds = self.pattern_dynamic(current_time, rms_val, centroid_val, zc_val)

            self.frames.append({
                "time": current_time,
                "leds": frame_leds
            })

            current_time += frame_interval_ms

        self.total_duration_ms = duration_ms

    def generate_led_frames_from_audio1(self, file_path):
        print(f"Loading audio file: {file_path}")
        y, sr = librosa.load(file_path, sr=None)  # native sample rate

        print("Detecting tempo and beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        if hasattr(tempo, '__len__') and not isinstance(tempo, str):
            tempo = float(tempo[0])
        self.tempo = tempo

        print(f"Estimated BPM: {tempo:.2f}")
        self.label.setText(f"BPM detected: {tempo:.2f}")

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)  # seconds
        beat_times_ms = [int(x * 1000) for x in beat_times]

        # Extract features for entire audio (frame-wise)
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
        zero_crossings = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)

        # Normalize features for mapping
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
        centroid_norm = (spectral_centroid - spectral_centroid.min()) / (spectral_centroid.max() - spectral_centroid.min() + 1e-6)
        zc_norm = (zero_crossings - zero_crossings.min()) / (zero_crossings.max() - zero_crossings.min() + 1e-6)

        total_frames = len(beat_times_ms)
        frames_per_beat = 4

        self.frames = []

        # Map librosa frames to beat frames index
        frame_times_ms = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length) * 1000

        def get_feature_at_time(feature_array, times_array, t_ms):
            # Find closest frame index to time t_ms
            idx = min(range(len(times_array)), key=lambda i: abs(times_array[i] - t_ms))
            return feature_array[idx]

        for i, t_ms in enumerate(beat_times_ms):
            next_beat_ms = beat_times_ms[min(i + 1, total_frames - 1)]
            beat_duration = max(1, next_beat_ms - t_ms)

            for step in range(frames_per_beat):
                current_time = t_ms + int((step / frames_per_beat) * beat_duration)

                # Extract features at this time (mapped)
                rms_val = get_feature_at_time(rms_norm, frame_times_ms, current_time)
                centroid_val = get_feature_at_time(centroid_norm, frame_times_ms, current_time)
                zc_val = get_feature_at_time(zc_norm, frame_times_ms, current_time)

                # Use features to create pattern
                frame_leds = self.pattern_dynamic(step, rms_val, centroid_val, zc_val)

                self.frames.append({
                    "time": current_time,
                    "leds": frame_leds
                })

            # Insert off frame with jitter except after last beat
            if i < total_frames - 1:
                off_frame = [
                    [{"r": 0, "g": 0, "b": 0, "a": 0} for _ in range(LED_COLS)]
                    for _ in range(LED_ROWS)
                ]
                base_off_time = t_ms + beat_duration // 2
                jitter = random.randint(-50, 50)
                off_time = max(t_ms + 10, base_off_time + jitter)
                self.frames.append({
                    "time": off_time,
                    "leds": off_frame
                })

        self.total_duration_ms = beat_times_ms[-1] if beat_times_ms else 0

    def pattern_dynamic(self, step, rms, centroid, zero_cross):
        """
        Dynamic pattern based on audio features:

        - Brightness linked to RMS energy
        - Color hue shifted by spectral centroid
        - Flicker speed modulated by zero crossing rate
        """

        leds = []
        base_hue = centroid  # 0-1 hue from spectral centroid
        flicker = 0.5 + 0.5 * math.sin(step * 2 * math.pi * zero_cross * 5)

        brightness = rms * flicker

        for row in range(LED_ROWS):
            row_leds = []
            for col in range(LED_COLS):
                # Create a moving wave of hue along the strip, shifted by step and col
                hue = (base_hue + (col / LED_COLS) + step * 0.1) % 1.0
                saturation = 1.0
                value = max(0.1, brightness)  # avoid too dark

                r, g, b = hsv_to_rgb(hue, saturation, value)

                # Alpha channel scaled by brightness (amplification)
                a = int(255 * value)

                row_leds.append({"r": r, "g": g, "b": b, "a": a})
            leds.append(row_leds)
        return leds

    def generate_led_frames_at_beats(self, file_path):

        print(f"Loading audio file: {file_path}")
        y, sr = librosa.load(file_path, sr=None)

        print("Detecting tempo...")
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if hasattr(tempo, '__len__') and not isinstance(tempo, str):
            tempo = float(tempo[0])
        self.tempo = tempo

        print(f"Estimated BPM: {tempo:.2f}")
        self.label.setText(f"BPM detected: {tempo:.2f}")

        # ---- Enhanced audio analysis ----
        hop_length = 512
        n_fft = 1024
        S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
        S_db = librosa.amplitude_to_db(S, ref=np.max)

        # Extract mood and intensity features
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length)[0]
        zero_crossings = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
        
        # Calculate mood intensity (0-1 scale)
        # High RMS + high spectral centroid + high rolloff = energetic
        # Low values = calm/relaxed
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
        centroid_norm = (spectral_centroid - spectral_centroid.min()) / (spectral_centroid.max() - spectral_centroid.min() + 1e-6)
        rolloff_norm = (spectral_rolloff - spectral_rolloff.min()) / (spectral_rolloff.max() - spectral_rolloff.min() + 1e-6)
        
        mood_intensity = (rms_norm + centroid_norm + rolloff_norm) / 3

        times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=hop_length)
        times_ms = (times * 1000).astype(int)

        freq_bins = S_db.shape[0]
        bands_per_row = freq_bins // LED_ROWS

        # ---- Brain entrainment patterns ----
        brain_patterns = [
            pattern_brain_entrainment,
            pattern_tempo_sync_pulse,
            pattern_mood_amplitude_wave,
            pattern_photic_stimulation,
            pattern_theta_flow,
            pattern_alpha_relaxation,
            pattern_beta_focus,
            pattern_wave_vertical,
            pattern_zigzag,
            pattern_gradient_rainbow,
            pattern_fading_left_to_right,
            pattern_fading_right_to_left,
            pattern_alternating_rows,
            pattern_checkerboard,
            pattern_snake,
            pattern_cylon,
            pattern_diagonal_wave,
        ]

        self.frames = []
        pattern_change_interval = 30  # Change pattern every 30 frames (0.6s at 50fps)
        current_pattern_func = random.choice(brain_patterns)
        current_frequency_type = 'alpha'  # Default brain frequency

        for t_idx in range(S_db.shape[1]):
            # Every N frames, pick a new pattern
            if t_idx % pattern_change_interval == 0:
                current_pattern_func = random.choice(brain_patterns)
                
                # Select brain frequency based on mood
                avg_mood = np.mean(mood_intensity[max(0, t_idx-10):t_idx+1])
                if avg_mood < 0.3:
                    current_frequency_type = 'theta'  # Calm -> theta for meditation
                elif avg_mood < 0.6:
                    current_frequency_type = 'alpha'  # Moderate -> alpha for relaxation
                else:
                    current_frequency_type = 'beta'   # Energetic -> beta for focus

            # Calculate average energy across bands for overall brightness
            band_energies = [
                np.mean(S_db[row * bands_per_row:(row + 1) * bands_per_row, t_idx])
                for row in range(LED_ROWS)
            ]
            avg_energy_db = np.mean(band_energies)
            brightness = np.clip((avg_energy_db + 80) / 80, 0.1, 1.0)

            # Get current mood intensity
            current_mood = mood_intensity[min(t_idx, len(mood_intensity)-1)]

            step = t_idx % 16  # Pattern animation steps

            # Apply the pattern function with enhanced parameters
            if current_pattern_func == pattern_brain_entrainment:
                frame_leds = current_pattern_func(step, brightness, current_frequency_type, tempo)
            elif current_pattern_func == pattern_tempo_sync_pulse:
                frame_leds = current_pattern_func(step, brightness, tempo)
            elif current_pattern_func == pattern_mood_amplitude_wave:
                frame_leds = current_pattern_func(step, brightness, current_mood, tempo)
            elif current_pattern_func == pattern_photic_stimulation:
                # Use tempo to determine flash frequency
                flash_freq = max(5.0, min(20.0, tempo / 6.0))  # 5-20 Hz range
                frame_leds = current_pattern_func(step, brightness, flash_freq)
            elif current_pattern_func == pattern_theta_flow:
                frame_leds = current_pattern_func(step, brightness, tempo)
            elif current_pattern_func == pattern_alpha_relaxation:
                frame_leds = current_pattern_func(step, brightness, tempo)
            elif current_pattern_func == pattern_beta_focus:
                frame_leds = current_pattern_func(step, brightness, tempo)
            else:
                # Original patterns
                frame_leds = current_pattern_func(step, brightness)

            # Add blinking rate to each LED
            for row_idx, row in enumerate(frame_leds):
                for col_idx, led in enumerate(row):
                    blinking_rate = self.calculate_led_blinking_rate(led, t_idx, current_mood, row_idx, col_idx)
                    led["blink_rate_hz"] = blinking_rate
            
            self.frames.append({
                "time": int(times_ms[t_idx]),
                "leds": frame_leds
            })

        self.total_duration_ms = times_ms[-1] if len(times_ms) > 0 else 0
        print(f"Generated {len(self.frames)} frames with brain entrainment patterns")
        print(f"Average mood intensity: {np.mean(mood_intensity):.2f}")
        self.label.setText(f"Generated {len(self.frames)} brain entrainment frames (BPM: {tempo:.1f})")

    def on_stream_clicked(self):
        if not self.frames:
            self.label.setText("No frames to stream.")
            return

        if self.stream_button.text() == "Stop Streaming":
            self.stream_button.setText("Stream Frames to Device")
            self.label.setText("Streaming stopped.")
            # Stop audio playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            return

        self.stream_button.setText("Stop Streaming")
        self.label.setText("Starting synchronized streaming...")
        
        # Start audio playback
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        
        arduino_url = "http://192.168.4.1/ledframes"  # Change to your device's IP
        self.start_streaming_frames(arduino_url, chunk_size=5)

    def toggle_play(self):
        if not self.audio_loaded:
            return

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_button.setText("Play")
            self.timer.stop()
        else:
            if pygame.mixer.music.get_pos() == -1:
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.play_button.setText("Pause")
            self.timer.start(30)

    def update_frame(self):
        if not pygame.mixer.music.get_busy():
            self.timer.stop()
            self.play_button.setText("Play")
            return

        pos_ms = pygame.mixer.music.get_pos()
        adjusted_ms = pos_ms * self.playback_speed

        current_frame_index = 0
        for i, frame in enumerate(self.frames):
            if frame["time"] <= adjusted_ms:
                current_frame_index = i
            else:
                break

        self.slider.blockSignals(True)
        self.slider.setMaximum(len(self.frames) - 1)
        self.slider.setValue(current_frame_index)
        self.slider.blockSignals(False)
        self.update()

    def slider_changed(self, value):
        if not self.frames or value >= len(self.frames):
            return

        time_ms = self.frames[value]["time"]
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=time_ms / 1000.0)
        pygame.mixer.music.pause()
        self.update()

    def speed_changed(self, value):
        speed_map = {
            "0.5x": 0.5,
            "0.75x": 0.75,
            "1.0x": 1.0,
            "1.25x": 1.25,
            "1.5x": 1.5,
            "2.0x": 2.0
        }
        self.playback_speed = speed_map[value]
        if pygame.mixer.music.get_busy():
            self.timer.start(30)

    def paintEvent(self, event):
        if not self.frames:
            return

        painter = QPainter(self)
        w = self.width()
        h = self.height() - 150  # Reserve space for controls

        cell_w = w / LED_COLS
        cell_h = h / LED_ROWS

        frame_index = self.slider.value()
        if frame_index >= len(self.frames):
            return

        frame = self.frames[frame_index]["leds"]

        for y in range(LED_ROWS):
            for x in range(LED_COLS):
                led = frame[y][x]
                
                # Normalize alpha: 25 (your threshold) = 255 (full brightness)
                alpha_normalized = min(255, int(led.get('a', 255) * 255 / 25))
                
                # Apply alpha normalization to RGB values as well
                brightness_scale = alpha_normalized / 255.0
                r = int(led["r"] * brightness_scale)
                g = int(led["g"] * brightness_scale)
                b = int(led["b"] * brightness_scale)
                
                color = QColor(r, g, b, 255)  # Use full alpha for display
                rect_x = int(x * cell_w)
                rect_y = int(y * cell_h)
                painter.fillRect(rect_x, rect_y, int(cell_w), int(cell_h), color)

                if self.selected_led == (y, x):
                    painter.setPen(Qt.GlobalColor.black)
                    painter.drawRect(rect_x, rect_y, int(cell_w), int(cell_h))

    def mousePressEvent(self, event):
        if not self.frames:
            return

        w = self.width()
        h = self.height() - 150
        cell_w = w / LED_COLS
        cell_h = h / LED_ROWS

        x = int(event.position().x())
        y = int(event.position().y())

        col = int(x / cell_w)
        row = int(y / cell_h)

        if 0 <= row < LED_ROWS and 0 <= col < LED_COLS:
            self.selected_led = (row, col)
            self.edit_led_color_and_alpha(row, col)

    def edit_led_color_and_alpha(self, row, col):
        frame_index = self.slider.value()
        if frame_index >= len(self.frames):
            return

        led = self.frames[frame_index]["leds"][row][col]
        current_color = QColor(led["r"], led["g"], led["b"], led.get('a', 255))

        dialog = ColorAlphaDialog(self, initial_color=current_color, initial_alpha=led.get('a', 255))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            led["r"] = dialog.color.red()
            led["g"] = dialog.color.green()
            led["b"] = dialog.color.blue()
            led['a'] = dialog.alpha
            self.update()

    def save_frames(self):
        if not self.frames:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Frames as JSON", "", "JSON Files (*.json)"
        )
        if not save_path:
            return

        try:
            with open(save_path, "w") as f:
                json.dump(self.frames, f, indent=2)
            self.label.setText(f"Frames saved to: {save_path}")
        except Exception as e:
            self.label.setText(f"Error saving frames: {e}")

    def start_streaming_frames(self, url, chunk_size=5):
        print("Starting to stream frames to device...")
        print("Connecting to WebSocket...")
        ws = websocket.create_connection(ESP32_WS_URL)

        def send_frames(frames):
            try:
                # Each LED has its own blinking rate, no global frequency needed
                data = {
                    "frames": frames,
                    "tempo_bpm": self.tempo
                }
                json_data = json.dumps(data)
                ws.send(json_data)
            except Exception as e:
                print("Failed to send frames:", e)

        # Calculate frame timing based on actual audio duration
        total_duration_ms = self.frames[-1]["time"] if self.frames else 0
        frame_interval_ms = total_duration_ms / len(self.frames) if len(self.frames) > 0 else 50
        
        print(f"Total duration: {total_duration_ms}ms, {len(self.frames)} frames")
        print(f"Frame interval: {frame_interval_ms:.2f}ms")

        for i in range(0, len(self.frames), chunk_size):
            if self.stream_button.text() == "Stream Frames to Device":
                print("Streaming stopped by user.")
                ws.close()
                return
                
            if i + chunk_size > len(self.frames):
                chunk_size = len(self.frames) - i

            frames = self.frames[i:i+chunk_size]
            print(f"Sending chunk {i//chunk_size + 1}: {len(frames)} frames")

            if not frames:
                print("No frames to send.")
                return
            
            # Each LED has its own blinking rate
            total_leds = sum(len(frame["leds"]) * len(frame["leds"][0]) for frame in frames)
            active_leds = sum(1 for frame in frames for row in frame["leds"] for led in row if led.get("blink_rate_hz", 0) > 0)
            print(f"Chunk: {active_leds}/{total_leds} LEDs active with individual blinking rates")
                
            send_frames(frames)
            
            # Calculate sleep time based on actual frame timing
            chunk_duration_ms = frame_interval_ms * chunk_size
            sleep_time = chunk_duration_ms / 1000.0  # Convert to seconds
            
            # Add small buffer to account for network latency
            sleep_time = max(0.01, sleep_time * 0.95)
            time.sleep(sleep_time)

        print("Streaming completed.")
        ws.close()

    def calculate_chunk_frequency(self, frames, chunk_start, chunk_size):
        """Calculate the optimal frequency for brain entrainment based on frames"""
        if not frames:
            return 10.0  # Default frequency
        
        # Analyze the frames to determine pattern characteristics
        total_leds = 0
        active_leds = 0
        brightness_sum = 0
        
        for frame in frames:
            for row in frame["leds"]:
                for led in row:
                    total_leds += 1
                    if led["a"] > 0:  # Active LED
                        active_leds += 1
                        brightness_sum += led["a"]
        
        # Calculate activity ratio and average brightness
        activity_ratio = active_leds / total_leds if total_leds > 0 else 0
        avg_brightness = brightness_sum / active_leds if active_leds > 0 else 0
        
        # Base frequency on activity and brightness
        base_freq = 8.0  # Alpha frequency as default
        
        if activity_ratio > 0.8 and avg_brightness > 20:
            # High activity and brightness - use beta/gamma for focus/alertness
            base_freq = 15.0 + (avg_brightness / 30.0) * 10.0  # 15-25 Hz
        elif activity_ratio > 0.5:
            # Moderate activity - use alpha for relaxation
            base_freq = 8.0 + (avg_brightness / 30.0) * 5.0  # 8-13 Hz
        else:
            # Low activity - use theta for meditation
            base_freq = 4.0 + (avg_brightness / 30.0) * 4.0  # 4-8 Hz
        
        # Adjust based on tempo
        tempo_factor = min(2.0, max(0.5, self.tempo / 120.0))
        final_freq = base_freq * tempo_factor
        
        # Ensure frequency is within safe brain entrainment range
        final_freq = max(1.0, min(30.0, final_freq))
        
        return final_freq

    def calculate_led_blinking_rate(self, led_data, frame_index, mood_intensity, row, col):
        """Calculate blinking rate for individual LED based on its properties and position"""
        if led_data["a"] == 0:
            return 0  # No blinking for inactive LEDs
        
        # Base blinking rate on LED brightness and position
        brightness_factor = led_data["a"] / 30.0  # Normalize to 0-1
        
        # Position-based variation (creates wave-like effects)
        position_factor = (row + col + frame_index * 0.1) % 1.0
        
        # Mood affects overall blinking speed
        mood_factor = 0.5 + mood_intensity * 1.5  # 0.5x to 2.0x
        
        # Calculate base blinking rate (Hz)
        base_rate = 5.0 + brightness_factor * 20.0  # 5-25 Hz range
        
        # Add position-based variation
        position_variation = math.sin(position_factor * 2 * math.pi) * 5.0
        
        # Final blinking rate
        blinking_rate = (base_rate + position_variation) * mood_factor
        
        # Ensure rate is within safe range
        blinking_rate = max(1.0, min(30.0, blinking_rate))
        
        return blinking_rate

def main():
    app = QApplication(sys.argv)
    window = LEDVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
