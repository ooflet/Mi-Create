from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsView, QGraphicsScene, QApplication,
    QVBoxLayout, QWidget, QSlider, QLabel, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath

class gview(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            zoom_factor = 1.25 if delta > 0 else 1 / 1.25
            self.scale(zoom_factor, zoom_factor)

        elif modifiers == Qt.AltModifier:
            scroll_delta = event.angleDelta().x()
            scroll_value = self.horizontalScrollBar().value() - scroll_delta
            self.horizontalScrollBar().setValue(scroll_value)
        else:
            scroll_delta = event.angleDelta().y()
            scroll_value = self.verticalScrollBar().value() - scroll_delta
            self.verticalScrollBar().setValue(scroll_value)

class CircularArcItem(QGraphicsItem):
    def __init__(self, rect, start_angle, span_angle, parent=None):
        super().__init__(parent)
        self.rect = QRectF(rect)
        self.start_angle = start_angle
        self.span_angle = span_angle

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen()
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(15)
        painter.setPen(pen)

        path = QPainterPath()
        path.arcMoveTo(self.rect, self.start_angle)
        path.arcTo(self.rect, self.start_angle, self.span_angle)

        painter.drawPath(path)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.view = gview(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.arc_item = CircularArcItem(QRectF(50, 50, 200, 200), 0, 90)
        self.scene.addItem(self.arc_item)

        self.start_angle_slider = QSlider(Qt.Horizontal)
        self.start_angle_slider.setRange(0, 360)
        self.start_angle_slider.setValue(0)
        self.start_angle_slider.valueChanged.connect(self.updateArcItem)

        self.span_angle_slider = QSlider(Qt.Horizontal)
        self.span_angle_slider.setRange(0, 360)
        self.span_angle_slider.setValue(90)
        self.span_angle_slider.valueChanged.connect(self.updateArcItem)

        self.start_angle_label = QLabel("Start Angle:")
        self.start_angle_input = QLineEdit()
        self.start_angle_input.textChanged.connect(self.updateSliderFromText)

        self.span_angle_label = QLabel("Span Angle:")
        self.span_angle_input = QLineEdit()
        self.span_angle_input.textChanged.connect(self.updateSliderFromText)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.start_angle_label)
        slider_layout.addWidget(self.start_angle_slider)
        slider_layout.addWidget(self.start_angle_input)
        slider_layout.addWidget(self.span_angle_label)
        slider_layout.addWidget(self.span_angle_slider)
        slider_layout.addWidget(self.span_angle_input)
        layout.addLayout(slider_layout)

        self.setWindowTitle("Circular Arc Item with Sliders and Text Fields")
        self.setGeometry(100, 100, 500, 600)

    def updateArcItem(self):
        self.arc_item.start_angle = self.start_angle_slider.value()
        self.arc_item.span_angle = self.span_angle_slider.value()
        self.scene.update()

        # Update text fields
        self.start_angle_input.setText(str(self.start_angle_slider.value()))
        self.span_angle_input.setText(str(self.span_angle_slider.value()))

    def updateSliderFromText(self):
        start_angle_text = self.start_angle_input.text()
        span_angle_text = self.span_angle_input.text()

        if start_angle_text.isdigit():
            self.start_angle_slider.setValue(int(start_angle_text))

        if span_angle_text.isdigit():
            self.span_angle_slider.setValue(int(span_angle_text))

def main():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()

