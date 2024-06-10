# Dialog Manager
# tostr 2024
import sys
import gettext
import threading
from pathlib import Path
from playsound import playsound

sys.path.append("..")

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QComboBox, QToolButton, QSpinBox, QVBoxLayout, 
                             QHBoxLayout, QSizePolicy, QWidget, QDialogButtonBox, QFileDialog, QFrame,
                             QPushButton, QListWidget, QListWidgetItem)
from widgets.stackedWidget import QStackedWidget, loadJsonStyle

from translate import QCoreApplication

class CoreDialog(QDialog):
    # Core dialog contains welcome screen, new project screen and compile project screen
    reloadSettings = pyqtSignal()
    saveSettings = pyqtSignal()
    def __init__(self, parent, settingsWidget, versionString, deviceList):
        super().__init__(parent)

        self.setWindowTitle(QCoreApplication.translate("", "Welcome"))
        self.setWindowIcon(QIcon(":Images/MiCreate48x48.png"))      

        self.resize(750, 500)
        self.setMinimumSize(QSize(750, 500))  

        self.dialogLayout = QHBoxLayout(self)
        self.dialogLayout.setContentsMargins(0,0,0,0)
        self.dialogLayout.setSpacing(0)

        self.sidebar = QStackedWidget(self)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setContentsMargins(9,9,9,9)
        self.sidebar.setFixedWidth(200)

        self.contentPanel = QStackedWidget(self)
        self.contentPanel.setObjectName("contentPanel")
        self.contentPanel.setContentsMargins(0,0,0,0)

        loadJsonStyle(self)

        self.dialogLayout.addWidget(self.sidebar, 0)
        self.dialogLayout.addWidget(self.contentPanel, 1)

        self.setupWelcomePage(versionString)
        self.setupNewProjectPage(deviceList)
        self.setupSettingsPage(settingsWidget)

    def translate(self):
        self.welcomeSidebarNewProject.setText(QCoreApplication.translate("", "New Project"))
        self.welcomeSidebarOpenProject.setText(QCoreApplication.translate("", "Open Project"))
        self.newProjectSidebarTitle.setText(QCoreApplication.translate("", "New Project"))
        self.welcomeSidebarSettings.setText(QCoreApplication.translate("", "Settings"))
        self.watchfaceCategory.setText(QCoreApplication.translate("", "Watchface"))
        self.settingsSidebarTitle.setText(QCoreApplication.translate("", "Settings"))
        self.newProjectWatchfacePageDeviceTitle.setText(QCoreApplication.translate("", "Select device"))
        self.newProjectWatchfacePageProjectTitle.setText(QCoreApplication.translate("", "Project name"))
        self.newProjectWatchfacePageDirectoryTitle.setText(QCoreApplication.translate("", "Project location"))

    def setupWelcomePage(self, versionString):
        # sidebar

        self.hertaGif = QMovie("data/herta/herta.gif")
        self.hertaGif.frameChanged.connect(lambda: self.welcomeSidebarLogo.setIcon(QIcon(self.hertaGif.currentPixmap())))

        def playHerta():
            playsound("data/herta/herta.mp3", block=False)
            self.welcomeSidebarLogo.setIconSize(QSize(100, 100))
            self.hertaGif.start()
            
        self.welcomeSidebar = QFrame(self.sidebar)
        self.welcomeSidebarLayout = QVBoxLayout(self.welcomeSidebar)
        self.welcomeSidebarLayout.setContentsMargins(0,0,0,0)
        self.welcomeSidebarLogo = QPushButton(self.welcomeSidebar)
        self.welcomeSidebarLogo.setIcon(QIcon(":/Images/MiCreate48x48.png"))
        self.welcomeSidebarLogo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self.welcomeSidebarLogo.setIconSize(QSize(48, 48))
        self.welcomeSidebarLogo.setDefault(False)
        self.welcomeSidebarLogo.setAutoDefault(False)
        self.welcomeSidebarLogo.setFlat(True)
        self.welcomeSidebarLogo.pressed.connect(playHerta)

        self.welcomeSidebarAppName = QLabel(self.welcomeSidebar)
        self.welcomeSidebarAppName.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self.welcomeSidebarAppName.setText("Mi Create")
        self.welcomeSidebarAppName.setStyleSheet("font-size: 14pt")
        self.welcomeSidebarAppName.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.welcomeSidebarVersion = QLabel(self.welcomeSidebar)
        self.welcomeSidebarVersion.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self.welcomeSidebarVersion.setText(versionString)
        self.welcomeSidebarVersion.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.welcomeSidebarLine = QFrame(self.welcomeSidebar)
        self.welcomeSidebarLine.setFrameShape(QFrame.Shape.HLine)
        self.welcomeSidebarLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.welcomeSidebarNewProject = QPushButton(self.welcomeSidebar)
        self.welcomeSidebarNewProject.setIcon(QIcon().fromTheme("document-new"))

        self.welcomeSidebarOpenProject = QPushButton(self.welcomeSidebar)
        self.welcomeSidebarOpenProject.setIcon(QIcon().fromTheme("document-open"))

        self.welcomeSidebarSettings = QToolButton(self.welcomeSidebar)
        self.welcomeSidebarSettings.setIcon(QIcon().fromTheme("preferences-desktop"))

        self.welcomeSidebarLayout.addStretch()
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarLogo)
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarAppName)
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarVersion)
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarLine)
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarNewProject)
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarOpenProject)
        self.welcomeSidebarLayout.addStretch()
        self.welcomeSidebarLayout.addWidget(self.welcomeSidebarSettings)

        self.welcomeSidebar.setLayout(self.welcomeSidebarLayout)

        # contentsPanel

        self.welcomePage = QListWidget()
        self.welcomePage.setStyleSheet("background-color: transparent;")
        self.welcomePage.setObjectName("contentPanel")

        # add to main layout

        self.sidebar.addWidget(self.welcomeSidebar)
        self.contentPanel.addWidget(self.welcomePage)

        # setup interactive things
        self.welcomeSidebarNewProject.clicked.connect(lambda: self.showNewProjectPage(self.showWelcomePage))
        self.welcomeSidebarSettings.clicked.connect(lambda: self.showSettingsPage(self.showWelcomePage))

    def setupNewProjectPage(self, deviceList):
        # sidebar

        self.newProjectSidebar = QFrame()
        self.newProjectSidebarLayout = QVBoxLayout()
        self.newProjectSidebarLayout.setContentsMargins(0,0,0,0)

        self.newProjectSidebarHeader = QHBoxLayout()
        self.newProjectSidebarBack = QToolButton(self)
        self.newProjectSidebarBack.setIcon(QIcon().fromTheme("application-back"))
        self.newProjectSidebarTitle = QLabel(self)
        self.newProjectSidebarTitle.setStyleSheet("font-size: 12pt")
        self.newProjectSidebarHeader.addWidget(self.newProjectSidebarBack, 0)
        self.newProjectSidebarHeader.addWidget(self.newProjectSidebarTitle, 1)

        self.newProjectSidebarList = QListWidget()
        self.newProjectSidebarList.setFrameShape(QFrame.Shape.NoFrame)
        self.watchfaceCategory = QListWidgetItem(self.newProjectSidebarList)
        self.watchfaceCategory.setSizeHint(QSize(25, 35))
        self.watchfaceCategory.setIcon(QIcon().fromTheme("device-watch"))
        
        self.newProjectSidebarLayout.addLayout(self.newProjectSidebarHeader, 0)
        self.newProjectSidebarLayout.addWidget(self.newProjectSidebarList, 1)

        self.newProjectSidebar.setLayout(self.newProjectSidebarLayout)

        # contents

        def update():
            # update and check if all fields are filled
            if self.newProjectWatchfacePageProjectField.text() != "" and self.newProjectWatchfacePageDirectoryField.text() != "":
                self.newProjectWatchfacePageButtonBox.setEnabled(True)
            else:
                self.newProjectWatchfacePageButtonBox.setEnabled(False)

        def openFolderDialog():
            location = QFileDialog.getExistingDirectory(self)
            self.newProjectWatchfacePageDirectoryField.setText(str(location))

        self.newProjectPage = QStackedWidget(self)
        self.newProjectPage.setObjectName("contentPanel")

        self.newProjectWatchfacePage = QFrame()
        self.newProjectWatchfacePage.setStyleSheet("background-color: transparent;")
        self.newProjectWatchfacePage.setContentsMargins(9,6,9,9)
        self.newProjectWatchfacePageLayout = QVBoxLayout()
        self.newProjectWatchfacePageLayout.setSpacing(4)
        self.newProjectWatchfacePageLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # device selection

        self.newProjectWatchfacePageDeviceLayout = QHBoxLayout()

        self.newProjectWatchfacePageDeviceTitle = QLabel(self)
        self.newProjectWatchfacePageDeviceField = QComboBox(self)
        self.newProjectWatchfacePageDeviceField.addItems(deviceList)
        self.newProjectWatchfacePageDeviceField.setFixedWidth(175)

        self.newProjectWatchfacePageDeviceLayout.addWidget(self.newProjectWatchfacePageDeviceTitle)
        self.newProjectWatchfacePageDeviceLayout.addWidget(self.newProjectWatchfacePageDeviceField)

        # device name input

        self.newProjectWatchfacePageProjectLayout = QHBoxLayout()

        self.newProjectWatchfacePageProjectTitle = QLabel(self)
        self.newProjectWatchfacePageProjectField = QLineEdit(self)
        self.newProjectWatchfacePageProjectField.setFixedWidth(175)
        self.newProjectWatchfacePageProjectField.textChanged.connect(update)

        self.newProjectWatchfacePageProjectLayout.addWidget(self.newProjectWatchfacePageProjectTitle)
        self.newProjectWatchfacePageProjectLayout.addWidget(self.newProjectWatchfacePageProjectField)

        # directory selection

        self.newProjectWatchfacePageDirectoryLayout = QHBoxLayout()

        self.newProjectWatchfacePageDirectoryTitle = QLabel(self)
        self.newProjectWatchfacePageDirectoryField = QLineEdit(self.newProjectWatchfacePage)
        self.newProjectWatchfacePageDirectoryField.setFixedWidth(300)
        self.newProjectWatchfacePageDirectoryField.textChanged.connect(update)
        self.newProjectWatchfacePageDirectoryFolderButton = QToolButton(self)
        self.newProjectWatchfacePageDirectoryFolderButton.setObjectName("inputField-button")
        self.newProjectWatchfacePageDirectoryFolderButton.setText("")
        self.newProjectWatchfacePageDirectoryFolderButton.setIcon(QIcon().fromTheme("document-open"))
        self.newProjectWatchfacePageDirectoryFolderButton.clicked.connect(openFolderDialog)

        self.newProjectWatchfacePageDirectoryLayout.addWidget(self.newProjectWatchfacePageDirectoryTitle)
        self.newProjectWatchfacePageDirectoryLayout.addWidget(self.newProjectWatchfacePageDirectoryField)
        self.newProjectWatchfacePageDirectoryLayout.addWidget(self.newProjectWatchfacePageDirectoryFolderButton)

        self.newProjectWatchfacePageButtonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)

        # layout
        
        self.newProjectWatchfacePageLayout.addLayout(self.newProjectWatchfacePageDeviceLayout)
        self.newProjectWatchfacePageLayout.addLayout(self.newProjectWatchfacePageProjectLayout)
        self.newProjectWatchfacePageLayout.addLayout(self.newProjectWatchfacePageDirectoryLayout)
        self.newProjectWatchfacePageLayout.addLayout(self.newProjectWatchfacePageDeviceLayout)
        self.newProjectWatchfacePageLayout.addStretch()
        self.newProjectWatchfacePageLayout.addWidget(self.newProjectWatchfacePageButtonBox)

        self.newProjectWatchfacePage.setLayout(self.newProjectWatchfacePageLayout)

        self.newProjectPage.addWidget(self.newProjectWatchfacePage)

        # add to main layout
        
        self.sidebar.addWidget(self.newProjectSidebar)
        self.contentPanel.addWidget(self.newProjectPage)

        update()

    def setupSettingsPage(self, settingsWidget):
        self.settingsSidebar = QFrame()
        self.settingsSidebarLayout = QVBoxLayout()
        self.settingsSidebarLayout.setContentsMargins(0,0,0,0)

        self.settingsSidebarHeader = QHBoxLayout()
        self.settingsSidebarBack = QToolButton(self)
        self.settingsSidebarBack.setIcon(QIcon().fromTheme("application-back"))
        self.settingsSidebarTitle = QLabel(self)
        self.settingsSidebarTitle.setStyleSheet("font-size: 12pt")
        self.settingsSidebarHeader.addWidget(self.settingsSidebarBack, 0)
        self.settingsSidebarHeader.addWidget(self.settingsSidebarTitle, 1)

        self.settingsPage = settingsWidget
        settingsWidget.setStyleSheet("background-color: transparent;")

        self.settingsSidebarLayout.addLayout(self.settingsSidebarHeader, 0)
        self.settingsSidebarLayout.addStretch()

        self.settingsSidebar.setLayout(self.settingsSidebarLayout)

        self.sidebar.addWidget(self.settingsSidebar)
        self.contentPanel.addWidget(self.settingsPage)

    def showWelcomePage(self):
        self.setWindowTitle(QCoreApplication.translate("", "Welcome"))
        self.sidebar.setCurrentWidget(self.welcomeSidebar)
        self.contentPanel.setCurrentWidget(self.welcomePage)

        self.hertaGif.stop()
        self.welcomeSidebarLogo.setIcon(QIcon(":/Images/MiCreate48x48.png"))
        self.welcomeSidebarLogo.setIconSize(QSize(48, 48))

    def showNewProjectPage(self, prevPageFunc=None):
        self.setWindowTitle(QCoreApplication.translate("", "New Project"))
        self.sidebar.setCurrentWidget(self.newProjectSidebar)
        self.contentPanel.setCurrentWidget(self.newProjectPage)
        self.newProjectSidebarList.setCurrentRow(0)

        if prevPageFunc:
            self.newProjectSidebarBack.setVisible(True)
            self.newProjectSidebarBack.clicked.connect(prevPageFunc)
        else:
            self.newProjectSidebarBack.setVisible(False)

    def showSettingsPage(self, prevPageFunc=None):
        self.setWindowTitle(QCoreApplication.translate("", "Settings"))
        self.reloadSettings.emit()
        self.sidebar.setCurrentWidget(self.settingsSidebar)
        self.contentPanel.setCurrentWidget(self.settingsPage)

        if prevPageFunc:
            self.settingsSidebarBack.setVisible(True)
            self.settingsSidebarBack.clicked.connect(prevPageFunc)
        else:
            self.settingsSidebarBack.setVisible(False)

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