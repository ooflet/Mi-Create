# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'resourceDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QGridLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QSizePolicy, QStackedWidget,
    QToolButton, QWidget)

import sys

sys.path.append("..")

from coreGettext import QCoreApplication

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(300, 300)
        Dialog.setMinimumSize(QSize(100, 225))
        Dialog.setMaximumSize(QSize(300, 300))
        Dialog.setLayoutDirection(Qt.LeftToRight)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply)

        self.gridLayout.addWidget(self.buttonBox, 1, 2, 1, 1)

        self.addImage = QToolButton(Dialog)
        self.addImage.setObjectName(u"addImage")
        self.addImage.setLayoutDirection(Qt.RightToLeft)
        icon = QIcon()
        icon.addFile(u":/Dark/file-plus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.addImage.setIcon(icon)

        self.gridLayout.addWidget(self.addImage, 1, 1, 1, 1)

        self.stackedWidget = QStackedWidget(Dialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout_2 = QGridLayout(self.page)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.imageSelect = QListWidget(self.page)
        self.imageSelect.setObjectName(u"imageSelect")
        self.imageSelect.setFrameShape(QFrame.NoFrame)
        self.imageSelect.setIconSize(QSize(64, 64))
        self.imageSelect.setUniformItemSizes(False)

        self.gridLayout_2.addWidget(self.imageSelect, 1, 0, 1, 3)

        self.searchLabel = QLabel(self.page)
        self.searchLabel.setObjectName(u"searchLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.searchLabel.sizePolicy().hasHeightForWidth())
        self.searchLabel.setSizePolicy(sizePolicy1)

        self.gridLayout_2.addWidget(self.searchLabel, 0, 0, 1, 1)

        self.searchBar = QLineEdit(self.page)
        self.searchBar.setObjectName(u"searchBar")
        self.searchBar.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.searchBar, 0, 1, 1, 1)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 3)


        self.retranslateUi(Dialog)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Select resource...", None))
        self.addImage.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.searchLabel.setText(QCoreApplication.translate("Dialog", u"Search:", None))
    # retranslateUi

