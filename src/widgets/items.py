from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QToolButton, QStackedWidget
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
        self.icon.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))

        self.labelLayout = QVBoxLayout()
        self.labelLayout.setSpacing(2)
        self.label = QLabel(name)
        self.sizeLabel = QLabel(f"{pixmap.width()}x{pixmap.height()}")
        self.sizeLabel.setStyleSheet("color: palette(light)")
        
        self.labelLayout.addStretch()
        self.labelLayout.addWidget(self.label)
        self.labelLayout.addWidget(self.sizeLabel)
        self.labelLayout.addStretch()

        self.moreBtn = QToolButton()
        self.moreBtn.setIcon(QIcon.fromTheme("application-more"))
        self.moreBtn.setToolTip("More")
        self.moreBtn.setVisible(False)

        self.itemLayout.addWidget(self.icon)
        self.itemLayout.addLayout(self.labelLayout)
        self.itemLayout.addStretch()
        self.itemLayout.addWidget(self.moreBtn)

    def enterEvent(self, event):
        self.moreBtn.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.moreBtn.setVisible(False)
        super().leaveEvent(event)

