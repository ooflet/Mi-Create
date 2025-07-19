from PyQt6.QtWidgets import QFrame, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class RubberBand(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setWindowFlags(Qt.WindowType.SubWindow)
        #self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setObjectName("rubberBand")
        self.setHidden(True)

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityEffect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacityEffect)

        self._fadeAnim = QPropertyAnimation(self.opacityEffect, b"opacity")
        self._fadeAnim.setDuration(250)
        self._fadeAnim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._fadeAnim.finished.connect(self.hide)

    def stopFadeOut(self):
        self._fadeAnim.stop()
        self.opacityEffect.setOpacity(1.0)

    def startFadeOut(self):
        print("fade")
        self._fadeAnim.stop()
        self._fadeAnim.setStartValue(1.0)
        self._fadeAnim.setEndValue(0.0)
        self._fadeAnim.start()
