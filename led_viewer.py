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
import requests
import os

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

        self.upload_walrus_button = QPushButton("Upload to Walrus")
        self.upload_walrus_button.setEnabled(False)
        self.upload_walrus_button.clicked.connect(self.upload_to_walrus)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.upload_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.save_frames_button)
        control_layout.addWidget(QLabel("Speed:"))
        control_layout.addWidget(self.speed_box)
        control_layout.addWidget(self.stream_button)
        control_layout.addWidget(self.upload_walrus_button)

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
        self.upload_walrus_button.setEnabled(True)

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
        self.frame_moods = []  # Store mood data for each frame
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
            self.frame_moods.append(current_mood)  # Store mood for this frame

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

            # Calculate Arduino mode for this frame
            mode, blink_interval, brightness = self.calculate_arduino_mode(frame_leds, t_idx, current_mood, tempo)
            
            # Store simplified frame data with only mode information
            self.frames.append({
                "time": int(times_ms[t_idx]),
                "mode": mode,
                "blink_interval": blink_interval,
                "brightness": brightness
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
        
        self.start_arduino_mode_streaming()

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

        frame = self.frames[frame_index]
        
        # Display mode information instead of LED array
        mode = frame["mode"]
        blink_interval = frame["blink_interval"]
        brightness = frame["brightness"]
        
        # Create a simple visualization based on mode
        mode_colors = {
            1: QColor(255, 255, 255),  # White
            2: QColor(255, 100, 100),  # Red
            3: QColor(100, 255, 100),  # Green
            4: QColor(100, 100, 255),  # Blue
            5: QColor(255, 255, 100),  # Yellow
            6: QColor(255, 100, 255),  # Magenta
            7: QColor(100, 255, 255),  # Cyan
            8: QColor(255, 150, 100)   # Orange
        }
        
        color = mode_colors.get(mode, QColor(128, 128, 128))
        brightness_scale = brightness / 255.0
        color.setRed(int(color.red() * brightness_scale))
        color.setGreen(int(color.green() * brightness_scale))
        color.setBlue(int(color.blue() * brightness_scale))
        
        # Fill the entire display area with the mode color
        painter.fillRect(0, 0, w, h, color)
        
        # Display mode information
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(painter.font())
        info_text = f"Mode: {mode} | Interval: {blink_interval}ms | Brightness: {brightness}"
        painter.drawText(10, 20, info_text)

    def mousePressEvent(self, event):
        # No longer needed since we don't have individual LED editing
        pass

    def edit_led_color_and_alpha(self, row, col):
        # No longer needed since we don't have individual LED editing
        pass

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

    def calculate_arduino_mode(self, frame_leds, frame_index, mood_intensity, tempo):
        """Calculate Arduino mode (1-8) based on audio analysis and LED pattern"""
        if not frame_leds:
            return 1, 50, 100  # Default mode, interval, brightness
        
        # Analyze LED activity
        total_leds = 0
        active_leds = 0
        brightness_sum = 0
        edge_leds = 0
        
        for row_idx, row in enumerate(frame_leds):
            for col_idx, led in enumerate(row):
                total_leds += 1
                if led["a"] > 0:
                    active_leds += 1
                    brightness_sum += led["a"]
                    # Check if it's an edge LED
                    if col_idx == 0 or col_idx == 15:
                        edge_leds += 1
        
        activity_ratio = active_leds / total_leds if total_leds > 0 else 0
        avg_brightness = brightness_sum / active_leds if active_leds > 0 else 0
        edge_ratio = edge_leds / max(1, active_leds)
        
        # Calculate blink interval based on tempo and mood
        base_interval = max(20, min(50, int(60000 / tempo)))  # BPM to ms, max 100ms
        mood_factor = 0.5 + mood_intensity * 1.5  # 0.5x to 2.0x
        blink_interval = int(base_interval * mood_factor)
        blink_interval = min(50, blink_interval)  # Ensure maximum 100ms
        
        # Calculate brightness (0-20 for safer brain entrainment)
        brightness = int(min(20, avg_brightness * 20 / 30))
        
        # Determine mode based on pattern characteristics
        if activity_ratio > 0.8:
            # High activity - use mode 1 (full strip flash) or mode 2 (color transition)
            mode = 1 if mood_intensity < 0.5 else 2
        elif edge_ratio > 0.3:
            # Edge-focused pattern - use mode 3 (edge only)
            mode = 3
        elif activity_ratio > 0.5:
            # Moderate activity - use mode 4 (expanding) or mode 5 (center out)
            mode = 4 if frame_index % 2 == 0 else 5
        elif activity_ratio > 0.2:
            # Low activity - use mode 6 (moving dot) or mode 7 (row toggle)
            mode = 6 if mood_intensity > 0.5 else 7
        else:
            # Very low activity - use mode 8 (snake)
            mode = 8
        
        return mode, blink_interval, brightness

    def send_arduino_mode(self, mode, blink_interval, brightness):
        """Send mode data to Arduino in the expected format"""
        try:
            message = f"{mode};{blink_interval};{brightness}"
            print(f"Sending Arduino mode: {message}")
            self.ws.send(message)
        except Exception as e:
            print(f"Failed to send mode: {e}")

    def start_arduino_mode_streaming(self):
        """Stream Arduino modes based on audio analysis"""
        print("Starting Arduino mode streaming...")
        print("Connecting to WebSocket...")
        
        try:
            self.ws = websocket.create_connection(ESP32_WS_URL)
            print("Connected to Arduino!")
            
            # Calculate frame interval
            total_duration_ms = self.frames[-1]["time"] if self.frames else 0
            frame_interval_ms = total_duration_ms / len(self.frames) if len(self.frames) > 0 else 50
            
            print(f"Total duration: {total_duration_ms}ms, {len(self.frames)} frames")
            print(f"Frame interval: {frame_interval_ms:.2f}ms")
            
            for i, frame in enumerate(self.frames):
                if self.stream_button.text() == "Stream Frames to Device":
                    print("Streaming stopped by user.")
                    self.ws.close()
                    return
                
                # Extract mode data from simplified frame
                mode = frame["mode"]
                blink_interval = frame["blink_interval"]
                brightness = frame["brightness"]
                
                # Send mode to Arduino
                self.send_arduino_mode(mode, blink_interval, brightness)
                
                # Add delay to prevent buffer overflow
                # Wait for the blink interval duration plus some buffer time
                sleep_time = (blink_interval / 1000.0) + 0.05  # Add 50ms buffer
                sleep_time = max(0.1, sleep_time)  # Minimum 100ms between sends
                time.sleep(sleep_time)
            
            print("Arduino mode streaming completed.")
            self.ws.close()
            
        except Exception as e:
            print(f"Arduino streaming error: {e}")
            if hasattr(self, 'ws'):
                self.ws.close()

    def get_mood_at_frame(self, frame_index):
        """Get mood intensity for a specific frame"""
        if hasattr(self, 'frame_moods') and frame_index < len(self.frame_moods):
            return self.frame_moods[frame_index]
        return 0.5  # Default mood if not available

    def json_serializer(self, obj):
        """Custom JSON serializer to handle numpy types and other non-serializable objects"""
        if hasattr(obj, 'item'):  # numpy types
            return obj.item()
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return str(obj)

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

    def upload_to_walrus(self):
        """Save frames to JSON and upload to Walrus"""
        if not self.frames:
            self.label.setText("No frames to upload.")
            return

        try:
            # Create a temporary JSON file
            temp_file = "brain_entrainment_frames.json"
            
            # Prepare the data with metadata
            upload_data = {
                "metadata": {
                    "name": "Brain Entrainment Frames",
                    "description": f"Audio-reactive brain entrainment patterns generated from {self.tempo:.1f} BPM audio",
                    "total_frames": len(self.frames),
                    "duration_ms": self.total_duration_ms,
                    "tempo_bpm": self.tempo,
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "version": "1.0"
                },
                "frames": self.frames
            }
            
            # Save to temporary file with proper JSON serialization
            with open(temp_file, 'w') as f:
                json.dump(upload_data, f, indent=2, default=self.json_serializer)
            
            self.label.setText("Uploading to Walrus...")
            
            # Upload to Walrus
            upload_response = self.upload_json_to_walrus(temp_file, epochs=10)
            
            if upload_response:
                self.label.setText("Successfully uploaded to Walrus!")
                
                # Get the blob ID for access
                if 'newlyCreated' in upload_response:
                    blob_id = upload_response['newlyCreated']['blobObject']['blobId']
                    object_id = upload_response['newlyCreated']['blobObject']['id']
                    
                    print(f"\n--- Walrus Upload Successful ---")
                    print(f"Blob ID: {blob_id}")
                    print(f"Object ID: {object_id}")
                    print(f"Access URL: https://aggregator.walrus-testnet.walrus.space/v1/blobs/{blob_id}")
                    
                    # Clean up temporary file
                    os.remove(temp_file)
                else:
                    self.label.setText("Upload completed but no blob ID received.")
            else:
                self.label.setText("Failed to upload to Walrus.")
                
        except Exception as e:
            self.label.setText(f"Error uploading to Walrus: {e}")
            print(f"Upload error: {e}")

    def upload_json_to_walrus(self, file_path: str, publisher_url: str = "https://publisher.walrus-testnet.walrus.space", epochs: int = 10):
        """
        Uploads a JSON file to a Walrus publisher.
        """
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return None

        # Read the content of the JSON file
        with open(file_path, 'r') as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON file at {file_path}")
                return None

        # The API expects the raw file content in the body
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Construct the full URL with parameters
        url = f"{publisher_url}/v1/blobs"
        params = {
            'epochs': epochs
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.put(url, params=params, data=file_content, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

def main():
    app = QApplication(sys.argv)
    window = LEDVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
