from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

def show_splash():
    splash = QSplashScreen(QPixmap(":/Images/splash.png"))
    splash.show()
    return splash
