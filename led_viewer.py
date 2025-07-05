import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QSlider, QLabel, QColorDialog, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from pydub import AudioSegment
import pygame

LED_ROWS = 2
LED_COLS = 16
FPS = 30

class LEDVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LED Audio Visualizer Editor")
        self.setMinimumSize(900, 500)

        self.frames = []
        self.frame_duration_ms = 1000 / FPS
        self.total_duration_ms = 0
        self.audio_loaded = False
        self.selected_led = None
        self.playback_speed = 1.0

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

        # Layouts
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.upload_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(QLabel("Speed:"))
        control_layout.addWidget(self.speed_box)

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

        self.generate_led_frames(file_path)

        pygame.mixer.music.load(file_path)
        self.slider.setMaximum(len(self.frames) - 1)
        self.slider.setEnabled(True)
        self.play_button.setEnabled(True)

        self.audio_loaded = True
        self.update()

    def generate_led_frames(self, file_path):
        audio = AudioSegment.from_file(file_path)
        self.total_duration_ms = len(audio)
        total_frames = int(self.total_duration_ms / self.frame_duration_ms)

        self.frames = []
        for _ in range(total_frames):
            frame = [
                [{"r": random.randint(0, 255),
                  "g": random.randint(0, 255),
                  "b": random.randint(0, 255)}
                 for _ in range(LED_COLS)]
                for _ in range(LED_ROWS)
            ]
            self.frames.append(frame)

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
            self.timer.start(int(1000 / (FPS * self.playback_speed)))

    def update_frame(self):
        if not pygame.mixer.music.get_busy():
            self.timer.stop()
            self.play_button.setText("Play")
            return

        pos_ms = pygame.mixer.music.get_pos()
        adjusted_ms = pos_ms * self.playback_speed
        current_frame = int(adjusted_ms / self.frame_duration_ms)

        if current_frame < len(self.frames):
            self.slider.blockSignals(True)
            self.slider.setValue(current_frame)
            self.slider.blockSignals(False)
            self.update()
        else:
            pygame.mixer.music.stop()
            self.timer.stop()
            self.play_button.setText("Play")

    def slider_changed(self, value):
        if not self.frames:
            return
        time_ms = int(value * self.frame_duration_ms / self.playback_speed)
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
            self.timer.start(int(1000 / (FPS * self.playback_speed)))

    def paintEvent(self, event):
        if not self.frames:
            return

        painter = QPainter(self)
        w = self.width()
        h = self.height() - 150  # Control space

        cell_w = w / LED_COLS
        cell_h = h / LED_ROWS

        frame_index = self.slider.value()
        if frame_index >= len(self.frames):
            return

        frame = self.frames[frame_index]

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

        led = self.frames[frame_index][row][col]
        current_color = QColor(led["r"], led["g"], led["b"])
        new_color = QColorDialog.getColor(current_color, self, "Select LED Color")

        if new_color.isValid():
            led["r"] = new_color.red()
            led["g"] = new_color.green()
            led["b"] = new_color.blue()
            self.update()


def main():
    app = QApplication(sys.argv)
    window = LEDVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
