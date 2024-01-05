# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compileDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

import sys
sys.path.append("..")
from coreGettext import QCoreApplication

from PySide6.QtCore import (QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLineEdit, QProgressBar,
    QSizePolicy, QSpacerItem, QStackedWidget, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(500, 300)
        Dialog.setMinimumSize(QSize(500, 300))
        Dialog.setMaximumSize(QSize(500, 300))
        self.verticalLayout_3 = QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.stackedWidget = QStackedWidget(Dialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.gridLayout = QGridLayout(self.page_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 6, 1, 1, 1)

        self.watchfaceName = QLineEdit(self.page_3)
        self.watchfaceName.setObjectName(u"watchfaceName")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.watchfaceName.sizePolicy().hasHeightForWidth())
        self.watchfaceName.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.watchfaceName, 2, 0, 1, 1)

        self.thumbnailLocation = QLineEdit(self.page_3)
        self.thumbnailLocation.setObjectName(u"thumbnailLocation")
        sizePolicy.setHeightForWidth(self.thumbnailLocation.sizePolicy().hasHeightForWidth())
        self.thumbnailLocation.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.thumbnailLocation, 6, 0, 1, 1)

        self.label_6 = QLabel(self.page_3)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 7, 0, 1, 1)

        self.label_4 = QLabel(self.page_3)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setStyleSheet(u"QLabel { font-size: 18pt;}")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_5 = QLabel(self.page_3)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_3)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_2 = QVBoxLayout(self.page)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setStyleSheet(u"QLabel { font-size: 18pt;}")

        self.verticalLayout_2.addWidget(self.label)

        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.label_2)

        self.progressBar = QProgressBar(self.page)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)

        self.verticalLayout_2.addWidget(self.progressBar)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout = QVBoxLayout(self.page_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 0, -1, -1)
        self.label_3 = QLabel(self.page_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setStyleSheet(u"QLabel { font-size: 18pt;}")

        self.verticalLayout.addWidget(self.label_3)

        self.textEdit = QTextEdit(self.page_2)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy3)

        self.verticalLayout.addWidget(self.textEdit)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout_3.addWidget(self.stackedWidget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.NoButton)
        self.buttonBox.setCenterButtons(False)

        self.verticalLayout_3.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Build Project...", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Watchface thumbnail", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Configure project...", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Watchface name", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Build project...", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Building project...", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Build results...", None))
    # retranslateUi

