from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QToolButton, QStackedWidget
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from datetime import datetime, timedelta

def getTimestamp(past, now=None):
    if not past:
        return "some time ago"

    now = now or datetime.now()
    diff = now - past

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    months = days // 30
    years = days // 365

    if seconds < 60:
        return "just now"
    elif minutes < 60:
        return f"{int(minutes)} minute(s) ago"
    elif hours < 24:
        return f"{int(hours)} hour(s) ago"
    elif days < 30:
        return f"{int(days)} day(s) ago"
    elif days < 365:
        return f"{int(months)} month(s) ago"
    else:
        return f"{int(years)} year(s) ago"

class HoverableFileItem(QWidget):
    def __init__(self, name, pixmap, parent=None):
        super().__init__(parent)

        self.itemLayout = QHBoxLayout(self)
        self.itemLayout.setSpacing(10)

        self.icon = QLabel()
        self.icon.setObjectName("imageFrame")
        self.icon.setFixedSize(48, 48)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.labelLayout = QVBoxLayout()
        self.labelLayout.setSpacing(2)
        self.label = QLabel(name)
        self.label.setMaximumWidth(200)
        self.label.setToolTip(name)
        self.sizeLabel = QLabel(f"{pixmap.width()}x{pixmap.height()}")
        self.sizeLabel.setStyleSheet("color: palette(light)")
        
        self.labelLayout.addStretch()
        self.labelLayout.addWidget(self.label)
        self.labelLayout.addWidget(self.sizeLabel)
        self.labelLayout.addStretch()

        self.deleteBtn = QToolButton()
        self.deleteBtn.setIcon(QIcon.fromTheme("edit-delete"))
        self.deleteBtn.setToolTip("Delete")
        self.deleteBtn.setVisible(False)

        self.itemLayout.addWidget(self.icon)
        self.itemLayout.addLayout(self.labelLayout)
        self.itemLayout.addStretch()
        self.itemLayout.addWidget(self.deleteBtn)

    def enterEvent(self, event):
        self.deleteBtn.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.deleteBtn.setVisible(False)
        super().leaveEvent(event)

class RecentProjectItem(QFrame):
    opened = pyqtSignal(str)
    removed = pyqtSignal(str)

    def __init__(self, name, pixmap, path, lastOpened=None, parent=None):
        super().__init__(parent)

        self.path = path

        self.setObjectName("fileEntry")
        self.setFixedSize(172, 220)

        self.itemLayout = QVBoxLayout(self)
        self.itemLayout.setContentsMargins(8, 8, 8, 8)
        self.itemLayout.setSpacing(4)

        self.icon = QLabel()
        self.icon.setObjectName("imageFrame")
        self.icon.setFixedSize(155, 155)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if pixmap.isNull():
            self.icon.setPixmap(QIcon.fromTheme("widget-image").pixmap(135, 135))
        else:
            self.icon.setPixmap(pixmap.scaled(135, 135, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.label = QLabel(name)
        self.label.setMaximumWidth(160)
        self.label.setToolTip(name)

        if lastOpened:
            lastOpened = datetime.fromisoformat(lastOpened)

        self.timestampLabel = QLabel(f"Opened {getTimestamp(lastOpened)}")
        self.timestampLabel.setStyleSheet("color: palette(light)")

        self.itemLayout.addWidget(self.icon)
        self.itemLayout.addStretch()
        self.itemLayout.addWidget(self.label)
        self.itemLayout.addWidget(self.timestampLabel)

        self.removeButton = QToolButton(self)
        self.removeButton.setIcon(QIcon.fromTheme("application-close"))  # Replace with your desired icon
        self.removeButton.setAutoRaise(True)
        self.removeButton.resize(30, 30)
        self.removeButton.move(self.width() - self.removeButton.width() - 9, 10)
        self.removeButton.clicked.connect(lambda: self.removed.emit(path))
        self.removeButton.hide()

    def updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def enterEvent(self, event):
        self.removeButton.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.removeButton.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, a0):
        self.setProperty("selected", True)
        self.updateStyle()
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0):
        self.setProperty("selected", False)
        self.updateStyle()
        QApplication.instance().processEvents()
        self.opened.emit(self.path)
        return super().mouseReleaseEvent(a0)
    