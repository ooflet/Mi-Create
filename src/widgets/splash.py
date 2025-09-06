from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap, QFont, QFontDatabase, QPainter
from PyQt6.QtCore import Qt, QRect

class Splash(QSplashScreen):
    def __init__(self, pixmap, version):
        super().__init__(pixmap)
        id = QFontDatabase.addApplicationFont(":/Fonts/Inter.ttf")
        print(QFontDatabase.applicationFontFamilies(id))
        self.text = ""
        self.contextFont = QFont("Inter Medium", 8)
        self.messageFont = QFont("Inter SemiBold", 12)
        self.text_pos = (50, 340)  # position for main message
        self.context_rect = QRect(52, 170, 200, 80)  # x, y, width, height for wrapping

        self.contributors = ["vonfritz", "Pranav-ONLY", "frankh93", "Zha0fusion", "neizod", "billabongbruno"]

        self.context_string = f"Version {version}\n\nThank you to contributors {", ".join(self.contributors)}"

    def show_message(self, message):
        self.text = message
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.white)

        # Draw wrapped context text
        painter.setFont(self.contextFont)
        painter.drawText(self.context_rect,
                         Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                         self.context_string)

        # Draw main message
        if self.text:
            painter.setFont(self.messageFont)
            painter.drawText(self.text_pos[0], self.text_pos[1], self.text)

def show_splash(version):
    splash = Splash(QPixmap(":/Images/splash.png"), version)
    splash.show()
    return splash
