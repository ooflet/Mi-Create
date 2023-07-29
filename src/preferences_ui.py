# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFontComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)
import icons_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(550, 350)
        Dialog.setMinimumSize(QSize(550, 350))
        Dialog.setMaximumSize(QSize(550, 350))
        icon = QIcon()
        icon.addFile(u":/Dark/MiFaceStudioFavicon.png", QSize(), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.vboxLayout = QVBoxLayout(Dialog)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setElideMode(Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.Interface = QWidget()
        self.Interface.setObjectName(u"Interface")
        self.gridLayout = QGridLayout(self.Interface)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.Interface)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(0)
        self.gridLayout_2.setVerticalSpacing(5)
        self.gridLayout_2.setContentsMargins(-1, 5, 5, 5)
        self.Property = QFrame(self.groupBox)
        self.Property.setObjectName(u"Property")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Property.sizePolicy().hasHeightForWidth())
        self.Property.setSizePolicy(sizePolicy)
        self.Property.setFrameShape(QFrame.NoFrame)
        self.Property.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.Property)
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.themeComboBox = QComboBox(self.Property)
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.setObjectName(u"themeComboBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.themeComboBox.sizePolicy().hasHeightForWidth())
        self.themeComboBox.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.themeComboBox)

        self.languageComboBox = QComboBox(self.Property)
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.setObjectName(u"languageComboBox")
        sizePolicy1.setHeightForWidth(self.languageComboBox.sizePolicy().hasHeightForWidth())
        self.languageComboBox.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.languageComboBox)

        self.fontComboBox = QFontComboBox(self.Property)
        self.fontComboBox.setObjectName(u"fontComboBox")
        sizePolicy1.setHeightForWidth(self.fontComboBox.sizePolicy().hasHeightForWidth())
        self.fontComboBox.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.fontComboBox)

        self.frame = QFrame(self.Property)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setMinimumSize(QSize(0, 30))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.accentColorRed = QPushButton(self.frame)
        self.accentColorRed.setObjectName(u"accentColorRed")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.accentColorRed.sizePolicy().hasHeightForWidth())
        self.accentColorRed.setSizePolicy(sizePolicy3)
        self.accentColorRed.setMinimumSize(QSize(20, 20))
        self.accentColorRed.setStyleSheet(u"background-color: rgb(242, 85, 85);\n"
"border: 0px solid black;\n"
"\n"
"\n"
"")

        self.horizontalLayout.addWidget(self.accentColorRed)

        self.accentColorOrange = QPushButton(self.frame)
        self.accentColorOrange.setObjectName(u"accentColorOrange")
        sizePolicy3.setHeightForWidth(self.accentColorOrange.sizePolicy().hasHeightForWidth())
        self.accentColorOrange.setSizePolicy(sizePolicy3)
        self.accentColorOrange.setMinimumSize(QSize(20, 20))
        self.accentColorOrange.setStyleSheet(u"background-color: rgb(225, 114, 11);\n"
"border: 0px solid black;")

        self.horizontalLayout.addWidget(self.accentColorOrange)

        self.accentColorYellow = QPushButton(self.frame)
        self.accentColorYellow.setObjectName(u"accentColorYellow")
        sizePolicy3.setHeightForWidth(self.accentColorYellow.sizePolicy().hasHeightForWidth())
        self.accentColorYellow.setSizePolicy(sizePolicy3)
        self.accentColorYellow.setMinimumSize(QSize(20, 20))
        self.accentColorYellow.setStyleSheet(u"background-color: rgb(255, 205, 39);\n"
"border: 0px solid black;")

        self.horizontalLayout.addWidget(self.accentColorYellow)

        self.accentColorGreen = QPushButton(self.frame)
        self.accentColorGreen.setObjectName(u"accentColorGreen")
        sizePolicy3.setHeightForWidth(self.accentColorGreen.sizePolicy().hasHeightForWidth())
        self.accentColorGreen.setSizePolicy(sizePolicy3)
        self.accentColorGreen.setMinimumSize(QSize(20, 20))
        self.accentColorGreen.setStyleSheet(u"background-color: rgb(39, 163, 65);\n"
"border: 0px solid black;")

        self.horizontalLayout.addWidget(self.accentColorGreen)

        self.accentColorBlue_3 = QPushButton(self.frame)
        self.accentColorBlue_3.setObjectName(u"accentColorBlue_3")
        sizePolicy3.setHeightForWidth(self.accentColorBlue_3.sizePolicy().hasHeightForWidth())
        self.accentColorBlue_3.setSizePolicy(sizePolicy3)
        self.accentColorBlue_3.setMinimumSize(QSize(20, 20))
        self.accentColorBlue_3.setStyleSheet(u"background-color: rgb(85, 170, 255);\n"
"border: 0px solid black;")

        self.horizontalLayout.addWidget(self.accentColorBlue_3)

        self.accentColorBlue_6 = QPushButton(self.frame)
        self.accentColorBlue_6.setObjectName(u"accentColorBlue_6")
        sizePolicy3.setHeightForWidth(self.accentColorBlue_6.sizePolicy().hasHeightForWidth())
        self.accentColorBlue_6.setSizePolicy(sizePolicy3)
        self.accentColorBlue_6.setMinimumSize(QSize(20, 20))
        self.accentColorBlue_6.setStyleSheet(u"background-color: rgb(146, 107, 255);\n"
"border: 0px solid black;")

        self.horizontalLayout.addWidget(self.accentColorBlue_6)

        self.accentColorBlue_7 = QPushButton(self.frame)
        self.accentColorBlue_7.setObjectName(u"accentColorBlue_7")
        sizePolicy3.setHeightForWidth(self.accentColorBlue_7.sizePolicy().hasHeightForWidth())
        self.accentColorBlue_7.setSizePolicy(sizePolicy3)
        self.accentColorBlue_7.setMinimumSize(QSize(20, 20))
        self.accentColorBlue_7.setStyleSheet(u"background-color: rgb(228, 84, 196);\n"
"border: 0px solid black;")

        self.horizontalLayout.addWidget(self.accentColorBlue_7)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addWidget(self.frame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.gridLayout_2.addWidget(self.Property, 0, 1, 1, 1)

        self.PropertyLabel = QFrame(self.groupBox)
        self.PropertyLabel.setObjectName(u"PropertyLabel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.PropertyLabel.sizePolicy().hasHeightForWidth())
        self.PropertyLabel.setSizePolicy(sizePolicy4)
        self.PropertyLabel.setMinimumSize(QSize(100, 0))
        self.PropertyLabel.setMaximumSize(QSize(100, 16777215))
        self.PropertyLabel.setFrameShape(QFrame.NoFrame)
        self.PropertyLabel.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.PropertyLabel)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.Theme = QLabel(self.PropertyLabel)
        self.Theme.setObjectName(u"Theme")
        sizePolicy5 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.Theme.sizePolicy().hasHeightForWidth())
        self.Theme.setSizePolicy(sizePolicy5)
        self.Theme.setMinimumSize(QSize(0, 22))

        self.verticalLayout_2.addWidget(self.Theme)

        self.Language = QLabel(self.PropertyLabel)
        self.Language.setObjectName(u"Language")
        self.Language.setMinimumSize(QSize(0, 22))

        self.verticalLayout_2.addWidget(self.Language)

        self.label = QLabel(self.PropertyLabel)
        self.label.setObjectName(u"label")
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)
        self.label.setMinimumSize(QSize(0, 22))

        self.verticalLayout_2.addWidget(self.label)

        self.Color = QLabel(self.PropertyLabel)
        self.Color.setObjectName(u"Color")
        self.Color.setMinimumSize(QSize(0, 40))

        self.verticalLayout_2.addWidget(self.Color)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)


        self.gridLayout_2.addWidget(self.PropertyLabel, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.frame_2 = QFrame(self.Interface)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)

        self.gridLayout.addWidget(self.frame_2, 1, 0, 1, 1)

        self.tabWidget.addTab(self.Interface, "")
        self.Keyboard = QWidget()
        self.Keyboard.setObjectName(u"Keyboard")
        self.verticalLayout_4 = QVBoxLayout(self.Keyboard)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_2 = QGroupBox(self.Keyboard)
        self.groupBox_2.setObjectName(u"groupBox_2")

        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.tabWidget.addTab(self.Keyboard, "")
        self.Behaviour = QWidget()
        self.Behaviour.setObjectName(u"Behaviour")
        self.tabWidget.addTab(self.Behaviour, "")

        self.vboxLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.vboxLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Preferences", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"User Interface", None))
        self.themeComboBox.setItemText(0, QCoreApplication.translate("Dialog", u"Dark", None))
        self.themeComboBox.setItemText(1, QCoreApplication.translate("Dialog", u"Light", None))

        self.languageComboBox.setItemText(0, QCoreApplication.translate("Dialog", u"English", None))
        self.languageComboBox.setItemText(1, QCoreApplication.translate("Dialog", u"\u7e41\u9ad4\u4e2d\u6587", None))
        self.languageComboBox.setItemText(2, QCoreApplication.translate("Dialog", u"\u7b80\u4f53\u4e2d\u6587", None))
        self.languageComboBox.setItemText(3, QCoreApplication.translate("Dialog", u"\u0420\u0443\u0441\u0441\u043a\u0438\u0439", None))

        self.accentColorRed.setText("")
        self.accentColorOrange.setText("")
        self.accentColorYellow.setText("")
        self.accentColorGreen.setText("")
        self.accentColorBlue_3.setText("")
        self.accentColorBlue_6.setText("")
        self.accentColorBlue_7.setText("")
        self.Theme.setText(QCoreApplication.translate("Dialog", u"Theme:", None))
        self.Language.setText(QCoreApplication.translate("Dialog", u"Language:", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Font:", None))
        self.Color.setText(QCoreApplication.translate("Dialog", u"Accent Color:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Interface), QCoreApplication.translate("Dialog", u"Interface", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"GroupBox", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Keyboard), QCoreApplication.translate("Dialog", u"Keyboard", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Behaviour), QCoreApplication.translate("Dialog", u"Behaviour", None))
    # retranslateUi

