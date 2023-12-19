# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'newProject.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QStackedWidget,
    QToolButton, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(500, 300)
        Dialog.setMinimumSize(QSize(500, 300))
        Dialog.setMaximumSize(QSize(500, 300))
        self.formLayout = QFormLayout(Dialog)
        self.formLayout.setObjectName(u"formLayout")
        self.stackedWidget = QStackedWidget(Dialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout = QGridLayout(self.page)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setContentsMargins(-1, 0, -1, -1)
        self.folderLocation = QLineEdit(self.page)
        self.folderLocation.setObjectName(u"folderLocation")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.folderLocation.sizePolicy().hasHeightForWidth())
        self.folderLocation.setSizePolicy(sizePolicy)
        self.folderLocation.setReadOnly(False)
        self.folderLocation.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.folderLocation, 6, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 6, 2, 1, 1)

        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.page)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setStyleSheet(u"QLabel { font-size: 18pt;}")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.folderShow = QToolButton(self.page)
        self.folderShow.setObjectName(u"folderShow")
        icon = QIcon()
        icon.addFile(u":/Dark/folder-open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.folderShow.setIcon(icon)

        self.gridLayout.addWidget(self.folderShow, 6, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 0, 1, 1)

        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName(u"label_4")
        sizePolicy2.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)

        self.deviceSelection = QComboBox(self.page)
        self.deviceSelection.setObjectName(u"deviceSelection")
        sizePolicy3 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.deviceSelection.sizePolicy().hasHeightForWidth())
        self.deviceSelection.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.deviceSelection, 2, 0, 1, 1)

        self.projectName = QLineEdit(self.page)
        self.projectName.setObjectName(u"projectName")
        sizePolicy.setHeightForWidth(self.projectName.sizePolicy().hasHeightForWidth())
        self.projectName.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.projectName, 4, 0, 1, 1)

        self.stackedWidget.addWidget(self.page)

        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.stackedWidget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"New Project...", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Select device", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Project name", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Create project...", None))
        self.folderShow.setText("")
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Project location", None))
    # retranslateUi

