from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6.QtGui import QPainter, QColor

# Constants
CIRCLE_DIAMETER = 14
MARGIN = 3


def take_closest(num, collection):
    return min(collection, key=lambda x: abs(x - num))


class SwitchCircle(QWidget):
    def __init__(self, parent, animation_curve, animation_duration):
        super().__init__(parent=parent)
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(animation_duration)

        self.setFixedSize(CIRCLE_DIAMETER, CIRCLE_DIAMETER)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        color = self.parent().palette().text().color()
        painter.setBrush(color)
        painter.drawEllipse(0, 0, CIRCLE_DIAMETER, CIRCLE_DIAMETER)

    def set_color(self, _):  # kept for compatibility
        self.update()

    def mousePressEvent(self, event):
        self.animation.stop()
        self.oldX = event.globalPosition().x()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().x() - self.oldX
        new_x = delta + self.x()
        min_x, max_x = self.parent().get_circle_range()

        # Clamp x within range
        new_x = max(min_x, min(max_x, new_x))
        self.move(int(new_x), self.y())
        self.oldX = event.globalPosition().x()
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        min_x, max_x = self.parent().get_circle_range()
        try:
            go_to = take_closest(self.x(), (min_x, max_x))
            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(QPoint(go_to, self.y()))
            self.animation.start()
            self.parent().setChecked(go_to == max_x)
        except AttributeError:
            pass
        return super().mouseReleaseEvent(event)


class SwitchControl(QCheckBox):
    def __init__(self, parent=None, animation_curve=QEasingCurve.Type.OutQuint,
                 animation_duration=200, checked=False, change_cursor=True):
        super().__init__(parent=parent)
        self.setFixedSize(35, 20)

        if change_cursor:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.animation_curve = animation_curve
        self.animation_duration = animation_duration

        # Circle widget
        self.__circle = SwitchCircle(self, self.animation_curve, self.animation_duration)

        self.auto = False
        self.pos_on_press = None

        self.update_circle_position(checked)
        self.setChecked(checked)

        # Animation object
        self.animation = QPropertyAnimation(self.__circle, b"pos")
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(animation_duration)

    def get_circle_range(self):
        min_x = MARGIN
        max_x = self.width() - CIRCLE_DIAMETER - MARGIN
        return min_x, max_x

    def update_circle_position(self, checked):
        x = self.get_circle_range()[1] if checked else self.get_circle_range()[0]
        y = (self.height() - CIRCLE_DIAMETER) // 2
        self.__circle.move(x, y)

    def start_animation(self, checked):
        self.animation.stop()
        start = self.__circle.pos()
        end_x = self.get_circle_range()[1] if checked else self.get_circle_range()[0]
        end_y = start.y()  # vertical stays fixed
        self.animation.setStartValue(start)
        self.animation.setEndValue(QPoint(end_x, end_y))
        self.setChecked(checked)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        palette = self.palette()
        radius = self.height() / 2

        if self.isChecked():
            color = palette.highlight().color()
        else:
            color = palette.midlight().color()

        painter.setBrush(color)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)

    def hitButton(self, pos):
        return self.contentsRect().contains(pos)

    def mousePressEvent(self, event):
        self.auto = True
        self.pos_on_press = event.globalPosition()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.globalPosition() != self.pos_on_press:
            self.auto = False
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.auto:
            self.auto = False
            self.start_animation(not self.isChecked())
