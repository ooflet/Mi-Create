# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
    QDialogButtonBox, QFrame, QGridLayout, QGroupBox,
    QLabel, QLayout, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)
import resources.icons_rc as icons_rc

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
        self.gridLayout_3 = QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.gridLayout_3.addWidget(self.buttonBox, 1, 1, 1, 1)

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

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.gridLayout_2.addWidget(self.Property, 0, 1, 1, 1)

        self.PropertyLabel = QFrame(self.groupBox)
        self.PropertyLabel.setObjectName(u"PropertyLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.PropertyLabel.sizePolicy().hasHeightForWidth())
        self.PropertyLabel.setSizePolicy(sizePolicy2)
        self.PropertyLabel.setMinimumSize(QSize(100, 0))
        self.PropertyLabel.setMaximumSize(QSize(100, 16777215))
        self.PropertyLabel.setFrameShape(QFrame.NoFrame)
        self.PropertyLabel.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.PropertyLabel)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.Theme = QLabel(self.PropertyLabel)
        self.Theme.setObjectName(u"Theme")
        sizePolicy3 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.Theme.sizePolicy().hasHeightForWidth())
        self.Theme.setSizePolicy(sizePolicy3)
        self.Theme.setMinimumSize(QSize(0, 22))

        self.verticalLayout_2.addWidget(self.Theme)

        self.Language = QLabel(self.PropertyLabel)
        self.Language.setObjectName(u"Language")
        self.Language.setMinimumSize(QSize(0, 22))

        self.verticalLayout_2.addWidget(self.Language)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)


        self.gridLayout_2.addWidget(self.PropertyLabel, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)

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
        self.verticalLayout = QVBoxLayout(self.Behaviour)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_3 = QGroupBox(self.Behaviour)
        self.groupBox_3.setObjectName(u"groupBox_3")

        self.verticalLayout.addWidget(self.groupBox_3)

        self.tabWidget.addTab(self.Behaviour, "")

        self.gridLayout_3.addWidget(self.tabWidget, 0, 1, 1, 1)


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

        self.Theme.setText(QCoreApplication.translate("Dialog", u"Theme:", None))
        self.Language.setText(QCoreApplication.translate("Dialog", u"Language:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Interface), QCoreApplication.translate("Dialog", u"Interface", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Keyboard Shortcuts", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Keyboard), QCoreApplication.translate("Dialog", u"Keyboard", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Behaviour", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Behaviour), QCoreApplication.translate("Dialog", u"Behaviour", None))
    # retranslateUi

