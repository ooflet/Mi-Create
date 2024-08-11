# Dialog Manager
# ooflet <ooflet@proton.me>

# Provides the CoreDialog class responsible for pretty much everything 
# Convenience Multi-Field dialog class for creating quick nice looking dialogs with multiple fields

import os
import sys
import gettext
import threading
from pathlib import Path

sys.path.append("..")

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QComboBox, QToolButton, QSpinBox, QVBoxLayout, 
                             QHBoxLayout, QSizePolicy, QWidget, QDialogButtonBox, QFileDialog, QFrame,
                             QPushButton, QCheckBox, QListWidget, QListWidgetItem, QMenu)
from PyQt6.QtMultimedia import QSoundEffect
from widgets.stackedWidget import QStackedWidget, loadJsonStyle

from translate import QCoreApplication

class CoreDialog(QDialog):
    # Core dialog contains welcome screen, new project screen and compile project screen
    reloadSettings = pyqtSignal()
    saveSettings = pyqtSignal()
    updateCompiler = pyqtSignal(str, str)
    resetSettings = pyqtSignal()

    def __init__(self, parent, settingsWidget, versionString, deviceList):
        super().__init__(parent)

        self.dialogButtonCallback = None

        self.setWindowTitle(QCoreApplication.translate("", "Welcome"))
        self.setWindowIcon(QIcon(":Images/MiCreate48x48.png"))      

        self.resize(750, 500)
        self.setMinimumSize(QSize(750, 500))  

        self.dialogLayout = QHBoxLayout(self)
        self.dialogLayout.setContentsMargins(0,0,0,0)
        self.dialogLayout.setSpacing(0)

        self.contentLayout = QVBoxLayout()
        self.contentLayout.setContentsMargins(0,0,0,0)
        self.contentLayout.setSpacing(0)

        self.sidebar = QStackedWidget(self)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setContentsMargins(9,9,9,9)
        self.sidebar.setFixedWidth(200)

        self.contentPanel = QStackedWidget(self)
        self.contentPanel.setObjectName("contentPanel")
        self.contentPanel.setContentsMargins(0,0,0,0)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setHidden(True)
        self.buttonBox.setEnabled(False)
        self.buttonBox.setContentsMargins(12,12,12,12)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        loadJsonStyle(self)

        self.dialogLayout.addWidget(self.sidebar, 0)
        self.contentLayout.addWidget(self.contentPanel, 1)
        self.contentLayout.addWidget(self.buttonBox)
        self.dialogLayout.addLayout(self.contentLayout)

        self.setupWelcomePage(versionString)
        self.setupNewProjectPage(deviceList)
        self.setupManageProjectPage()
        self.setupSettingsPage(settingsWidget)

    def translate(self):
        self.welcomeSidebarNewProject.setText(QCoreApplication.translate("", "New Project"))
        self.welcomeSidebarOpenProject.setText(QCoreApplication.translate("", "Open Project"))
        self.newProjectSidebarTitle.setText(QCoreApplication.translate("", "New Project"))
        self.welcomeSidebarSettings.setText(QCoreApplication.translate("", "Settings"))
        self.watchfaceCategory.setText(QCoreApplication.translate("", "Watchface"))
        self.manageProjectSidebarTitle.setText(QCoreApplication.translate("", "Manage Project"))
        self.configureProjectCategory.setText(QCoreApplication.translate("", "Configure"))
        self.configurePageNameTitle.setText(QCoreApplication.translate("", "Watchface name"))
        self.configurePagePreviewText.setText(QCoreApplication.translate("", "Watchface thumbnail"))
        self.settingsSidebarTitle.setText(QCoreApplication.translate("", "Settings"))
        self.watchfacePageDeviceTitle.setText(QCoreApplication.translate("", "Select device"))
        self.watchfacePageProjectTitle.setText(QCoreApplication.translate("", "Project name"))
        self.watchfacePageDirectoryTitle.setText(QCoreApplication.translate("", "Project location"))

    def showButtonBox(self):
        self.buttonBox.setHidden(False)
        self.buttonBox.setEnabled(True)

    def hideButtonBox(self):
        self.buttonBox.setHidden(True)
        self.buttonBox.setEnabled(False)

    def setupWelcomePage(self, versionString):
        # sidebar

        self.hertaGif = QMovie(":/Herta/herta.gif")
        self.hertaGif.frameChanged.connect(lambda: self.welcomeSidebarLogo.setIcon(QIcon(self.hertaGif.currentPixmap())))
        hertaSound = QSoundEffect()
        hertaSound.setSource(QUrl("qrc:/Herta/herta.wav"))
        
        def playHerta():
            # kuru kuru~
            self.welcomeSidebarLogo.setIconSize(QSize(100, 100))
            self.hertaGif.start()
            hertaSound.play()
            
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
        self.welcomeSidebarAppName.setStyleSheet("font-size: 16pt")
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
        self.welcomeSidebarNewProject.clicked.connect(lambda: self.showNewProjectPage(self.showWelcomePage, True))
        self.welcomeSidebarSettings.clicked.connect(lambda: self.showSettingsPage(self.showWelcomePage, True))

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
        self.newProjectSidebarTitle.setFixedHeight(26)
        self.newProjectSidebarHeader.addWidget(self.newProjectSidebarBack, 0)
        self.newProjectSidebarHeader.addWidget(self.newProjectSidebarTitle, 1)

        self.newProjectSidebarHeaderLine = QFrame(self.welcomeSidebar)
        self.newProjectSidebarHeaderLine.setFrameShape(QFrame.Shape.HLine)
        self.newProjectSidebarHeaderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.newProjectSidebarList = QListWidget()
        self.newProjectSidebarList.setFrameShape(QFrame.Shape.NoFrame)
        self.watchfaceCategory = QListWidgetItem(self.newProjectSidebarList)
        self.watchfaceCategory.setSizeHint(QSize(25, 35))
        self.watchfaceCategory.setIcon(QIcon().fromTheme("device-watch"))
        
        self.newProjectSidebarLayout.addLayout(self.newProjectSidebarHeader, 0)
        self.newProjectSidebarLayout.addWidget(self.newProjectSidebarHeaderLine, 0)
        self.newProjectSidebarLayout.addWidget(self.newProjectSidebarList, 1)

        self.newProjectSidebar.setLayout(self.newProjectSidebarLayout)

        # contents

        def update():
            # update and check if all fields are filled
            if self.watchfacePageProjectField.text() != "" and self.watchfacePageDirectoryField.text() != "":
                self.watchfacePageButtonBox.setEnabled(True)
            else:
                self.watchfacePageButtonBox.setEnabled(False)

        def openFolderDialog():
            location = QFileDialog.getExistingDirectory(self)
            self.watchfacePageDirectoryField.setText(str(location))

        self.newProjectPage = QStackedWidget(self)
        self.newProjectPage.setObjectName("contentPanel")

        self.watchfacePage = QFrame()
        self.watchfacePage.setStyleSheet("background-color: transparent;")
        self.watchfacePage.setContentsMargins(9,6,9,9)
        self.watchfacePageLayout = QVBoxLayout()
        self.watchfacePageLayout.setSpacing(4)
        self.watchfacePageLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # device selection

        self.watchfacePageDeviceLayout = QHBoxLayout()

        self.watchfacePageDeviceTitle = QLabel(self)
        self.watchfacePageDeviceField = QComboBox(self)
        self.watchfacePageDeviceField.addItems(deviceList)
        self.watchfacePageDeviceField.setFixedWidth(175)

        self.watchfacePageDeviceLayout.addWidget(self.watchfacePageDeviceTitle)
        self.watchfacePageDeviceLayout.addWidget(self.watchfacePageDeviceField)

        # device name input

        self.watchfacePageProjectLayout = QHBoxLayout()

        self.watchfacePageProjectTitle = QLabel(self)
        self.watchfacePageProjectField = QLineEdit(self)
        self.watchfacePageProjectField.setFixedWidth(175)
        self.watchfacePageProjectField.textChanged.connect(update)

        self.watchfacePageProjectLayout.addWidget(self.watchfacePageProjectTitle)
        self.watchfacePageProjectLayout.addWidget(self.watchfacePageProjectField)

        # directory selection

        self.watchfacePageDirectoryLayout = QHBoxLayout()

        self.watchfacePageDirectoryTitle = QLabel(self)
        self.watchfacePageDirectoryField = QLineEdit(self.watchfacePage)
        self.watchfacePageDirectoryField.setFixedWidth(300)
        self.watchfacePageDirectoryField.textChanged.connect(update)
        self.watchfacePageDirectoryFolderButton = QToolButton(self)
        self.watchfacePageDirectoryFolderButton.setObjectName("inputField-button")
        self.watchfacePageDirectoryFolderButton.setText("")
        self.watchfacePageDirectoryFolderButton.setIcon(QIcon().fromTheme("document-open"))
        self.watchfacePageDirectoryFolderButton.clicked.connect(openFolderDialog)

        self.watchfacePageDirectoryLayout.addWidget(self.watchfacePageDirectoryTitle)
        self.watchfacePageDirectoryLayout.addWidget(self.watchfacePageDirectoryField)
        self.watchfacePageDirectoryLayout.addWidget(self.watchfacePageDirectoryFolderButton)

        self.watchfacePageButtonBox = QDialogButtonBox()
        self.watchfacePageButtonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        # layout
        
        self.watchfacePageLayout.addLayout(self.watchfacePageDeviceLayout)
        self.watchfacePageLayout.addLayout(self.watchfacePageProjectLayout)
        self.watchfacePageLayout.addLayout(self.watchfacePageDirectoryLayout)
        self.watchfacePageLayout.addStretch()
        self.watchfacePageLayout.addWidget(self.watchfacePageButtonBox)

        self.watchfacePage.setLayout(self.watchfacePageLayout)

        self.newProjectPage.addWidget(self.watchfacePage)

        # add to main layout
        
        self.sidebar.addWidget(self.newProjectSidebar)
        self.contentPanel.addWidget(self.newProjectPage)

        update()

    def setupManageProjectPage(self):
        # sidebar

        self.manageProjectSidebar = QFrame()
        self.manageProjectSidebarLayout = QVBoxLayout()
        self.manageProjectSidebarLayout.setContentsMargins(0,0,0,0)

        self.manageProjectSidebarHeader = QHBoxLayout()
        self.manageProjectSidebarBack = QToolButton(self)
        self.manageProjectSidebarBack.setIcon(QIcon().fromTheme("application-back"))
        self.manageProjectSidebarSave = QToolButton(self)
        self.manageProjectSidebarSave.setIcon(QIcon().fromTheme("document-save"))
        self.manageProjectSidebarTitle = QLabel(self)
        self.manageProjectSidebarTitle.setStyleSheet("font-size: 12pt")
        self.manageProjectSidebarTitle.setFixedHeight(26)
        self.manageProjectSidebarHeader.addWidget(self.manageProjectSidebarBack, 0)
        self.manageProjectSidebarHeader.addWidget(self.manageProjectSidebarTitle, 1)
        self.manageProjectSidebarHeader.addWidget(self.manageProjectSidebarSave, 0)

        self.manageProjectSidebarHeaderLine = QFrame(self.welcomeSidebar)
        self.manageProjectSidebarHeaderLine.setFrameShape(QFrame.Shape.HLine)
        self.manageProjectSidebarHeaderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.manageProjectSidebarList = QListWidget()
        self.manageProjectSidebarList.setFrameShape(QFrame.Shape.NoFrame)
        self.configureProjectCategory = QListWidgetItem(self.manageProjectSidebarList)
        self.configureProjectCategory.setSizeHint(QSize(25, 35))
        self.configureProjectCategory.setIcon(QIcon().fromTheme("device-watch"))

        self.manageProjectSidebarLayout.addLayout(self.manageProjectSidebarHeader, 0)
        self.manageProjectSidebarLayout.addWidget(self.manageProjectSidebarHeaderLine, 0)
        self.manageProjectSidebarLayout.addWidget(self.manageProjectSidebarList, 1)
        self.manageProjectSidebar.setLayout(self.manageProjectSidebarLayout)

        # content

        self.manageProjectPage = QStackedWidget(self)
        self.manageProjectPage.setObjectName("contentPanel")

        self.configurePage = QFrame(self)
        self.configurePage.setContentsMargins(9,6,9,9)
        self.configurePageLayout = QVBoxLayout(self.configurePage)

        self.configurePageName = QHBoxLayout()
        self.configurePageNameTitle = QLabel()
        
        self.configurePageNameField = QLineEdit()
        self.configurePageNameField.setFixedWidth(175)
    
        self.configurePagePreview = QHBoxLayout()

        self.configurePagePreviewText = QLabel()
        
        self.configurePagePreviewField = QComboBox()
        self.configurePagePreviewField.setEditable(True)
        self.configurePagePreviewField.setFixedWidth(175)
        
        #self.configurePageAutoThumbnail = QCheckBox("Auto-generate watchface preview")

        self.configurePageName.addWidget(self.configurePageNameTitle)
        self.configurePageName.addWidget(self.configurePageNameField)

        self.configurePagePreview.addWidget(self.configurePagePreviewText)
        self.configurePagePreview.addWidget(self.configurePagePreviewField)

        self.configurePageLayout.addLayout(self.configurePageName)
        self.configurePageLayout.addLayout(self.configurePagePreview)
        self.configurePageLayout.addStretch()
        self.configurePage.setLayout(self.configurePageLayout)

        self.manageProjectPage.addWidget(self.configurePage)

        # layout

        self.sidebar.addWidget(self.manageProjectSidebar)
        self.contentPanel.addWidget(self.manageProjectPage)

    def setupSettingsPage(self, settingsWidget):
        self.settingsSidebar = QFrame()
        self.settingsSidebarLayout = QVBoxLayout()
        self.settingsSidebarLayout.setContentsMargins(0,0,0,0)

        self.settingsMenu = QMenu()
        updateAction = self.settingsMenu.addAction("Update Compiler from EasyFace")
        resetAction = self.settingsMenu.addAction("Reset Settings")

        def update():
            folder = QFileDialog.getExistingDirectory(self)
            print(folder)
            if folder:
                self.updateCompiler.emit(os.path.join(folder, "Compiler.exe"), os.path.join(folder, "DeviceInfo.db"))

        updateAction.triggered.connect(update)
        resetAction.triggered.connect(self.resetSettings.emit)

        self.settingsSidebarHeader = QHBoxLayout()
        self.settingsSidebarBack = QToolButton(self)
        self.settingsSidebarBack.setIcon(QIcon().fromTheme("application-back"))
        self.settingsSidebarMore = QToolButton(self)
        self.settingsSidebarMore.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        self.settingsSidebarMore.setIcon(QIcon().fromTheme("application-more"))
        self.settingsSidebarMore.setMenu(self.settingsMenu)
        self.settingsSidebarMore.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.settingsSidebarTitle = QLabel(self)
        self.settingsSidebarTitle.setStyleSheet("font-size: 12pt")
        self.settingsSidebarTitle.setFixedHeight(26)
        self.settingsSidebarHeader.addWidget(self.settingsSidebarBack, 0)
        self.settingsSidebarHeader.addWidget(self.settingsSidebarTitle, 1)
        self.settingsSidebarHeader.addWidget(self.settingsSidebarMore, 0)

        self.settingsSidebarHeaderLine = QFrame(self.welcomeSidebar)
        self.settingsSidebarHeaderLine.setFrameShape(QFrame.Shape.HLine)
        self.settingsSidebarHeaderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.settingsPage = settingsWidget
        settingsWidget.setStyleSheet("background-color: transparent;")

        self.settingsSidebarLayout.addLayout(self.settingsSidebarHeader, 0)
        self.settingsSidebarLayout.addWidget(self.settingsSidebarHeaderLine, 0)
        self.settingsSidebarLayout.addStretch()

        self.settingsSidebar.setLayout(self.settingsSidebarLayout)

        self.sidebar.addWidget(self.settingsSidebar)
        self.contentPanel.addWidget(self.settingsPage)

    def showWelcomePage(self, animate=False):
        self.setWindowTitle(QCoreApplication.translate("", "Welcome"))
        self.hideButtonBox()

        self.sidebar.setSlideTransition(animate)
        self.sidebar.setCurrentWidget(self.welcomeSidebar)

        self.contentPanel.setCurrentWidget(self.welcomePage)

        self.hertaGif.stop()
        self.welcomeSidebarNewProject.setFocus()
        self.welcomeSidebarLogo.setIcon(QIcon(":/Images/MiCreate48x48.png"))
        self.welcomeSidebarLogo.setIconSize(QSize(48, 48))

    def showNewProjectPage(self, prevPageFunc=None, animate=False):
        self.setWindowTitle(QCoreApplication.translate("", "New Project"))
        self.hertaGif.stop()
        self.showButtonBox()

        self.sidebar.setSlideTransition(animate)
        self.sidebar.setCurrentWidget(self.newProjectSidebar)

        self.contentPanel.setCurrentWidget(self.newProjectPage)

        self.newProjectSidebarList.setCurrentRow(0)

        if prevPageFunc:
            self.newProjectSidebarBack.setVisible(True)
            self.newProjectSidebarBack.clicked.connect(lambda: prevPageFunc(animate=True))
        else:
            self.newProjectSidebarBack.setVisible(False)

    def showManageProjectPage(self, prevPageFunc=None, animate=False):
        self.setWindowTitle(QCoreApplication.translate("", "Manage Project"))
        self.showButtonBox()
        
        self.sidebar.setSlideTransition(animate)
        self.sidebar.setCurrentWidget(self.manageProjectSidebar)
        
        self.contentPanel.setCurrentWidget(self.manageProjectPage)

        self.manageProjectSidebarList.setCurrentRow(0)

        if prevPageFunc:
            self.manageProjectSidebarBack.setVisible(True)
            self.manageProjectSidebarBack.clicked.connect(lambda: prevPageFunc(animate=True))
        else:
            self.manageProjectSidebarBack.setVisible(False)

    def showSettingsPage(self, prevPageFunc=None, animate=False):
        self.setWindowTitle(QCoreApplication.translate("", "Settings"))
        self.hertaGif.stop()
        self.reloadSettings.emit()
        self.showButtonBox()

        self.sidebar.setSlideTransition(animate)
        self.sidebar.setCurrentWidget(self.settingsSidebar)
        
        self.contentPanel.setCurrentWidget(self.settingsPage)
        
        if prevPageFunc:
            self.settingsSidebarBack.setVisible(True)
            self.settingsSidebarBack.clicked.connect(lambda: prevPageFunc(animate=True))
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
        self.title.setStyleSheet("QLabel { font-size: 16pt;}")
        
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
        folderButton.setObjectName("inputField-button")
        folderButton.setText("")
        foldericon = QIcon().fromTheme("document-open")
        folderButton.setIcon(foldericon)
        folderButton.clicked.connect(openFileDialog)
        
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