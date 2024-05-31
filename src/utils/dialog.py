# Dialog Manager
# tostr 2024
import sys
import gettext

sys.path.append("..")

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QComboBox, QToolButton, QSpinBox, QVBoxLayout, 
                             QHBoxLayout, QSizePolicy, QSpacerItem, QDialogButtonBox, QFileDialog)

from translate import QCoreApplication

class MultiFieldDialog(QDialog):
    def __init__(self, parent, windowTitle, title):
        super().__init__(parent)

        self.mandatoryFields = []

        self.setWindowTitle(QCoreApplication.translate("Dialog", windowTitle))
        self.setWindowIcon(QIcon(":Images/MiCreate48x48.png"))
        self.resize(500, 300)
        self.setMinimumSize(QSize(500, 300))
        self.setMaximumSize(QSize(500, 300))

        self.widgetLayout = QVBoxLayout(self)
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setContentsMargins(9,0,4,4)

        self.title = QLabel(self)
        self.title.setText(QCoreApplication.translate("Dialog", title))
        self.title.setStyleSheet("QLabel { font-size: 18pt;}")
        
        self.widgetLayout.addWidget(self.title)
        self.setLayout(self.widgetLayout)

    def loadLanguage(self, language):
        translation = gettext.translation('properties', localedir='locales', languages=[language])
        translation.install()
        global _
        _ = translation.gettext

    def clearWidgets(self):
        for i in reversed(range(self.widgetLayout.count())): 
            self.widgetLayout.itemAt(i).widget().setParent(None)

    def clearMandatoryFields(self):
        self.mandatoryFields.clear()         

    def addTextField(self, titleText, defaultText="", placeholderText="", mandatory=False):
        title = QLabel(QCoreApplication.translate("Dialog", titleText), self)
        field = QLineEdit(defaultText, self)
        field.setFixedWidth(175)
        field.setPlaceholderText(placeholderText)

        if mandatory:
            self.mandatoryFields.append(field)

        self.widgetLayout.addWidget(title)
        self.widgetLayout.addWidget(field)

        return field
    
    def addFolderField(self, titleText, defaultText="", placeholderText="", mandatory=False):
        def openFolderDialog():
            location = QFileDialog.getExistingDirectory(self)
            field.setText(str(location))

        title = QLabel(QCoreApplication.translate("Dialog", titleText), self)
        field = QLineEdit(defaultText, self)
        field.setFixedWidth(175)
        field.setPlaceholderText(placeholderText)
        folderButton = QToolButton(self)
        folderButton.setObjectName("inputField-button")
        folderButton.setText("")
        foldericon = QIcon().fromTheme("document-open")
        folderButton.setIcon(foldericon)
        folderButton.clicked.connect(openFolderDialog)
        
        if mandatory:
            self.mandatoryFields.append(field)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.setSpacing(4)
        horizontalLayout.addWidget(field)
        horizontalLayout.addWidget(folderButton)
        horizontalLayout.addStretch()
        self.widgetLayout.addWidget(title)
        self.widgetLayout.addLayout(horizontalLayout)

        return field

    def addFileField(self, titleText, defaultText="", placeholderText="", mandatory=False):
        def openFileDialog():
            location = QFileDialog.getOpenFileName(self)
            field.setText(str(location[0]))

        title = QLabel(QCoreApplication.translate("Dialog", titleText), self)
        field = QLineEdit(defaultText, self)
        field.setFixedWidth(175)
        field.setPlaceholderText(placeholderText)
        folderButton = QToolButton(self)
        folderButton.setText("")
        folderButton.setFixedSize(22, 22)
        foldericon = QIcon().fromTheme("document-open")
        folderButton.setIcon(foldericon)
        folderButton.clicked.connect(openFileDialog)
        
        if mandatory:
            self.mandatoryFields.append(field)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.setSpacing(0)
        horizontalLayout.addWidget(field)
        horizontalLayout.addWidget(folderButton)
        horizontalLayout.addStretch()
        self.widgetLayout.addWidget(title)
        self.widgetLayout.addLayout(horizontalLayout)

        return field

    def addDropdown(self, titleText, itemList, defaultItem=None, textEditable=False):
        title = QLabel(QCoreApplication.translate("Dialog", titleText), self)
        field = QComboBox(self)
        field.addItems(itemList)
        if defaultItem:
            field.setCurrentIndex(itemList.index(defaultItem))
        field.setFixedWidth(175)
        field.setEditable(textEditable)

        self.widgetLayout.addWidget(title)
        self.widgetLayout.addWidget(field)

        return field
    
    def addButtonBox(self, defaultButtons):
        def update():
            for item in self.mandatoryFields:
                if item.text() == "":
                    buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
                    return
            buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

        buttonBox = QDialogButtonBox(defaultButtons, self)

        self.widgetLayout.addStretch()
        self.widgetLayout.addWidget(buttonBox)

        for item in self.mandatoryFields:
            item.textChanged.connect(update)

        update()

        return buttonBox