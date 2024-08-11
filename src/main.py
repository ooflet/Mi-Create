# Mi Create
# ooflet <ooflet@proton.me>

# TODO
# Put documentation on code, its a wasteland out there
# In-line AOD editing (through a toggle)

import logging
import traceback
import os

os.chdir(os.path.dirname(
    os.path.realpath(__file__)))  # switch working directory to program location so that data files can be found

# check if compiled and if so, logs to a file
if "__compiled__" in globals():
    logging.basicConfig(level=logging.DEBUG, filemode="w", filename="data/app.log",
                        format="%(asctime)s %(module)s.py:%(lineno)d %(threadName)-10s %(levelname)s %(message)s")
else:
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(module)s.py:%(lineno)d %(threadName)-10s %(levelname)s %(message)s")
    
logging.info("-- Starting Mi Create --")
logging.info("Initializing modules")

import sys
import shutil
import argparse
import requests
import subprocess
import platform
import gettext

from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QApplication, QProgressBar,
                             QDialogButtonBox, QFileDialog, QWidget, QVBoxLayout,
                             QFrame, QColorDialog, QFontDialog, QLabel, QListWidgetItem,
                             QAbstractItemView, QSplashScreen, QDialog, QUndoView, QCheckBox, QHBoxLayout)
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QDrag, QImage, QPainter, QFontDatabase, QFont
from PyQt6.QtCore import Qt, QSettings, QSize, QUrl, pyqtSignal
from window import FramelessDialog

if platform.system() == "Windows":  # menubar does not display on linux
    # TODO: fix it
    from window import QMainWindow
else:
    from PyQt6.QtWidgets import QMainWindow

from pprint import pprint, pformat
import xml.dom.minidom
import configparser
import threading
import json
import traceback

from utils.project import WatchData, XiaomiProject, FprjProject, GMFProject
from utils.dialog import CoreDialog, MultiFieldDialog
from utils.theme import Theme
from utils.updater import Updater
from utils.history import History, CommandAddWidget, CommandDeleteWidget, CommandPasteWidget, CommandModifyWidgetLayer, \
    CommandModifyProperty, CommandModifyPosition
from widgets.canvas import Canvas, ObjectIcon
from widgets.explorer import Explorer
from widgets.properties import PropertiesWidget
from widgets.editor import Editor, XMLLexer
from translate import QCoreApplication

import resources.resources_rc  # resource import required because it sets up the icons

from window_ui import Ui_MainWindow

_ = gettext.gettext

programVersion = 'v1.1'

class MainWindow(QMainWindow):
    updateFound = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.fileChanged = False
        self.compiling = False
        self.clipboard = []
        self.stagedChanges = []
        self.resourceImages = []
        self.selectionDebounce = False

        # Setup projects (tabs)
        self.projects = {}

        # Setup Main Window
        logging.info("Initializing MainWindow")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if platform.system() == "Windows":
            self.titleBar.layout().insertWidget(0, self.ui.menubar, 0, Qt.AlignmentFlag.AlignLeft)
            self.titleBar.layout().insertStretch(1, 1)
            self.setMenuWidget(self.titleBar)

        # Setup WatchData
        logging.info("Initializing WatchData")
        self.WatchData = WatchData()

        logging.info("Initializing Application Widgets")
        self.setupWidgets()
        logging.info("Initializing Workspace")
        self.setupWorkspace()
        logging.info("Initializing Explorer")
        self.setupExplorer()

        # Setup Language

        self.languages = []
        self.languageNames = []

        config = configparser.ConfigParser()
        logging.info("Initializing Language Files")
        for file in os.listdir("locales"):
            languageDir = os.path.join("locales", file)
            if os.path.isdir(languageDir):
                logging.info("Language directory found: " + languageDir)
                config.read_file(open(os.path.join(languageDir, "CONFIG.ini"), encoding="utf8"))
                self.languages.append(
                    {
                        "languageName": config.get('config', 'language'),
                        "directory": languageDir,
                        "authorMessage": config.get('config', 'authorMessage'),
                        "authorContact": config.get('config', 'contact')
                    }
                )
                self.languageNames.append(config.get('config', 'language'))

        logging.info("Initializing Watch Properties")
        self.setupProperties()

        logging.info("Initializing Settings")
        self.settingsWidget = PropertiesWidget(self)

        self.setupThemes()
        self.loadSettings()
        self.loadTheme()

        self.settingsWidget.propertyChanged.connect(lambda property, value: self.setSetting(property, value))

        logging.info("Initializing Dialogs")
        self.setupDialogs()

        rawSettings = QSettings("Mi Create", "Settings")
        if "Language" not in rawSettings.allKeys():
            logging.info("No language selected")
            item, accepted = QInputDialog().getItem(None, "Mi Create", "Select Language", self.languageNames, 0, False)

            if item in self.languageNames:
                if accepted:
                    self.setSetting("Language", item)

        self.loadLanguage(True)
        self.settingsWidget.loadProperties(self.settings)

        # Setup History System
        self.History = History()
        self.ignoreHistoryInvoke = False

        # Undo History Dialog
        # self.undoLayout = QVBoxLayout()
        # self.undoDialog = QDialog(self)
        # self.undoView = QUndoView(self.History.undoStack)
        # self.undoLayout.addWidget(self.undoView)
        # self.undoDialog.setLayout(self.undoLayout)
        # self.undoDialog.show()

        # Setup Project
        self.project = None
        self.projectXML = None

        logging.info("Initializing Misc")
        self.loadWindowState()
        self.updateFound.connect(self.promptUpdate)
        logging.info("Launch!!")

    def closeEvent(self, event):
        logging.info("Exit requested!")

        def quitWindow():
            logging.info("-- Exiting Mi Create --")
            logging.info("Disconnecting selectionChanged event")
            for project in self.projects.values():
                if project.get("canvas"):
                    project["canvas"].scene().selectionChanged.disconnect()
            logging.info("Saving Window State")
            self.saveWindowState()
            logging.info("Quitting")
            event.accept()

        if self.fileChanged == True:
            quit_msg = _("You have unsaved project(s) open. Save and quit?")
            reply = self.showDialog("warning", quit_msg, "",
                                    QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.SaveAll:
                logging.info("Saving all unsaved projects")
                self.saveProjects("all")
                quitWindow()

            elif reply == QMessageBox.StandardButton.Discard:
                quitWindow()

            else:
                event.ignore()
        else:
            quitWindow()

    def showEvent(self, event):
        # update view actions
        if self.settings["General"]["CheckUpdate"]["value"] == True:
            threading.Thread(target=self.checkForUpdates).start()

    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def showWelcome(self):
        settings = QSettings("Mi Create", "Workspace")

        self.coreDialog.welcomePage.clear()

        if settings.value("recentProjects") != None:
            projectList = settings.value("recentProjects")
            projectList.reverse()
            for name, location in projectList:
                if os.path.isfile(location):
                    listWidget = QWidget()
                    textLayout = QVBoxLayout()
                    widgetLayout = QHBoxLayout()
                    projectName = QLabel()
                    projectLocation = QLabel()
                    projectIcon = QLabel()
                    icon = QIcon().fromTheme("project-icon")

                    projectName.setText(name)
                    projectLocation.setText(location)
                    projectLocation.setStyleSheet("color: palette(midlight)")
                    projectIcon.setPixmap(QPixmap(icon.pixmap(QSize(32, 32))))

                    textLayout.setSpacing(0)
                    textLayout.addWidget(projectName)
                    textLayout.addWidget(projectLocation)

                    widgetLayout.setSpacing(8)
                    widgetLayout.setContentsMargins(12, 8, 12, 8)
                    widgetLayout.addWidget(projectIcon, 0)
                    widgetLayout.addLayout(textLayout, 1)

                    listWidget.setLayout(widgetLayout)

                    # item
                    listItem = QListWidgetItem(self.coreDialog.welcomePage)
                    listItem.setToolTip(location)
                    listItem.setSizeHint(listWidget.sizeHint())
                    self.coreDialog.welcomePage.setItemWidget(listItem, listWidget)

        self.coreDialog.showWelcomePage()
        self.coreDialog.exec()

    def getCurrentProject(self) -> dict:
        # tab paths are stored in the tabToolTip string
        currentIndex = self.ui.workspace.currentIndex()
        currentProject = None
        if self.ui.workspace.tabToolTip(currentIndex) != "":
            currentProject = self.projects.get(self.ui.workspace.tabToolTip(currentIndex))
        else:
            currentProject = self.projects.get(self.ui.workspace.tabText(currentIndex))
        return currentProject

    def saveWindowState(self):
        settings = QSettings("Mi Create", "Workspace")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())

    def loadWindowState(self):
        settings = QSettings("Mi Create", "Workspace")

        if settings.value("geometry") == None or settings.value("state") == None:
            return

        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("state"))

    def setSetting(self, setting, value, loadSettings=True):
        logging.info(f"Set setting {setting} to {value}")
        settings = QSettings("Mi Create", "Settings")
        settings.setValue(setting, value)

        if loadSettings:
            self.loadSettings()
            if setting == "Theme":
                self.loadTheme()
            if setting == "Language":
                self.loadLanguage(True)
                self.settingsWidget.loadProperties(self.settings)

    def saveSettings(self, retranslate, loadSettings=True):
        settings = QSettings("Mi Create", "Settings")
        for property, value in self.stagedChanges:
            settings.setValue(property, value)

        if loadSettings:
            self.loadSettings()
            self.loadTheme()
        if retranslate:
            self.loadLanguage(True)

    def loadSettings(self):
        # settings are stored through QSettings, not the settingItems.json file
        # on windows its located at Computer\HKEY_CURRENT_USER\Software\Mi Create
        # on linux its located at /home/user/.config/Mi Create/
        savedSettings = QSettings("Mi Create", "Settings")
        with open("data/settingItems.json") as file:
            self.settings = json.load(file)
            logging.info("settingItems.json loaded")
            self.settings["General"]["Theme"]["options"] = self.themes.themeNames
            self.settings["General"]["Language"]["options"] = self.languageNames

        for key in savedSettings.allKeys():
            for category, properties in self.settings.items():
                for property, value in properties.items():
                    if key == property:
                        logging.info("Property load " + property)
                        # convert string to bool
                        if savedSettings.value(key) == "true":
                            value["value"] = True
                        elif savedSettings.value(key) == "false":
                            value["value"] = False
                        else:
                            value["value"] = savedSettings.value(key)

        for project in self.projects.values():
            if project.get("canvas"):
                project["canvas"].setRenderHint(QPainter.RenderHint.Antialiasing,
                                                self.settings["Canvas"]["Antialiasing"]["value"])
                project["canvas"].loadObjects(project["project"],
                                                self.settings["Canvas"]["Snap"]["value"],
                                                self.settings["Canvas"]["Interpolation"]["value"],
                                                self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                                self.settings["Canvas"]["ShowDeviceOutline"]["value"])

    def loadLanguage(self, retranslate):
        selectedLanguage = None
        for language in self.languages:
            if language["languageName"] == self.settings["General"]["Language"]["value"]:
                selectedLanguage = language
                break
        else:
            self.showDialog("warning",
                            f"An error occured while loading the language {self.settings['General']['Language']['value']}. Language settings have been reset.")
            self.setSetting("Language", "English")
            self.saveSettings(False, False)
            self.loadLanguage(True)

        if selectedLanguage != None:
            mainTranslation = gettext.translation('main', localedir='locales',
                                                  languages=[os.path.basename(selectedLanguage["directory"])])
            mainTranslation.install()
            global _  # fetch global translation variable (gettext)
            _ = mainTranslation.gettext
            QCoreApplication.loadLanguage(os.path.basename(selectedLanguage["directory"]))
            self.propertiesWidget.loadLanguage(os.path.basename(selectedLanguage["directory"]))
            self.ui.retranslateUi(self)  # function on each precompiled window/dialog
            self.coreDialog.translate()
            # retranslate relies on the translate.py module
            # the translate module reimplements CoreApplication's translate function to rely on gettext instead

    def launchUpdater(self):
        progressBar = QProgressBar()
        progressBar.setRange(0, 0)
        text = QLabel("Downloading Update...")
        self.statusBar().addPermanentWidget(text, 0)
        self.statusBar().addPermanentWidget(progressBar, 1)

        Updater(self.statusBar(), progressBar, text)

    def promptUpdate(self, ver):
        reply, dontCheck = self.showDialog("question",
                                           _('A new update has been found ({version}). Would you like to update now?').format(
                                               version=ver), "",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.Yes, "Never check for updates", False)

        if dontCheck:
            self.setSetting("CheckUpdate", False)

        if reply == QMessageBox.StandardButton.Yes:
            self.launchUpdater()

    def checkForUpdates(self):
        # Contacts GitHub server for current version and compares installed to current version
        try:
            #check for updated version
            response = requests.get("https://api.github.com/repos/ooflet/Mi-Create/releases/latest")
            release_info = response.json()
            version = release_info["tag_name"]
        except Exception as e:
            logging.warning(f"Update check resulted in an exception: {e}")
            return

        if version > programVersion:
            self.updateFound.emit(version)

    def setupThemes(self):
        self.themes = Theme()

    def loadTheme(self):
        # Loads theme from settings table
        themeName = self.settings["General"]["Theme"]["value"]
        app = QApplication.instance()

        if themeName == "Dark":
            themeName = "Default Dark"
            self.setSetting("Theme", "Default Dark")

        success = self.themes.loadTheme(app, themeName)
        if not success:
            if "Default Dark" not in self.themes.themeNames:
                self.showDialog("error", "Failed to load default theme. The system theme will be used.")
                return
            
            self.setSetting("Theme", "Default Dark")
            self.loadTheme()
            self.showDialog("warning",
                            f"An error occured while loading the theme {themeName}. Theme settings have been reset.")

    def reloadImages(self, imageFolder):
        self.ui.resourceList.clear()
        if imageFolder != None:
            self.resourceImages.clear()
            directory = os.listdir(imageFolder)
            directory.sort()
            for filename in directory:
                file = os.path.join(imageFolder, filename)
                if os.path.isfile(file):
                    logging.info("Creating file entry for " + os.path.basename(file))
                    item = QListWidgetItem(QIcon(file), os.path.basename(file))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setData(0, os.path.basename(file))
                    item.setSizeHint(QSize(14, 64))

                    self.resourceImages.append(os.path.basename(file))
                    self.ui.resourceList.addItem(item)

    def setIconState(self, disabled):
        self.ui.actionSave.setDisabled(disabled)
        self.ui.actionManage_Project.setDisabled(disabled)

        # edit
        self.ui.actionDelete.setDisabled(disabled)
        self.ui.actionCut.setDisabled(disabled)
        self.ui.actionCopy.setDisabled(disabled)
        self.ui.actionPaste.setDisabled(disabled)
        self.ui.actionUndo.setDisabled(disabled)
        self.ui.actionRedo.setDisabled(disabled)
        self.ui.actionBring_to_Front.setDisabled(disabled)
        self.ui.actionBring_Forwards.setDisabled(disabled)
        self.ui.actionSend_to_Back.setDisabled(disabled)
        self.ui.actionSend_Backwards.setDisabled(disabled)
        self.ui.actionProject_XML_File.setDisabled(disabled)

        # view
        self.ui.actionZoom_In.setDisabled(disabled)
        self.ui.actionZoom_Out.setDisabled(disabled)

        # compile
        self.ui.actionBuild.setDisabled(disabled)
        self.ui.actionUnpack.setDisabled(disabled)

    def openFolder(self, path):
        if platform.system() == "Windows":
            # windows not supporting forward slashes :skull:
            path = str.replace(path, "/", "\\")
            # uh oh ACE vulnerability?????
            os.startfile(path)
        elif platform.system() == "Darwin":
            # never buying a mac to port this hot garbage, but just keep it here
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def closeTab(self, index):
        print(index)

        # Fires when tab closes
        def delProjectItem(index):
            if self.ui.workspace.tabToolTip(index) != "":
                # tooltips are used to store the name of the project
                # usually the project location
                self.projects.pop(self.ui.workspace.tabToolTip(index))
            else:
                # the tab text name is used
                self.projects.pop(self.ui.workspace.tabText(index))

        project = self.ui.workspace.tabToolTip(index)

        if project == "":
            self.ui.workspace.widget(index).deleteLater()
            self.ui.workspace.removeTab(index)
            return

        if self.projects.get(project) and self.projects[project]["hasFileChanged"]:
            reply = self.showDialog("warning", "This tab has unsaved changes. Save and close?", "",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                    QMessageBox.StandardButton.Yes)

            if reply == QMessageBox.StandardButton.Yes:
                self.saveProjects("current")
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        if isinstance(self.ui.workspace.widget(index), Canvas):
            self.ui.workspace.widget(index).scene().selectionChanged.disconnect()

        delProjectItem(index)
        self.ui.workspace.removeTab(index)
        self.fileChanged = False

        if self.ui.workspace.count() == 0:
            self.setIconState(True)
            self.showWelcome()

    def setupWorkspace(self):
        def handleTabChange(index):
            # Fires when tab changes
            tabName = self.ui.workspace.tabText(index)
            currentProject = self.getCurrentProject()
            self.setWindowTitle(tabName + " - Mi Create")

            # Clear selection of all canvases
            for project in self.projects.values():
                if project.get("canvas"):
                    project["canvas"].clearSelected()

            self.updateProperties(False)
            if currentProject is None or tabName == "Project XML":
                self.setIconState(False)
                self.clearExplorer()
                self.reloadImages(None)
                return

            if currentProject.get("canvas") is not None:
                self.setIconState(False)
                self.selectionDebounce = False
                self.Explorer.updateExplorer(currentProject["project"])
                logging.info("Explorer updated")
                thread = threading.Thread(target=lambda: self.reloadImages(currentProject["project"].imageFolder))
                thread.start()
            else:
                self.setIconState(True)
                self.clearExplorer()
                self.reloadImages(None)

        # setup resourceList

        def startDrag(supportedActions):
            # hides the drag preview
            listsQModelIndex = self.ui.resourceList.selectedIndexes()
            if listsQModelIndex:
                dataQMimeData = self.ui.resourceList.model().mimeData(listsQModelIndex)
                if not dataQMimeData:
                    return None
                dragQDrag = QDrag(self.ui.resourceList)
                dragQDrag.setMimeData(dataQMimeData)
                defaultDropAction = Qt.DropAction.IgnoreAction
                if ((supportedActions & Qt.DropAction.CopyAction) and (
                        self.ui.resourceList.dragDropMode() != QAbstractItemView.DragDropMode.InternalMove)):
                    defaultDropAction = Qt.DropAction.CopyAction
                dragQDrag.exec(supportedActions, defaultDropAction)

        def search():
            # search resourceList
            filter_text = self.ui.resourceSearch.text()
            visible_items = []
            for x in range(self.ui.resourceList.count()):
                item = self.ui.resourceList.item(x)
                if filter_text.lower() in item.text().lower():
                    item.setHidden(False)
                    visible_items.append(x)
                else:
                    item.setHidden(True)

            if filter_text != "" and visible_items != []:
                self.ui.resourceList.setCurrentRow(visible_items[0])

        def openResourceFolder():
            currentProject = self.getCurrentProject()

            if currentProject == None or not currentProject.get("project"):
                return

            self.openFolder(currentProject["project"].imageFolder)

        def addResource():
            currentProject = self.getCurrentProject()

            if currentProject == None or not currentProject.get("project"):
                return

            files = QFileDialog.getOpenFileNames(self, _("Add Image..."), "%userprofile%\\",
                                                 "Image File (*.png *.jpeg *.jpg)")

            if not files[0]:
                return

            for file in files[0]:
                destFile = os.path.join(currentProject["project"].imageFolder, os.path.basename(file))
                if os.path.isfile(destFile):
                    self.showDialog("info", f"File {destFile} already exists!")
                else:
                    shutil.copyfile(file, destFile)

            currentProject["canvas"].clearSelected()
            self.reloadImages(currentProject["project"].imageFolder)

        def reloadResource():
            currentProject = self.getCurrentProject()

            if currentProject == None or not currentProject.get("project"):
                return

            self.reloadImages(currentProject["project"].imageFolder)

        self.statusBar().setContentsMargins(4, 4, 4, 4)

        self.ui.resourceList.startDrag = startDrag
        self.ui.resourceSearch.textChanged.connect(search)
        self.ui.reloadResource.clicked.connect(reloadResource)
        self.ui.addResource.clicked.connect(addResource)
        self.ui.openResourceFolder.clicked.connect(openResourceFolder)

        # Connect objects in the Insert menu to actions
        self.ui.actionImage.triggered.connect(lambda: self.createWatchfaceWidget("widget"))
        self.ui.actionImage_List.triggered.connect(lambda: self.createWatchfaceWidget("widget_imagelist"))
        self.ui.actionDigital_Number.triggered.connect(lambda: self.createWatchfaceWidget("widget_num"))
        self.ui.actionAnalog_Display.triggered.connect(lambda: self.createWatchfaceWidget("widget_analog"))
        self.ui.actionArc_Progress.triggered.connect(lambda: self.createWatchfaceWidget("widget_arc"))

        # Connect tab changes
        self.ui.workspace.tabCloseRequested.connect(self.closeTab)
        self.ui.workspace.currentChanged.connect(handleTabChange)

    def setupExplorer(self):
        self.Explorer = Explorer(self, ObjectIcon(), self.ui)
        self.ui.explorerWidget.setWidget(self.Explorer)
        self.Explorer.itemSelectionChanged.connect(lambda: self.updateProjectSelections("explorer"))

    def clearExplorer(self):
        self.Explorer.clear()

    def setupProperties(self):
        def setProperty(args):
            currentProject = self.getCurrentProject()
            if currentProject == None or not currentProject.get("project"):
                return
            currentSelected = self.Explorer.currentItem()

            # search for item by name, and if available set as currentItem
            currentItem = currentProject["project"].getWidget(currentSelected.data(0, 101))

            if currentItem == None:
                return

            currentProject["hasFileChanged"] = True
            self.fileChanged = True

            if "*" not in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(),
                                             self.ui.workspace.tabText(self.ui.workspace.currentIndex()) + "*")

            logging.info(f"Set property {args[0]}, {args[1]} for widget {currentSelected.data(0, 101)}")

            def updateProperty(widgetName, property, value):
                print("select")
                if currentProject["canvas"].getObject(widgetName).isSelected() is not True:
                    currentProject["canvas"].selectObject(widgetName)
                    
                print("chk property")
                if property == "num_source" or property == "imagelist_source" or property == "widget_visibility_source":
                    if value == "None":
                        currentItem.setProperty(property, 0)
                    else:
                        for data in self.WatchData.modelSourceData[str(currentProject["project"].getDeviceType())]:
                            if data["@Name"] == value:
                                try:
                                    currentItem.setProperty(property, int(data["@ID"], 0))
                                except:
                                    currentItem.setProperty(property, int(data["@ID"]))
                                break
                        else:
                            self.showDialog("warning", "Invalid source name!")
                            return
                elif property == "num_alignment":
                    alignmentList = ["Left", "Center", "Right"]
                    print(str(alignmentList.index(value)))
                    currentItem.setProperty(property, str(alignmentList.index(value)))
                elif property == "widget_name":
                    if value == widgetName:
                        return
                    elif currentProject["canvas"].getObject(value):
                        self.showDialog("info", "Another widget has this name! Please change it to something else.")
                        return
                    else:
                        currentItem.setProperty(property, value)

                elif property == "widget_bitmap":
                    pixmap = QPixmap()
                    pixmap.load(os.path.join(currentProject["project"].imageFolder, value))

                    # set widget size to image size
                    currentItem.setProperty("widget_size_width", pixmap.width())
                    self.propertiesWidget.propertyItems["widget_size_width"].setText(str(pixmap.width()))
                    currentItem.setProperty("widget_size_height", pixmap.height())
                    self.propertiesWidget.propertyItems["widget_size_height"].setText(str(pixmap.width()))

                    currentItem.setProperty(property, value)

                elif isinstance(value, bool):
                    if value == True:
                        value = "1"
                    else:
                        value = "0"
                    currentItem.setProperty(property, value)
                else:
                    currentItem.setProperty(property, value)

                print("update")
                if property == "widget_name":
                    self.propertiesWidget.clearOnRefresh = False
                    print("explorer update")
                    self.Explorer.updateExplorer(currentProject["project"])
                    print("load obj")
                    currentProject["canvas"].loadObjects(currentProject["project"],
                                                         self.settings["Canvas"]["Snap"]["value"],
                                                        self.settings["Canvas"]["Interpolation"]["value"],
                                                        self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                                        self.settings["Canvas"]["ShowDeviceOutline"]["value"])
                    currentProject["canvas"].selectObject(value)
                else:
                    self.propertiesWidget.clearOnRefresh = False
                    currentProject["canvas"].reloadObject(widgetName, currentItem)

                    currentProject["canvas"].selectObject(widgetName)

            if self.ignoreHistoryInvoke:
                print("ignore history")
                self.ignoreHistoryInvoke = False
                updateProperty(currentSelected.data(0, 101), args[0], args[1])
            else:
                print("command")
                command = CommandModifyProperty(currentItem.getProperty("widget_name"), args[0],
                                                currentItem.getProperty(args[0]), args[1], updateProperty,
                                                f"Change property {args[0]} to {args[1]}")
                self.History.undoStack.push(command)
                self.ignoreHistoryInvoke = False

        # Setup properties widget
        with open("data/properties.json", encoding="utf8") as raw:
            propertiesSource = raw.read()
            self.propertyJson = json.loads(propertiesSource)
            self.propertiesWidget = PropertiesWidget(self, self.WatchData.modelSourceList,
                                                     self.WatchData.modelSourceData)
            self.propertiesWidget.propertyChanged.connect(lambda *args: setProperty(args))
            self.ui.propertiesWidget.setWidget(self.propertiesWidget)

    def updateProperties(self, item, itemType=None):
        currentProject = self.getCurrentProject()
        if item and currentProject["project"].getWidget(item) != None:
            if self.propertiesWidget.clearOnRefresh:
                self.propertiesWidget.loadProperties(self.propertyJson[itemType], currentProject["project"], item,
                                                     self.resourceImages, currentProject["project"].getDeviceType())
            else:
                self.propertiesWidget.clearOnRefresh = True
        else:
            if self.propertiesWidget.clearOnRefresh:
                self.propertiesWidget.clearProperties()

    def setupDialogs(self):
        def closeEvent():
            if not self.isVisible():
                sys.exit()

        def saveConfig():
            currentProject: FprjProject = self.getCurrentProject()["project"]
            currentProject.setTitle(self.coreDialog.configurePageNameField.text())
            currentProject.setThumbnail(self.coreDialog.configurePagePreviewField.currentText())
            self.coreDialog.close()

        def resetSettings():
            result = self.showDialog("question", _("Are you sure you want to reset all settings?"), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, defaultButton=QMessageBox.StandardButton.No)
            if result == QMessageBox.StandardButton.Yes:
                QSettings("Mi Create", "Settings").clear()
                QSettings("Mi Create", "Workspace").clear()
                self.loadSettings()
                self.loadTheme()
                self.loadLanguage(True)
                self.settingsWidget.loadProperties(self.settings)

        self.coreDialog = CoreDialog(None, self.settingsWidget, f"{programVersion} • compiler {self.WatchData.getCompilerVersion()}",
                                     self.WatchData.models)
        self.coreDialog.welcomeSidebarOpenProject.clicked.connect(self.openProject)
        self.coreDialog.reloadSettings.connect(lambda: self.settingsWidget.loadProperties(self.settings))
        self.coreDialog.updateCompiler.connect(lambda compiler, db: self.WatchData.updateDataFiles(compiler, db))
        self.coreDialog.resetSettings.connect(resetSettings)
        self.coreDialog.manageProjectSidebarSave.clicked.connect(saveConfig)
        self.coreDialog.rejected.connect(closeEvent)

        deviceField = self.coreDialog.watchfacePageDeviceField
        nameField = self.coreDialog.watchfacePageProjectField
        locationField = self.coreDialog.watchfacePageDirectoryField

        self.coreDialog.watchfacePageButtonBox.accepted.connect(
            lambda: self.newProject(locationField.text(), nameField.text(), deviceField.currentText()))

        def projectListOpen():
            if len(self.coreDialog.welcomePage.selectedItems()) == 1:
                listItem = self.coreDialog.welcomePage.selectedItems()[0]
                QApplication.instance().processEvents()
                self.openProject(projectLocation=listItem.toolTip())

        self.coreDialog.welcomePage.itemPressed.connect(projectListOpen)

    def changeSelectionInExplorer(self, name):
        if isinstance(name, str):
            self.Explorer.items[name].setSelected(True)
        elif isinstance(name, list):
            for item in name:
                self.Explorer.items[name].setSelected(True)

    def createWatchfaceWidget(self, id):
        currentProject = self.getCurrentProject()

        if not currentProject.get("project"):
            return

        count = 0
        for widget in currentProject["project"].getAllWidgets():
            if "widget-" in widget.getProperty("widget_name"):
                count += 1

        name = "widget-" + str(count)
    
        if self.ignoreHistoryInvoke:
            self.ignoreHistoryInvoke = False
        else:
            def commandFunc(type, name):
                if type == "undo":
                    currentProject["project"].deleteWidget(currentProject["project"].getWidget(name))
                elif type == "redo":
                    currentProject["project"].createWidget(id, name, "center", "center")
                    currentProject["canvas"].loadObjects(currentProject["project"],
                                            self.settings["Canvas"]["Snap"]["value"],
                                            self.settings["Canvas"]["Interpolation"]["value"],
                                            self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                            self.settings["Canvas"]["ShowDeviceOutline"]["value"])
                self.Explorer.updateExplorer(currentProject["project"])

            print(name)
            command = CommandAddWidget(name, commandFunc, f"Add object {name}")
            self.History.undoStack.push(command)

    def changeSelectedWatchfaceWidgetLayer(self, changeType):
        currentProject = self.getCurrentProject()
        currentCanvasSelected = []

        if currentProject == None or not currentProject.get("canvas"):
            return

        for item in currentProject["canvas"].getSelectedObjects():
            currentCanvasSelected.insert(int(item.zValue()),
                                         [currentProject["project"].getWidget(item.data(0)), int(item.zValue())])

        if currentCanvasSelected == []:
            return

        def commandFunc(type, layerChange, widgets):
            if type == "undo":
                for widget in widgets:
                    currentProject["project"].setWidgetLayer(widget[0], widget[1])
            elif type == "redo":
                if layerChange == "bottom":
                    widgets.reverse()  # preserve widget stacking order by doing the first widgets last

                for widget in widgets:
                    if layerChange == "raise":
                        currentProject["project"].setWidgetLayer(widget[0], widget[1] + 1)
                    elif layerChange == "lower" and widget[1] - 1 >= 0:
                        currentProject["project"].setWidgetLayer(widget[0], widget[1] - 1)
                    elif layerChange == "top":
                        currentProject["project"].setWidgetLayer(widget[0], "top")
                    elif layerChange == "bottom":
                        currentProject["project"].setWidgetLayer(widget[0], 0)

            currentProject["canvas"].loadObjects(currentProject["project"], self.settings["Canvas"]["Snap"]["value"],
                                                self.settings["Canvas"]["Interpolation"]["value"],
                                                self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                                self.settings["Canvas"]["ShowDeviceOutline"]["value"])
            self.Explorer.updateExplorer(currentProject["project"])

        command = CommandModifyWidgetLayer(currentCanvasSelected, changeType, commandFunc,
                                           f"Change object/s order through ModifyProjectData command")
        self.History.undoStack.push(command)

    def deleteSelectedWatchfaceWidgets(self):
        currentProject = self.getCurrentProject()
        itemList = []
        if not currentProject.get("project"):
            return

        for item in currentProject["canvas"].getSelectedObjects():
            itemList.append(item)

        if self.ignoreHistoryInvoke:
            self.ignoreHistoryInvoke = False
        else:
            def commandFunc(type, widgetList):
                if type == "undo":
                    for widget, index in widgetList:
                        currentProject["project"].restoreWidget(widget, index)

                elif type == "redo":
                    for widget in widgetList:
                        currentProject["project"].deleteWidget(widget[0])

                currentProject["canvas"].loadObjects(currentProject["project"],
                                                     self.settings["Canvas"]["Snap"]["value"],
                                                    self.settings["Canvas"]["Interpolation"]["value"],
                                                    self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                                    self.settings["Canvas"]["ShowDeviceOutline"]["value"])
                self.Explorer.updateExplorer(currentProject["project"])

            widgetList = []
            for item in itemList:
                widgetList.append([currentProject["project"].getWidget(item.data(0)), int(item.zValue())])

            command = CommandDeleteWidget(widgetList, commandFunc, f"Delete objects through ModifyProjectData command")
            self.History.undoStack.push(command)

    def cutSelectedWatchfaceWidgets(self):
        self.copySelectedWatchfaceWidgets()
        self.deleteSelectedWatchfaceWidgets()

    def copySelectedWatchfaceWidgets(self):
        currentProject = self.getCurrentProject()
        if not currentProject.get("canvas"):
            return

        selectedObjects = currentProject["canvas"].getSelectedObjects()
        self.clipboard = []

        for object in selectedObjects:
            # preserve layer order
            self.clipboard.insert(int(object.zValue()), currentProject["project"].getWidget(object.data(0)))

    def pasteWatchfaceWidgets(self):
        currentProject = self.getCurrentProject()

        if not currentProject.get("project") or self.clipboard == []:
            return

        clipboardCopy = self.clipboard.copy()

        for item in clipboardCopy:
            count = 0

            for existingWidget in currentProject["project"].getAllWidgets():
                if item.getProperty("widget_name") in existingWidget.getProperty("widget_name"):
                    count += 1

            if count > 0:
                name_suffix = ' - Copy'

                item.removeAssociation()
                item.setProperty("widget_name", f"{item.getProperty('widget_name')}{name_suffix}{count}")

        def commandFunc(type, clipboard):
            currentProject["canvas"].clearSelected()

            if type == "undo":
                for widget in clipboard:
                    currentProject["project"].deleteWidget(widget)
            elif type == "redo":
                for widget in clipboard:
                    currentProject["project"].appendWidget(widget)

            currentProject["canvas"].loadObjects(currentProject["project"], self.settings["Canvas"]["Snap"]["value"],
                                                self.settings["Canvas"]["Interpolation"]["value"],
                                                self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                                self.settings["Canvas"]["ShowDeviceOutline"]["value"])
            self.Explorer.updateExplorer(currentProject["project"])

            # select objects pasted in
            if type == "redo":
                for widget in clipboard:
                    currentProject["canvas"].selectObject(widget.getProperty("widget_name"), False)

        print(clipboardCopy)

        command = CommandPasteWidget(clipboardCopy, commandFunc, f"Paste objects through ModifyProjectData command")
        self.History.undoStack.push(command)

    def zoomCanvas(self, zoom):
        currentProject = self.getCurrentProject()

        if not currentProject.get("canvas"):
            return

        if zoom == "in":
            zoom_factor = 1.25
            currentProject["canvas"].scale(zoom_factor, zoom_factor)
        elif zoom == "out":
            zoom_factor = 1 / 1.25
            currentProject["canvas"].scale(zoom_factor, zoom_factor)

    def updateProjectSelections(self, subject):
        currentProject = self.getCurrentProject()
        currentCanvasSelected = []
        currentExplorerSelected = []

        if currentProject == None or not currentProject.get("canvas") or self.selectionDebounce:
            return

        for item in currentProject["canvas"].scene().selectedItems():
            currentCanvasSelected.append(item.data(0))

        for item in self.Explorer.selectedItems():
            currentExplorerSelected.append(item.data(0, 101))

        if set(currentCanvasSelected) == set(currentExplorerSelected):
            return

        if subject == "canvas":
            self.selectionDebounce = True

            if len(currentCanvasSelected) > 1:
                for key in self.Explorer.items:
                    if key in currentCanvasSelected:
                        self.Explorer.items[key].setSelected(True)
                    else:
                        self.Explorer.items[key].setSelected(False)
            elif len(currentCanvasSelected) == 1:
                self.Explorer.setCurrentItem(self.Explorer.items[currentCanvasSelected[0]])
            else:
                self.Explorer.setCurrentItem(None)

            if len(currentCanvasSelected) == 1:
                self.updateProperties(currentCanvasSelected[0],
                                      self.Explorer.items[currentCanvasSelected[0]].data(0, 100))
            else:
                self.updateProperties(False)

            self.selectionDebounce = False
        elif subject == "explorer":
            self.selectionDebounce = True

            for item in currentExplorerSelected:
                currentProject["canvas"].selectObject(currentExplorerSelected[0])

            if currentExplorerSelected == [] or currentExplorerSelected[0] == None:
                self.selectionDebounce = False
                self.updateProperties(False)
                return

            if len(currentExplorerSelected) == 1:
                self.updateProperties(currentExplorerSelected[0],
                                      self.Explorer.items[currentExplorerSelected[0]].data(0, 100))
            else:
                self.updateProperties(False)

            self.selectionDebounce = False

    def createNewWorkspace(self, project):
        # projects are technically "tabs"
        self.previousSelected = None
        if self.projects.get(project.directory):
            self.ui.workspace.setCurrentIndex(self.ui.workspace.indexOf(self.projects[project.directory]['canvas']))
            return

        def propertyChange(objectName, propertyName, propertyValue):
            propertyField = self.propertiesWidget.propertyItems.get(propertyName)

            if not propertyField:
                return

            if isinstance(propertyValue, list):
                propertyValue = propertyValue[0]

            if propertyField.metaObject().className() == "QSpinBox":
                propertyField.setValue(int(propertyValue))
            else:
                propertyField.setText(propertyValue)

        def posChange():
            currentProject = self.getCurrentProject()
            selectedObjects = currentProject["canvas"].getSelectedObjects()

            prevPos = []
            currentPos = []

            for object in selectedObjects:
                widget = currentProject["project"].getWidget(object.data(0))

                if int(widget.getProperty("widget_pos_x")) == round(object.pos().x()) and int(
                        widget.getProperty("widget_pos_y")) == round(object.pos().y()):
                    print("return")
                    return

                prevPosObject = {
                    "Name": widget.getProperty("widget_name"),
                    "Widget": widget,
                    "X": widget.getProperty("widget_pos_x"),
                    "Y": widget.getProperty("widget_pos_y")
                }
                currentPosObject = {
                    "Name": widget.getProperty("widget_name"),
                    "Widget": widget,
                    "X": round(object.pos().x()),
                    "Y": round(object.pos().y())
                }
                prevPos.append(prevPosObject)
                currentPos.append(currentPosObject)

            if "*" not in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(),
                                             self.ui.workspace.tabText(self.ui.workspace.currentIndex()) + "*")
                self.fileChanged = True
                currentProject["hasFileChanged"] = True

            def commandFunc(objects):
                if isinstance(currentProject["project"], FprjProject):
                    for object in objects:
                        object["Widget"].setProperty("widget_pos_x", int(object["X"]))
                        object["Widget"].setProperty("widget_pos_y", int(object["Y"]))
                currentProject["canvas"].loadObjects(currentProject["project"],
                                                     self.settings["Canvas"]["Snap"]["value"],
                                                     self.settings["Canvas"]["Interpolation"]["value"],
                                                     self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                                     self.settings["Canvas"]["ShowDeviceOutline"]["value"])
                currentProject["canvas"].selectObjectsFromPropertyList(objects)

            command = CommandModifyPosition(prevPos, currentPos, commandFunc, f"Change object pos")
            self.History.undoStack.push(command)

        # Setup Project
        self.projectXML = xml
        self.Explorer.clear()

        # Create a Canvas (QGraphicsScene & QGraphicsView)
        canvas = Canvas(project.getDeviceType(), self.settings["Canvas"]["Antialiasing"]["value"],
                        self.settings["Canvas"]["ClipDeviceShape"]["value"], self.ui, self)

        # Create the project
        canvas.setAcceptDrops(True)
        canvas.scene().selectionChanged.connect(lambda: self.updateProjectSelections("canvas"))
        canvas.onObjectChange.connect(propertyChange)
        canvas.onObjectPosChange.connect(posChange)

        # Add Icons
        icon = QIcon().fromTheme("project-icon")

        success = True

        # Render objects onto the canvas
        if project is not False:
            success = canvas.loadObjects(project,
                                         self.settings["Canvas"]["Snap"]["value"],
                                         self.settings["Canvas"]["Interpolation"]["value"],
                                         self.settings["Canvas"]["ClipDeviceShape"]["value"],
                                         self.settings["Canvas"]["ShowDeviceOutline"]["value"])

        if success[0]:
            self.projects[project.directory] = {
                "type": "workspace",
                "canvas": canvas,
                "project": project,
                "hasFileChanged": False
            }

            widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(canvas)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            widget.setLayout(layout)

            name = os.path.basename(project.name)

            index = self.ui.workspace.addTab(widget, icon, name)
            self.ui.workspace.setTabToolTip(index, project.directory)
            self.ui.workspace.setCurrentIndex(index)
            canvas.setFrameShape(QFrame.Shape.NoFrame)

            if self.ui.workspace.count() == 1:  # new tab from empty workspace does not refresh
                self.setIconState(False)
                self.selectionDebounce = False
                self.Explorer.updateExplorer(project)
                logging.info("Explorer updated")
                thread = threading.Thread(target=lambda: self.reloadImages(project.imageFolder))
                thread.start()
                self.show()

            self.coreDialog.close()

        else:
            self.showDialog("error", "Cannot render project!" + success[1], success[1])

    def createNewCodespace(self, name, path, text, language):
        # Creates a new instance of QScintilla in a Codespace (code workspace)
        def textChanged():
            self.fileChanged = True
            if "*" not in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(),
                                             self.ui.workspace.tabText(self.ui.workspace.currentIndex()) + "*")

        widget = QWidget()
        editor = Editor(widget, self.palette(), language)
        editor.setText(text)
        editor.textChanged.connect(textChanged)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(editor)
        widget.setLayout(layout)

        icon = QIcon(":/Dark/file-code-2.png")
        index = self.ui.workspace.addTab(widget, icon, name)
        self.projects[path] = {
            "type": "codespace",
            "hasFileChanged": False,
            "editor": editor,
            "path": path
        }
        self.ui.workspace.setTabToolTip(index, path)
        self.ui.workspace.setCurrentIndex(index)

    def setupWidgets(self):
        # Setup Dock Widgets
        #self.dockManager = CDockManager(self)

        # Connect menu actions

        def toggleViewOfWidget(action, widget):
            if widget.isVisible():
                widget.hide()
                action.setChecked(False)
            else:
                widget.show()
                action.setChecked(True)

        # file
        self.ui.actionNewFile.triggered.connect(self.showNewProjectDialog)
        self.ui.actionManage_Project.triggered.connect(self.showManageProjectDialog)
        self.ui.actionClose_Project.triggered.connect(lambda: self.closeTab(self.ui.workspace.currentIndex()))
        self.ui.actionOpenFile.triggered.connect(self.openProject)
        self.ui.actionSave.triggered.connect(lambda: self.saveProjects("current"))
        self.ui.actionExit.triggered.connect(self.close)

        # edit
        self.ui.actionDelete.triggered.connect(self.deleteSelectedWatchfaceWidgets)
        self.ui.actionCut.triggered.connect(self.cutSelectedWatchfaceWidgets)
        self.ui.actionCopy.triggered.connect(self.copySelectedWatchfaceWidgets)
        self.ui.actionPaste.triggered.connect(self.pasteWatchfaceWidgets)
        self.ui.actionUndo.triggered.connect(lambda: self.History.undoStack.undo())
        self.ui.actionRedo.triggered.connect(lambda: self.History.undoStack.redo())
        self.ui.actionBring_to_Front.triggered.connect(lambda: self.changeSelectedWatchfaceWidgetLayer("top"))
        self.ui.actionBring_Forwards.triggered.connect(lambda: self.changeSelectedWatchfaceWidgetLayer("raise"))
        self.ui.actionSend_to_Back.triggered.connect(lambda: self.changeSelectedWatchfaceWidgetLayer("bottom"))
        self.ui.actionSend_Backwards.triggered.connect(lambda: self.changeSelectedWatchfaceWidgetLayer("lower"))
        self.ui.actionProject_XML_File.triggered.connect(self.editProjectXML)
        self.ui.actionPreferences.triggered.connect(self.showSettings)

        # view
        def updateViewMenu():
            self.ui.actionToggleExplorer.setChecked(self.ui.explorerWidget.isVisible())
            self.ui.actionToggleResources.setChecked(self.ui.resourcesWidget.isVisible())
            self.ui.actionToggleProperties.setChecked(self.ui.propertiesWidget.isVisible())
            self.ui.actionToggleToolbar.setChecked(self.ui.toolBar.isVisible())
        
        self.ui.menuView.aboutToShow.connect(updateViewMenu)
        self.ui.actionToggleExplorer.triggered.connect(
            lambda: toggleViewOfWidget(self.ui.actionToggleExplorer, self.ui.explorerWidget))
        self.ui.actionToggleResources.triggered.connect(
            lambda: toggleViewOfWidget(self.ui.actionToggleResources, self.ui.resourcesWidget))
        self.ui.actionToggleProperties.triggered.connect(
            lambda: toggleViewOfWidget(self.ui.actionToggleProperties, self.ui.propertiesWidget))
        self.ui.actionToggleToolbar.triggered.connect(
            lambda: toggleViewOfWidget(self.ui.actionToggleToolbar, self.ui.toolBar))
        self.ui.actionZoom_In.triggered.connect(lambda: self.zoomCanvas("in"))
        self.ui.actionZoom_Out.triggered.connect(lambda: self.zoomCanvas("out"))
        self.ui.actionFull_Screen.triggered.connect(self.toggleFullscreen)

        # compile
        self.ui.actionBuild.triggered.connect(self.compileProject)
        #self.ui.actionUnpack.triggered.connect(self.decompileProject)

        # help
        self.ui.actionDocumentation.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://ooflet.github.io/docs", QUrl.ParsingMode.TolerantMode)))
        self.ui.actionWelcome.triggered.connect(self.showWelcome)
        self.ui.actionAbout_MiFaceStudio.triggered.connect(self.showAboutWindow)
        self.ui.actionAbout_Qt.triggered.connect(lambda: QMessageBox.aboutQt(self))

    def clearWindowState(self):
        reply = QMessageBox.question(self, 'Confirm Clear',
                                     _("Are you sure you want to reset all dock widget positions?"), QMessageBox.StandardButton.Yes,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.Yes:
            settings = QSettings("Mi Create", "Workspace")
            settings.setValue("geometry", None)
            settings.setValue("state", None)
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    def showNewProjectDialog(self):
        self.coreDialog.showNewProjectPage()
        self.coreDialog.exec()

    def newProject(self, file, projectName, watchModel):
        # Check if file was selected
        if file:
            newProject = FprjProject()
            create = newProject.fromBlank(file, self.WatchData.modelID[str(watchModel)], projectName)
            if create[0]:
                try:
                    self.createNewWorkspace(newProject)
                    settings = QSettings("Mi Create", "Workspace")
                    recentProjectList = settings.value("recentProjects")

                    if recentProjectList == None:
                        recentProjectList = []

                    path = os.path.normpath(newProject.dataPath)

                    if [os.path.basename(path), path] in recentProjectList:
                        recentProjectList.pop(recentProjectList.index([os.path.basename(path), path]))

                    recentProjectList.append(
                        [os.path.basename(newProject.dataPath), os.path.normpath(newProject.dataPath)])

                    settings.setValue("recentProjects", recentProjectList)
                except Exception as e:
                    self.showDialog("error", _("Failed to createNewWorkspace: ") + e, traceback.format_exc())
            else:
                self.showDialog("error", _("Failed to create a new project: ") + create[1], create[2])

    def openProject(self, event=None, projectLocation=None):
        # Get where to open the project from
        if projectLocation == None:
            projectLocation = QFileDialog.getOpenFileName(self, _('Open Project...'), "%userprofile%/")

        if not isinstance(projectLocation, str):
            projectLocation = projectLocation[0].replace("\\", "/")

        if os.path.isfile(projectLocation):
            if os.path.splitext(projectLocation)[1] == '.fprj':
                project = FprjProject()
            else:
                self.showDialog("error", "Invalid project!")
                return False
        else:
            # no file was selected
            return False

        load = project.fromExisting(projectLocation)
        if load[0]:
            try:
                self.createNewWorkspace(project)
                settings = QSettings("Mi Create", "Workspace")
                recentProjectList = settings.value("recentProjects")

                if recentProjectList == None:
                    recentProjectList = []

                path = os.path.normpath(projectLocation)
                projectListing = [os.path.basename(path), path]
                print(path)

                if projectListing in recentProjectList:
                    recentProjectList.pop(recentProjectList.index(projectListing))

                recentProjectList.append(projectListing)

                settings.setValue("recentProjects", recentProjectList)
            except Exception as e:
                self.showDialog("error", _("Failed to open project: ") + str(e), traceback.format_exc())
                return False
        else:
            self.showDialog("error", _('Cannot open project: ') + load[1], load[2])
            return False

    def showManageProjectDialog(self):
        currentProject: FprjProject = self.getCurrentProject()["project"]

        self.coreDialog.configurePagePreviewField.addItems(self.resourceImages)

        self.coreDialog.configurePageNameField.setText(currentProject.getTitle())
        self.coreDialog.configurePagePreviewField.setCurrentText(currentProject.getThumbnail())

        self.coreDialog.showManageProjectPage()
        self.coreDialog.exec()

    def saveProjects(self, projectsToSave):
        if projectsToSave == "all":
            for index, project in enumerate(self.projects.items()):
                project = project[1]
                if project["hasFileChanged"]:
                    if not project.get("project"):
                        return
                    success, message = project.save()
                    if not success:
                        self.showDialog("error", _("Failed to save project: ") + str(message))

        elif projectsToSave == "current":
            currentIndex = self.ui.workspace.currentIndex()
            currentProject = self.getCurrentProject()

            if currentProject.get("project"):
                success, message = currentProject["project"].save()
                if success:
                    self.statusBar().showMessage(_("Project saved at ") + currentProject["project"].dataPath, 2000)
                    self.fileChanged = False
                    currentProject["hasFileChanged"] = False
                else:
                    self.statusBar().showMessage(_("Failed to save: ") + str(message), 10000)
                    self.showDialog("error", _("Failed to save project: ") + str(message))
            elif currentProject.get("editor"):
                try:
                    with open(currentProject["path"], "w", encoding="utf8") as file:
                        file.write(currentProject["editor"].text())
                    self.statusBar().showMessage(_("Project saved at ") + currentProject["path"], 2000)
                except Exception as e:
                    self.statusBar().showMessage(_("Failed to save: ") + str(e), 10000)
                    self.showDialog("error", _("Failed to save project: ") + str(e))

            if "*" in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(),
                                             self.ui.workspace.tabText(self.ui.workspace.currentIndex()).replace("*",
                                                                                                                 ""))

    def createPreview(self):
        currentProject = self.getCurrentProject()

        scene = currentProject["canvas"].scene()
        scene.clearSelection()  # Clear selection
        scene.setSceneRect(scene.itemsBoundingRect())  # Adjust scene rectangle
        image = QImage(scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)  # Create image
        image.fill(Qt.GlobalColor.transparent)  # Fill image with transparent pixels

        # Render scene onto the image
        painter = QPainter(image)
        scene.render(painter)
        painter.end()

        # Save the image
        image.save("file_name.png")

    def compileProject(self):
        if not self.getCurrentProject().get("project"):
            return

        if self.compiling:
            return

        if platform.system() != "Windows":
            self.showDialog("info", "The compiler only supports Windows. Linux support will be added soon.")
            return
        
        result = self.showDialog("question", _("Save project before building?"), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, defaultButton=QMessageBox.StandardButton.Yes)

        currentProject = self.getCurrentProject()

        if result == QMessageBox.StandardButton.Yes:
            self.saveProjects("current")
        elif result == QMessageBox.StandardButton.Cancel:
            return

        if currentProject["project"].getTitle() == "" or currentProject["project"].getThumbnail() == "":
            self.showDialog("info", _("Please set the watchface's name and thumbnail before building!"))
            self.showManageProjectDialog()
            return

        self.compiling = True

        def success():
            self.compiling = False
            progressBar.deleteLater()
            text.deleteLater()

            print(output)

            if "Error:" in output[1]:
                parts = output[1].split('\r\n')
                # The desired error message is the first part

                extracted_error = parts[0]

                self.showDialog("error", _("Failed to build watchface! ") + extracted_error)
                return

            fileLocation = str.split(os.path.basename(currentProject["project"].dataPath), ".")[0] + ".face"
            self.statusBar().showMessage(_("Watchface built successfully at ") + f"{compileDirectory}\\{fileLocation}",
                                         3000)

        progressBar = QProgressBar()
        progressBar.setRange(0, 0)
        text = QLabel("Building watchface...")
        self.statusBar().addPermanentWidget(text, 0)
        self.statusBar().addPermanentWidget(progressBar, 1)

        compileDirectory = os.path.join(os.path.dirname(currentProject["project"].dataPath), "output")
        output = []

        process = currentProject["project"].compile(currentProject["project"].dataPath, compileDirectory,
                                                    "compiler/compile.exe")
        process.readyReadStandardOutput.connect(lambda: output.append(bytearray(process.readAll()).decode('utf-8', 'backslashreplace')))
        process.finished.connect(success)

    def decompileProject(self):
        self.showDialog("warning", _("Please note that unpacking is not perfect, some parts of the watchface may be glitched."))

        dialog = MultiFieldDialog(self, _("Unpack Binary"), _("Unpack Binary"))
        binaryField = dialog.addFileField(_("Watchface Binary"), mandatory=True)
        outputField = dialog.addFolderField(_("Output Location"), mandatory=True)
        dialog.addButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        dialog.exec()

        def accept():
            project = FprjProject()
            success, message = project.fromBinary(outputField.text(), binaryField.text())

        dialog.accepted

    def editProjectXML(self):
        currentProject = self.getCurrentProject()

        if not currentProject.get("project"):
            return

        projectString = currentProject["project"].toString()
        if self.projects.get(currentProject["project"].dataPath):
            self.ui.workspace.setCurrentIndex(
                self.ui.workspace.indexOf(self.projects[currentProject["path"]]["editor"]))
            return
        self.createNewCodespace("Project XML", currentProject["project"].dataPath, projectString, XMLLexer)

    def showColorDialog(self):
        color = QColorDialog.getColor(Qt.white, self, "Select Color")

    def showFontSelect(self):
        font = QFontDialog.getFont(self, "Select Font")

    def showSettings(self):
        self.coreDialog.showSettingsPage()
        self.coreDialog.exec()

    def showAboutWindow(self):
        dialog = FramelessDialog(self)
        dialog.setFixedSize(350, 325)
        dialog.setContentsMargins(5, 60, 5, 5)
        aboutIcon = QLabel()
        aboutIcon.setPixmap(QPixmap(":/Images/MiCreate48x48.png"))
        aboutIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aboutText = QLabel()
        aboutText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aboutText.setText(
            f'''
            <html>
            <head/>
            <body>
                <p>Mi Create {programVersion}<br/>Visit the <a href="https://github.com/ooflet/Mi-Create/">Github Repo</a> to get help or contribute.</p>
                <p>Copyright (C) 2024 ooflet<br/>
                    This program comes with ABSOLUTELY NO WARRANTY.<br/>
                    This is free software, and you are welcome to redistribute it<br/>
                    under certain conditions.</p>
            </body>
            </html>
            '''
        )
        aboutText.setOpenExternalLinks(True)
        buttonBox = QDialogButtonBox()
        buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        buttonBox.accepted.connect(dialog.close)
        dialogLayout = QVBoxLayout()
        dialogLayout.setSpacing(20)
        dialogLayout.addStretch()
        dialogLayout.addWidget(aboutIcon)
        dialogLayout.addWidget(aboutText)
        dialogLayout.addStretch()
        dialogLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        dialogLayout.addStretch()
        dialogLayout.addWidget(buttonBox)
        dialog.setLayout(dialogLayout)
        dialog.titleBar.raise_()
        dialog.exec()

    def showDialog(self, type, text, detailedText="", buttons=None, defaultButton=None, checkbox=None,
                   checkboxTicked=None):
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Mi Create")
        MessageBox.setWindowIcon(QIcon(":/Images/MiCreate48x48.png"))
        MessageBox.setText(text)
        MessageBox.setDetailedText(detailedText)
        if type == "info":
            MessageBox.setIcon(QMessageBox.Icon.Information)
        elif type == "question":
            MessageBox.setIcon(QMessageBox.Icon.Question)
        elif type == "warning":
            logging.warning(text)
            MessageBox.setIcon(QMessageBox.Icon.Warning)
        elif type == "error":
            logging.error(text)
            logging.error("Detailed output: " + detailedText)
            logging.error(
                f"Error dump: \nprojects: {pformat(self.projects)}\n------------------------\nsettings: {pformat(self.settings)}")
            MessageBox.setIcon(QMessageBox.Icon.Critical)

        if checkbox != None:
            messageCheckBox = QCheckBox(checkbox, MessageBox)
            messageCheckBox.setChecked(checkboxTicked)
            MessageBox.setCheckBox(messageCheckBox)

        if buttons != None:
            MessageBox.setStandardButtons(buttons)
            MessageBox.setDefaultButton(defaultButton)
            result = MessageBox.exec()
            if checkbox != None:
                return result, messageCheckBox.isChecked()
            else:
                return result
        else:
            MessageBox.exec()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', default=False)
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    
    splash = QSplashScreen(QPixmap(":/Images/splash.png"))
    splash.show()
    
    # setup font
    
    QFontDatabase.addApplicationFont(":/Fonts/Inter.ttf")

    def onException(exc_type, exc_value, exc_traceback):
        exception = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        errString = "Internal error! Please report as a bug.\n\n"+exception
        logging.error(errString)
        if "C++" not in traceback.format_exception(exc_type, exc_value, exc_traceback): # prevent C++ class already deleted message from appearing on app close
                                                                                        # i will fix (soon)
            QMessageBox.critical(None, 'Error', errString, QMessageBox.StandardButton.Ok)

    sys.excepthook = onException

    if args.reset:
        QSettings("Mi Create", "Settings").clear()
        QSettings("Mi Create", "Workspace").clear()
        print("Settings reset.")

    try:
        main_window = MainWindow()

        if args.filename:
            logging.info("Opening file from argument 1")
            result = main_window.openProject(projectLocation=args.filename)
            splash.close()
            if result == False:
                main_window.showWelcome()
        else:
            splash.close()
            main_window.showWelcome()
    except Exception as e:
        error_message = "Critical error during initialization: " + traceback.format_exc()
        logging.error(error_message)
        QMessageBox.critical(None, 'Error', error_message, QMessageBox.StandardButton.Ok)
        sys.exit(1)

    sys.exit(app.exec())
