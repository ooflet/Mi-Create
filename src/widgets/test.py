import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QBrush, QColor

class ProgressGauge(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Progress Gauge")

        # Create main layout
        main_layout = QVBoxLayout()

        # Create input fields
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Start Angle:"))
        self.start_angle_input = QLineEdit()
        input_layout.addWidget(self.start_angle_input)
        input_layout.addWidget(QLabel("End Angle:"))
        self.end_angle_input = QLineEdit()
        input_layout.addWidget(self.end_angle_input)

        # Create a button to draw the progress gauge
        draw_button = QPushButton("Draw Progress Gauge")
        draw_button.clicked.connect(self.draw_progress_gauge)

        # Add input layout and button to the main layout
        main_layout.addLayout(input_layout)
        main_layout.addWidget(draw_button)

        # Create QGraphicsView and QGraphicsScene
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)

        # Add graphics view to the main layout
        main_layout.addWidget(self.graphics_view)

        # Set the main layout to the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def draw_progress_gauge(self):
        # Clear the previous scene
        self.scene.clear()

        # Get the start and end angles from the input fields
        start_angle = int(self.start_angle_input.text())
        end_angle = int(self.end_angle_input.text())

        # Calculate the span angle
        span_angle = end_angle - start_angle

        # Draw the progress gauge
        rect = QRectF(50, 50, 200, 200)  # Defines the bounding rectangle
        ellipse = QGraphicsEllipseItem(rect)
        ellipse.setStartAngle(start_angle * 16)  # PyQt uses 1/16th of a degree
        ellipse.setSpanAngle(span_angle * 16)  # PyQt uses 1/16th of a degree
        ellipse.setBrush(QBrush(QColor(0, 255, 0)))  # Green color

        # Add the ellipse to the scene
        self.scene.addItem(ellipse)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressGauge()
    window.show()
    sys.exit(app.exec())
