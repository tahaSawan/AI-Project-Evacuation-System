import sys
import cv2
import json
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 10

class MapEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Editor with PyQt6")
        self.setGeometry(100, 100, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.image = None
        self.walls = set()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        image_layout = QHBoxLayout()

        self.threshold_label = QLabel(self)
        self.threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.threshold_label.setText("Threshold Image")
        image_layout.addWidget(self.threshold_label)

        self.map_label = QLabel(self)
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setText("Map View")
        image_layout.addWidget(self.map_label)

        main_layout.addLayout(image_layout)

        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 255)
        self.slider.setValue(128)
        self.slider.valueChanged.connect(self.apply_threshold)
        main_layout.addWidget(self.slider)

        self.load_button = QPushButton("Load Map Image", self)
        self.load_button.clicked.connect(self.load_image)
        main_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Map", self)
        self.save_button.clicked.connect(self.save_map)
        main_layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            if self.image is None:
                print("Error: Could not load image.")
                return
            self.image = cv2.resize(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.apply_threshold()

    def apply_threshold(self):
        if self.image is None:
            return

        threshold = self.slider.value()
        _, binary_image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY)

        self.walls = set()
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                if binary_image[y, x] == 0:
                    self.walls.add((x, y))

        self.update_image_label(binary_image, self.threshold_label)

        map_image = np.ones((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.uint8) * 255
        for x, y in self.walls:
            cv2.rectangle(map_image, (x, y), (x + GRID_SIZE, y + GRID_SIZE), 0, -1)

        self.update_image_label(map_image, self.map_label)

    def update_image_label(self, image, label):
        qimage = QImage(
            image.data,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            QImage.Format.Format_Grayscale8,
        )
        label.setPixmap(QPixmap.fromImage(qimage))

    def save_map(self):
        if not self.walls:
            print("No map to save.")
            return
        wall_list = [{"x": x, "y": y} for x, y in self.walls]
        with open("map.json", "w") as f:
            json.dump(wall_list, f, indent=4)
        print("Map saved as 'map.json'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MapEditor()
    editor.show()
    sys.exit(app.exec())
