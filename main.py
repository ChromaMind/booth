import sys
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QSlider, QVBoxLayout, QFileDialog, QLabel
)
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import pygame
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env into os.environ
API_KEY = os.environ.get("ASI1_API_KEY")
if not API_KEY:
    raise ValueError("Missing ASI1_API_KEY in environment variables")


class FrameFetchThread(QThread):
    frames_received = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_path, api_key, api_url):
        super().__init__()
        self.audio_path = audio_path
        self.api_key = api_key
        self.api_url = api_url

    def run(self):
        try:
            # Read audio file bytes
            with open(self.audio_path, "rb") as f:
                audio_bytes = f.read()

            # Replace with your real API call
            # Here, we're simulating with a dummy response for demo
            # Example: send multipart/form-data with audio to your API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            files = {"audio_file": (self.audio_path, audio_bytes)}

            response = requests.post(self.api_url, headers=headers, files=files)
            response.raise_for_status()
            frames = response.json()["frames"]

            # Frames should be a list of frames, each frame is a 2D array of LED dicts: [{"r":0,"g":0,"b":0},...]
            self.frames_received.emit(frames)

        except Exception as e:
            self.error_occurred.emit(str(e))


class LEDFrameViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.rows = 0
        self.columns = 0
        self.current_frame = 0
        self.is_playing = False
        self.api_key = API_KEY
        self.api_url = "https://api.asi1.ai/v1"

        self.setWindowTitle("LED Music Visualizer with AI Frames")
        self.setMinimumSize(800, 600)

        self.status_label = QLabel("Upload audio to start")
        self.upload_button = QPushButton("Upload Audio")
        self.upload_button.clicked.connect(self.upload_audio)

        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.slider_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        pygame.mixer.init()
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        self.audio_path = None

    def paintEvent(self, event):
        if not self.frames:
            return

        painter = QPainter(self)
        w = self.width()
        h = self.height() - 150  # leave space for buttons and status

        cell_w = w / self.columns
        cell_h = h / self.rows

        frame = self.frames[self.current_frame]
        for y in range(self.rows):
            for x in range(self.columns):
                led = frame[y][x]
                color = QColor(led["r"], led["g"], led["b"])
                painter.fillRect(int(x * cell_w), int(y * cell_h), int(cell_w), int(cell_h), color)

    def upload_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav)")
        if not file_path:
            return

        self.audio_path = file_path
        self.status_label.setText("Uploading audio and generating frames... please wait.")
        self.play_button.setEnabled(False)
        self.slider.setEnabled(False)

        self.thread = FrameFetchThread(file_path, self.api_key, self.api_url)
        self.thread.frames_received.connect(self.frames_received)
        self.thread.error_occurred.connect(self.api_error)
        self.thread.start()

    def frames_received(self, frames):
        if not frames or not isinstance(frames, list):
            self.status_label.setText("Error: Invalid frames data received")
            return

        self.frames = frames
        self.rows = len(frames[0])
        self.columns = len(frames[0][0])
        self.current_frame = 0

        self.slider.setMaximum(len(frames) - 1)
        self.slider.setEnabled(True)
        self.play_button.setEnabled(True)
        self.status_label.setText(f"Loaded {len(frames)} frames from AI model")

        # Load and play audio with pygame
        pygame.mixer.music.load(self.audio_path)

        self.update()

    def api_error(self, msg):
        self.status_label.setText(f"Error contacting AI model: {msg}")

    def slider_changed(self, value):
        self.current_frame = value
        self.update()

    def toggle_play(self):
        if self.is_playing:
            self.timer.stop()
            pygame.mixer.music.pause()
            self.play_button.setText("Play")
        else:
            self.timer.start(100)  # 10 FPS animation
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.play_button.setText("Pause")
        self.is_playing = not self.is_playing

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            pygame.mixer.music.stop()
            self.timer.stop()
            self.is_playing = False
            self.play_button.setText("Play")
        self.slider.setValue(self.current_frame)
        self.update()


def main():
    app = QApplication(sys.argv)
    viewer = LEDFrameViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
