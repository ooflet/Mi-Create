from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QToolButton, QStackedWidget
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

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
    def __init__(self, name, pixmap, path, openProject, parent=None):
        super().__init__(parent)

        self.path = path
        self.openProjectFunction = openProject

        self.setObjectName("fileEntry")
        self.setFixedSize(172, 220)

        self.itemLayout = QVBoxLayout(self)
        self.itemLayout.setContentsMargins(8, 8, 8, 8)
        self.itemLayout.setSpacing(4)

        self.icon = QLabel()
        self.icon.setObjectName("imageFrame")
        self.icon.setFixedSize(155, 155)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setPixmap(pixmap.scaled(135, 135, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.label = QLabel(name)
        self.sizeLabel = QLabel(f"{pixmap.width()}x{pixmap.height()}")
        self.sizeLabel.setStyleSheet("color: palette(light)")

        self.itemLayout.addWidget(self.icon)
        self.itemLayout.addStretch()
        self.itemLayout.addWidget(self.label)
        self.itemLayout.addWidget(self.sizeLabel)

    def updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, a0):
        self.setProperty("selected", True)
        self.updateStyle()
        QApplication.instance().processEvents()
        self.openProjectFunction(self.path)
        self.setProperty("selected", False)
        self.updateStyle()
        return super().mousePressEvent(a0)

    