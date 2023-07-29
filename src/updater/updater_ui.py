# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'updater.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QMainWindow, QProgressBar, QSizePolicy, QVBoxLayout,
    QWidget)
import icons_rc

class Ui_UpdaterWindow(object):
    def setupUi(self, UpdaterWindow):
        if not UpdaterWindow.objectName():
            UpdaterWindow.setObjectName(u"UpdaterWindow")
        UpdaterWindow.resize(600, 384)
        UpdaterWindow.setMinimumSize(QSize(600, 384))
        UpdaterWindow.setMaximumSize(QSize(600, 384))
        UpdaterWindow.setSizeIncrement(QSize(0, 0))
        self.centralwidget = QWidget(UpdaterWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.image = QLabel(self.centralwidget)
        self.image.setObjectName(u"image")
        self.image.setStyleSheet(u"background-color: rgb(20, 20, 20);")

        self.gridLayout.addWidget(self.image, 0, 0, 1, 1)

        self.StatusBar = QFrame(self.centralwidget)
        self.StatusBar.setObjectName(u"StatusBar")
        self.StatusBar.setStyleSheet(u"background-color: rgb(20, 20, 20);")
        self.StatusBar.setFrameShape(QFrame.StyledPanel)
        self.StatusBar.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.StatusBar)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.UpdateStatus = QLabel(self.StatusBar)
        self.UpdateStatus.setObjectName(u"UpdateStatus")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.UpdateStatus.sizePolicy().hasHeightForWidth())
        self.UpdateStatus.setSizePolicy(sizePolicy)
        self.UpdateStatus.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.verticalLayout.addWidget(self.UpdateStatus)

        self.progressBar = QProgressBar(self.StatusBar)
        self.progressBar.setObjectName(u"progressBar")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy1)
        self.progressBar.setCursor(QCursor(Qt.ArrowCursor))
        self.progressBar.setStyleSheet(u"")
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)

        self.verticalLayout.addWidget(self.progressBar)


        self.gridLayout.addWidget(self.StatusBar, 2, 0, 1, 1)

        UpdaterWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(UpdaterWindow)

        QMetaObject.connectSlotsByName(UpdaterWindow)
    # setupUi

    def retranslateUi(self, UpdaterWindow):
        UpdaterWindow.setWindowTitle(QCoreApplication.translate("UpdaterWindow", u"Updater", None))
        self.image.setText(QCoreApplication.translate("UpdaterWindow", u"<html><head/><body><p><img src=\":/Images/MiFaceStudioSplash.png\"/></p></body></html>", None))
        self.UpdateStatus.setText(QCoreApplication.translate("UpdaterWindow", u"Downloading...", None))
    # retranslateUi

