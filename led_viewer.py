import sys
import random
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QSlider, QLabel, QColorDialog, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
import pygame
import threading
import time
import requests
import librosa
import websocket

ESP32_WS_URL = "ws://10.151.240.37:81"

# Configuration
NUM_FRAMES = 10
NUM_PIXELS = 32
DELAY_BETWEEN_SENDS = 1  # seconds

LED_ROWS = 2
LED_COLS = 16


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
        self.streaming_thread = None
        self.streaming_stop_event = threading.Event()

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

    def generate_led_frames_at_beats(self, file_path):
        print(f"Loading audio file: {file_path}")
        y, sr = librosa.load(file_path, sr=None)  # native sample rate

        print("Detecting tempo and beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # Convert tempo to float if it's an array
        if hasattr(tempo, '__len__') and not isinstance(tempo, str):
            tempo = float(tempo[0])
        self.tempo = tempo

        print(f"Estimated BPM: {tempo:.2f}")
        self.label.setText(f"BPM detected: {tempo:.2f}")

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)  # seconds
        beat_times_ms = [int(x) for x in (beat_times * 1000)]  # milliseconds as int

        self.frames = []
        for t_ms in beat_times_ms:
            frame = [
                [{"r": random.randint(0, 255),
                  "g": random.randint(0, 255),
                  "b": random.randint(0, 255),
                  'a': random.randint(0,100)}
                 for _ in range(LED_COLS)]
                for _ in range(LED_ROWS)
            ]
            self.frames.append({
                "time": t_ms,
                "leds": frame
            })

        self.total_duration_ms = beat_times_ms[-1] if beat_times_ms else 0

    def on_stream_clicked(self):
        if not self.frames:
            self.label.setText("No frames to stream.")
            return

        if self.stream_button.text() == "Stop Streaming":
            self.streaming_stop_event.set()  # signal thread to stop
            self.stream_button.setText("Stream Frames to Device")
            self.label.setText("Stopping streaming...")
            return

        # Clear stop event and start streaming thread
        self.streaming_stop_event.clear()
        self.stream_button.setText("Stop Streaming")
        self.label.setText("Streaming frames to device...")
    
        # Start streaming in background thread
        self.streaming_thread = threading.Thread(target=self.start_streaming_frames, args=(ESP32_WS_URL, 10))
        self.streaming_thread.start()


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
                color = QColor(led["r"], led["g"], led["b"])
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
            self.edit_led_color(row, col)

    def edit_led_color(self, row, col):
        frame_index = self.slider.value()
        if frame_index >= len(self.frames):
            return

        led = self.frames[frame_index]["leds"][row][col]
        current_color = QColor(led["r"], led["g"], led["b"])
        new_color = QColorDialog.getColor(current_color, self, "Select LED Color")

        if new_color.isValid():
            led["r"] = new_color.red()
            led["g"] = new_color.green()
            led["b"] = new_color.blue()
            led['a'] = random.randint(0, 255)  # Add alpha channel for consistency
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

    def start_streaming_frames(self, url, chunk_size=10):
        import websocket
        print("Starting to stream frames to device...")
        try:
            ws = websocket.create_connection(url)
        except Exception as e:
            self.label.setText(f"WebSocket connection failed: {e}")
            self.stream_button.setText("Stream Frames to Device")
            return

        def send_frames(frames):
            try:
                json_data = json.dumps(frames)
                ws.send(json_data)
            except Exception as e:
                print("Failed to send frames:", e)

        for i in range(0, len(self.frames), chunk_size):
            if self.streaming_stop_event.is_set():
                print("Streaming stopped by user.")
                break

            if i + chunk_size > len(self.frames):
                chunk_size = len(self.frames) - i

            frames_chunk = self.frames[i:i+chunk_size]
            if not frames_chunk:
                print("No frames to send.")
                break

            send_frames(frames_chunk)
            time.sleep(DELAY_BETWEEN_SENDS)  # your delay

        ws.close()
        print("Streaming finished.")
        self.label.setText("Streaming finished.")
        self.stream_button.setText("Stream Frames to Device")







def main():
    app = QApplication(sys.argv)
    window = LEDVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
