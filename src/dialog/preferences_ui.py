# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGridLayout,
    QGroupBox, QLabel, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)

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
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(5)
        self.formLayout.setContentsMargins(20, 9, 9, 9)
        self.Theme = QLabel(self.groupBox)
        self.Theme.setObjectName(u"Theme")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Theme.sizePolicy().hasHeightForWidth())
        self.Theme.setSizePolicy(sizePolicy)
        self.Theme.setMinimumSize(QSize(0, 22))

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.Theme)

        self.themeComboBox = QComboBox(self.groupBox)
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.setObjectName(u"themeComboBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.themeComboBox.sizePolicy().hasHeightForWidth())
        self.themeComboBox.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.themeComboBox)

        self.languageComboBox = QComboBox(self.groupBox)
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.setObjectName(u"languageComboBox")
        sizePolicy1.setHeightForWidth(self.languageComboBox.sizePolicy().hasHeightForWidth())
        self.languageComboBox.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.languageComboBox)

        self.Language = QLabel(self.groupBox)
        self.Language.setObjectName(u"Language")
        self.Language.setMinimumSize(QSize(125, 22))

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.Language)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.tabWidget.addTab(self.Interface, "")
        self.Behaviour = QWidget()
        self.Behaviour.setObjectName(u"Behaviour")
        self.verticalLayout = QVBoxLayout(self.Behaviour)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(self.Behaviour)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_3 = QFormLayout(self.groupBox_2)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setHorizontalSpacing(0)
        self.formLayout_3.setVerticalSpacing(5)
        self.formLayout_3.setContentsMargins(20, 9, 9, 9)
        self.Theme_3 = QLabel(self.groupBox_2)
        self.Theme_3.setObjectName(u"Theme_3")
        sizePolicy.setHeightForWidth(self.Theme_3.sizePolicy().hasHeightForWidth())
        self.Theme_3.setSizePolicy(sizePolicy)
        self.Theme_3.setMinimumSize(QSize(0, 22))

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.Theme_3)

        self.Language_3 = QLabel(self.groupBox_2)
        self.Language_3.setObjectName(u"Language_3")
        self.Language_3.setMinimumSize(QSize(125, 22))

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.Language_3)

        self.SnapToGuides = QCheckBox(self.groupBox_2)
        self.SnapToGuides.setObjectName(u"SnapToGuides")
        self.SnapToGuides.setMinimumSize(QSize(0, 22))

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.SnapToGuides)

        self.DeviceOutlineVisible = QCheckBox(self.groupBox_2)
        self.DeviceOutlineVisible.setObjectName(u"DeviceOutlineVisible")
        self.DeviceOutlineVisible.setMinimumSize(QSize(0, 22))
        self.DeviceOutlineVisible.setChecked(True)

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.DeviceOutlineVisible)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setSizeIncrement(QSize(0, 0))

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.label)

        self.AntialiasingEnabled = QCheckBox(self.groupBox_2)
        self.AntialiasingEnabled.setObjectName(u"AntialiasingEnabled")
        self.AntialiasingEnabled.setMinimumSize(QSize(0, 22))
        self.AntialiasingEnabled.setSizeIncrement(QSize(0, 0))
        self.AntialiasingEnabled.setChecked(True)

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.AntialiasingEnabled)


        self.verticalLayout.addWidget(self.groupBox_2)

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
        self.Theme.setText(QCoreApplication.translate("Dialog", u"Theme", None))
        self.themeComboBox.setItemText(0, QCoreApplication.translate("Dialog", u"Dark", None))
        self.themeComboBox.setItemText(1, QCoreApplication.translate("Dialog", u"Light", None))

        self.languageComboBox.setItemText(0, QCoreApplication.translate("Dialog", u"English", None))
        self.languageComboBox.setItemText(1, QCoreApplication.translate("Dialog", u"\u7e41\u9ad4\u4e2d\u6587", None))
        self.languageComboBox.setItemText(2, QCoreApplication.translate("Dialog", u"\u7b80\u4f53\u4e2d\u6587", None))
        self.languageComboBox.setItemText(3, QCoreApplication.translate("Dialog", u"\u0420\u0443\u0441\u0441\u043a\u0438\u0439", None))

        self.Language.setText(QCoreApplication.translate("Dialog", u"Language", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Interface), QCoreApplication.translate("Dialog", u"Interface", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Behaviour", None))
        self.Theme_3.setText(QCoreApplication.translate("Dialog", u"Snap to Guides", None))
        self.Language_3.setText(QCoreApplication.translate("Dialog", u"Show Device Outline", None))
        self.SnapToGuides.setText("")
        self.DeviceOutlineVisible.setText("")
        self.label.setText(QCoreApplication.translate("Dialog", u"Enable Antialiasing", None))
        self.AntialiasingEnabled.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Behaviour), QCoreApplication.translate("Dialog", u"Behaviour", None))
    # retranslateUi

