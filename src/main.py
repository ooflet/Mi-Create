# Mi Create
# tostr <ooflet@proton.me>

# TODO
# Put documentation on code, its a wasteland out there
# Remove multi-project support in favor of in-line AOD editing (through a toggle)
# Transition welcome screen to QML

import os
import time
import sys
import shutil
import requests
import subprocess
import platform
import gettext

os.chdir(os.path.dirname(os.path.realpath(__file__))) # switch working directory to program location
                                                      # so that data files can be found

from PyQt6.QtWidgets import (QMainWindow, QDialog, QInputDialog, QMessageBox, QApplication, QGraphicsScene, QProgressBar, 
                               QDialogButtonBox, QTreeWidgetItem, QFileDialog, QToolButton, QToolBar, QWidget, QVBoxLayout, 
                               QFrame, QColorDialog, QFontDialog, QSplashScreen, QGridLayout, QLabel, QListWidgetItem,
                               QSpacerItem, QSizePolicy, QAbstractItemView, QUndoView, QTextBrowser, QRubberBand)
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QDrag
from PyQt6.QtCore import Qt, QSettings, QSize, QUrl, QFileInfo, QItemSelectionModel

from pprint import pprint, pformat
from copy import deepcopy
import xml.dom.minidom
import configparser
import xmltodict
import threading
import logging

# check if compiled and if so, logs to a file
if "__compiled__" in globals():
    logging.basicConfig(level=logging.DEBUG, filemode="w", filename="data/app.log", format="%(asctime)s %(module)s.py:%(lineno)d %(threadName)-10s %(levelname)s %(message)s")
else:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(module)s.py:%(lineno)d %(threadName)-10s %(levelname)s %(message)s")

import json
import traceback

from translate import QCoreApplication
from utils.theme import Theme
from utils.updater import Updater
from utils.project import watchData, fprjProject
from utils.history import History, CommandAddWidget, CommandModifyProperty, CommandModifyPosition, CommandModifyProjectData
from widgets.canvas import Canvas, ObjectIcon
from widgets.explorer import Explorer
from widgets.properties import PropertiesWidget
from widgets.editor import Editor, XMLLexer

from translate import QCoreApplication

import resources.icons_rc # resource import required because it sets up the icons

from window_ui import Ui_MainWindow
from dialog.newProject_ui import Ui_Dialog as Ui_NewProject
from dialog.compileDialog_ui import Ui_Dialog as Ui_CompileDialog

_ = gettext.gettext

currentDir = os.getcwd()
currentVersion = 'v0.4'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.fileChanged = False
        self.clipboard = []
        self.stagedChanges = []
        self.resourceImages = []
        self.selectionDebounce = False

        self.fprjProject = fprjProject()

        # Setup Settings
        logging.debug("Loading App Settings")
        
        def close():
            self.settingsDialog.close()
            self.stagedChanges = []

        # Setup Language

        self.languages = []
        self.languageNames = []

        config = configparser.ConfigParser()
        logging.debug("Initializing Language Files")
        for file in os.listdir("locales"):
            languageDir = os.path.join("locales", file)
            if os.path.isdir(languageDir):
                logging.debug("Language directory found: "+languageDir)
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

        logging.debug("Initializing Settings")
        self.settingsDialog = QDialog(self) 
        self.settingsDialog.setFixedSize(500, 300)
        self.settingsDialog.setWindowTitle("Settings")
        self.settingsLayout = QVBoxLayout()
        self.settingsWidget = PropertiesWidget(self)
        self.settingsButtonBox = QDialogButtonBox()
        self.settingsButtonBox.setStandardButtons(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.settingsButtonBox.rejected.connect(close)
        self.settingsLayout.addWidget(self.settingsWidget)
        self.settingsLayout.addWidget(self.settingsButtonBox)
        self.settingsDialog.setLayout(self.settingsLayout)
        self.setupThemes()
        self.loadSettings() 
        self.loadTheme()

        rawSettings = QSettings("Mi Create", "Settings") 
        if "Language" not in rawSettings.allKeys():
            logging.info("No language selected")
            item, accepted = QInputDialog().getItem(self, "Mi Create", "Select Language", self.languageNames, 0)

            if item in self.languageNames:
                if accepted:
                    self.stagedChanges.append(["Language", item])
                    self.saveSettings(False)
            else:
                self.showDialog("warning", "Selected language is not available")
                
        self.settingsWidget.loadProperties(self.settings)
        self.settingsWidget.propertyChanged.connect(lambda property, value: self.stagedChanges.append([property, value]))

        # Setup projects (tabs) 
        self.projects = {
            "Welcome": {
                "hasFileChanged": False
            }
        } 
 
        # Setup WatchData 
        logging.debug("Initializing watchData")
        self.watchData = watchData() 

        # Setup History System
        self.History = History()
        self.ignoreHistoryInvoke = False
        # self.undoLayout = QVBoxLayout()
        # self.undoDialog = QDialog(self)
        # self.undoView = QUndoView(self.History.undoStack)
        # self.undoLayout.addWidget(self.undoView)
        # self.undoDialog.setLayout(self.undoLayout)
        # self.undoDialog.show()
 
        # Setup Project 
        self.project = None 
        self.projectXML = None 

        # Setup Dialog 
        logging.debug("Initializing pre-compiled dialogs")
 
        # Setup New Project Dialog 
        self.newProjectDialog = QDialog(self) 
        self.newProjectUi = Ui_NewProject() 
        self.newProjectUi.setupUi(self.newProjectDialog) 

        self.compileDialog = QDialog(self) 
        self.compileUi = Ui_CompileDialog() 
        self.compileUi.setupUi(self.compileDialog) 
        self.compileUi.buttonBox.accepted.connect(lambda: self.compileProject(1))
        self.compileUi.buttonBox.rejected.connect(self.compileDialog.close)
 
        # Setup Main Window 
        logging.debug("Initializing MainWindow")
        self.ui = Ui_MainWindow() 
        self.ui.setupUi(self) 
        logging.debug("Loading Scaffold")
        self.setupScaffold() 
        logging.debug("Initializing Application Widgets")
        self.setupWidgets() 
        logging.debug("Initializing Workspace")
        self.setupWorkspace() 
        logging.debug("Initializing Explorer")
        self.setupExplorer() 
        logging.debug("Initializing Watch Properties")
        self.setupProperties()
        logging.debug("Initializing Misc") 
        self.setupNewProjectDialog()
        self.loadWindowState()
        self.loadLanguage(True)
        self.createWelcomePage()
        logging.debug("Launch!!")
        self.statusBar().showMessage("Ready", 3000) 

    def closeEvent(self, event):
        logging.debug("Exit requested!") 
        def quitWindow():
            logging.debug("-- Exiting Mi Create --")
            currentProject = self.getCurrentProject()
            if not currentProject == None and currentProject.get("canvas"):
                currentProject["canvas"].scene().selectionChanged.disconnect()
            logging.debug("Saving Window State")
            self.saveWindowState()
            logging.debug("Quitting")
            event.accept()

        if self.fileChanged == True: 
            quit_msg = _("You have unsaved project(s) open. Save and quit?")
            reply = self.showDialog("warning", quit_msg, "", QMessageBox.StandardButton.SaveAll | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.SaveAll:
                logging.debug("Saving all unsaved projects") 
                self.saveProjects("all")
                quitWindow()
            
            elif reply == QMessageBox.StandardButton.Discard:
                quitWindow()

            else:
                event.ignore()
        else:
            quitWindow()

    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def getCurrentProject(self) -> dict:
        # tab paths are stored in the tabToolTip string.
        # temporary, only for multi-project support
        # this will be replaced in order to remove multi-project support
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
        if settings.value("usesNewLayout") == None:
            logging.warning("State and Geometry settings reset due to a new update.")
            settings.clear()
            settings.setValue("usesNewLayout", True)
        if settings.value("geometry") == None or settings.value("state") == None:
            return
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("state"))

    def saveSettings(self, retranslate, loadSettings=True):
        settings = QSettings("Mi Create", "Settings")
        for property, value in self.stagedChanges:
            settings.setValue(property, value)

        self.settingsDialog.close()
        print(loadSettings)
        if loadSettings:
            self.loadSettings()
            self.loadTheme()
        if retranslate:
            self.loadLanguage(True)

    def loadSettings(self):
        # settings are stored through QSettings, not the settingItems.json file
        # on windows its located at Computer\HKEY_CURRENT_USER\Software\Mi Create
        # on linux its located at /home/user/.config/Mi Create/
        settings = QSettings("Mi Create", "Settings")
        with open("data/settingItems.json") as file:
            self.settings = json.load(file)
            logging.debug("settingItems.json loaded")
            self.settings["General"]["Theme"]["options"] = self.themes.themeNames
            self.settings["General"]["Language"]["options"] = self.languageNames

        for key in settings.allKeys():
            for category, properties in self.settings.items():
                for property, value in properties.items():
                    if key == property:
                        logging.debug("Property load "+property)
                        if settings.value(key) == "true":
                            value["value"] = True
                        elif settings.value(key) == "false":
                            value["value"] = False
                        else:
                            value["value"] = settings.value(key)

    def loadLanguage(self, retranslate):
        selectedLanguage = None
        for language in self.languages:
            if language["languageName"] == self.settings["General"]["Language"]["value"]:
                selectedLanguage = language
                break

        if selectedLanguage != None:
            translation = gettext.translation('main', localedir='locales', languages=[os.path.basename(selectedLanguage["directory"])])
            translation.install()
            global _ # fetch global translation variable (gettext)
            _ = translation.gettext
            QCoreApplication.loadLanguage(os.path.basename(selectedLanguage["directory"]))
            self.propertiesWidget.loadLanguage(os.path.basename(selectedLanguage["directory"]))
            self.ui.retranslateUi(self) # function on each precompiled window/dialog
            self.compileUi.retranslateUi(self.compileDialog)
            self.newProjectUi.retranslateUi(self.newProjectDialog)
            # retranslate relies on the translate.py module
            # the translate module reimplements CoreApplication's translate function to rely on gettext instead
        else:
            self.showDialog("error", "Current selected language not found!")

    def launchUpdater(self):
        self.closeWithoutWarning = True
        Updater()
        sys.exit()

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

        if version > currentVersion:
            if version[-1] == 'u':
                self.showDialog('info', _('An urgent update {version} was released! The app will now update.').format(version=version))
                self.launchUpdater()
            else:
                reply = self.showDialog("question", _('A new update has been found ({version}). Would you like to update now?').format(version=version), "", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

                if reply == QMessageBox.StandardButton.Yes:
                    self.launchUpdater()

    def setupThemes(self):
        self.themes = Theme()

    def loadTheme(self):
        # Loads theme from settings table
        themeName = self.settings["General"]["Theme"]["value"]
        app = QApplication.instance()
        # if themeName == "Light":
        #     styles.light(app)
        #     self.showDialog('info', 'Icons in light theme have not been implemented yet. Sorry!')
        # elif themeName == "Dark":
        #     styles.dark(app)
        success = self.themes.loadTheme(app, themeName)
        print(success)
        if not success:
            self.showDialog("warning", f"An error occured while loading the theme {themeName}. Theme settings have been reset.")
            self.settings["General"]["Theme"]["value"] = "Dark"
            self.stagedChanges.append(["Theme", "Dark"])
            self.saveSettings(False, False)

    def createWelcomePage(self):
        Welcome = QWidget()
        Welcome.setObjectName("Welcome")
        gridLayout_3 = QGridLayout(Welcome)
        gridLayout_3.setContentsMargins(32, -1, -1, -1)
        gridLayout_3.setObjectName("gridLayout_3")
        OpenProject = QLabel(parent=Welcome)
        OpenProject.setObjectName("OpenProject")
        gridLayout_3.addWidget(OpenProject, 3, 0, 1, 1)
        spacerItem = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        gridLayout_3.addItem(spacerItem, 4, 0, 1, 1)
        WelcomeText = QLabel(parent=Welcome)
        WelcomeText.setStyleSheet("QLabel { font-size: 18pt;}")
        WelcomeText.setObjectName("WelcomeText")
        gridLayout_3.addWidget(WelcomeText, 1, 0, 1, 1)
        NewProject = QLabel(parent=Welcome)
        NewProject.setObjectName("NewProject")
        gridLayout_3.addWidget(NewProject, 2, 0, 1, 1)
        spacerItem1 = QSpacerItem(20, 177, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        gridLayout_3.addItem(spacerItem1, 0, 0, 1, 1)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/Dark/MiFaceStudioFavicon.png"), QIcon.Mode.Normal, QIcon.State.Off)

        OpenProject.setText(QCoreApplication.translate("MainWindow", "<html><head/><body><p><img src=\":/Dark/folder-open.png\"/> <a href=\"\\&quot;\\&quot;\"><span style=\" text-decoration: underline; color:#55aaff;\">Open Project...</span></a></p></body></html>"))
        WelcomeText.setText(QCoreApplication.translate("MainWindow", "Welcome"))
        NewProject.setText(QCoreApplication.translate("MainWindow", "<html><head/><body><p><img src=\":/Dark/file-plus.png\"/> <a href=\"\\&quot;\\&quot;\"><span style=\" text-decoration: underline; color:#55aaff;\">New Project...</span></a></p></body></html>"))

        NewProject.linkActivated.connect(lambda: self.ui.actionNewFile.trigger())
        OpenProject.linkActivated.connect(lambda: self.ui.actionOpenFile.trigger())

        self.ui.workspace.addTab(Welcome, icon1, QCoreApplication.translate("MainWindow", "Welcome"))

    def reloadImages(self, imageFolder):
        if imageFolder == None:
            self.ui.resourceList.clear()
        else:
            self.ui.resourceList.clear()
            self.resourceImages.clear()
            directory = os.listdir(imageFolder)
            directory.sort()
            for filename in directory:
                file = os.path.join(imageFolder, filename)
                if os.path.isfile(file):
                    logging.debug("Creating file entry for "+os.path.basename(file))
                    item = QListWidgetItem(QIcon(file), os.path.basename(file))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setData(0, os.path.basename(file))
                    item.setSizeHint(QSize(64, 64))
                    
                    self.resourceImages.append(os.path.basename(file))
                    self.ui.resourceList.addItem(item)

    def setupWorkspace(self):
        def handleTabClose(index):
            # Fires when tab closes
            def delProjectItem(index):
                if self.ui.workspace.tabToolTip(index) != "":
                    self.projects.pop(self.ui.workspace.tabToolTip(index))
                else:
                    self.projects.pop(self.ui.workspace.tabText(index))

            project = self.ui.workspace.tabToolTip(index)

            if project == "":
                self.ui.workspace.removeTab(index)
                self.fileChanged = False
                return

            if self.projects.get(project) and self.projects[project]["hasFileChanged"]:
                reply = self.showDialog("warning", "This tab has unsaved changes. Save and close?", "", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)

                if reply == QMessageBox.StandardButton.Yes:
                    self.saveProjects("current")
                elif reply == QMessageBox.StandardButton.Cancel:
                    return

            delProjectItem(index)
            self.ui.workspace.removeTab(index)
            self.fileChanged = False

        def handleTabChange(index):
            # Fires when tab changes
            tabName = self.ui.workspace.tabText(index)
            currentProject = self.getCurrentProject()
            self.setWindowTitle(tabName+" - Mi Create")
            if currentProject == None or tabName == "Project XML":
                self.clearExplorer()
                self.updateProperties(False)
                self.reloadImages(None)
                return
            
            if currentProject.get("canvas") != None:
                self.selectionDebounce = False
                self.Explorer.updateExplorer(currentProject["data"])
                logging.debug("Explorer updated") 
                thread = threading.Thread(target=lambda: self.reloadImages(currentProject["imageFolder"]))
                thread.start()
            else:
                self.clearExplorer()
                self.updateProperties(False)
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
                if ((supportedActions & Qt.DropAction.CopyAction) and (self.ui.resourceList.dragDropMode() != QAbstractItemView.DragDropMode.InternalMove)):
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

        def addResource():
            currentProject = self.getCurrentProject()
            
            if currentProject == None or not currentProject.get("imageFolder"):
                return
            
            files = QFileDialog.getOpenFileNames(self, _("Add Image..."), "%userprofile%\\", "Image File (*.png *.jpeg *.jpg)")

            if not files[0]:
                return
            
            for file in files[0]:
                shutil.copyfile(file, os.path.join(currentProject["imageFolder"], os.path.basename(file)))
            self.reloadImages(currentProject["imageFolder"])

        def reloadResource():
            currentProject = self.getCurrentProject()

            if currentProject == None or not currentProject.get("imageFolder"):
                return
            
            self.reloadImages(currentProject["imageFolder"])

        def openResourceFolder():
            currentProject = self.getCurrentProject()

            if currentProject == None or not currentProject.get("imageFolder"):
                return
            
            if platform.system() == "Windows":
                path = str.replace(currentProject["imageFolder"], "/", "\\")
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", currentProject["imageFolder"]])
            else:
                subprocess.Popen(["xdg-open", currentProject["imageFolder"]])

        self.ui.resourceList.startDrag = startDrag
        self.ui.resourceSearch.textChanged.connect(search)
        self.ui.reloadResource.clicked.connect(reloadResource)
        self.ui.addResource.clicked.connect(addResource)
        self.ui.openResourceFolder.clicked.connect(openResourceFolder)

        # Connect objects in the Insert menu to actions
        self.ui.actionImage.triggered.connect(lambda: self.createWatchfaceWidget("30"))
        self.ui.actionImage_List.triggered.connect(lambda: self.createWatchfaceWidget("31"))
        self.ui.actionDigital_Number.triggered.connect(lambda: self.createWatchfaceWidget("32"))
        self.ui.actionAnalog_Display.triggered.connect(lambda: self.createWatchfaceWidget("27"))
        self.ui.actionArc_Progress.triggered.connect(lambda: self.createWatchfaceWidget("42"))

        # Connect tab changes
        self.ui.workspace.tabCloseRequested.connect(handleTabClose)
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
            if currentProject == None or not currentProject.get("data"):
                return
            currentSelected = self.Explorer.currentItem()
            currentItem = None
            currentProject["hasFileChanged"] = True
            self.fileChanged = True

            if "*" not in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(), self.ui.workspace.tabText(self.ui.workspace.currentIndex())+"*")

            logging.debug(f"Set property {args[0]}, {args[1]} for widget {currentSelected.data(0,101)}")
            # search for item by name, and if available set as currentItem
            currentItem = currentProject["data"]["FaceProject"]["Screen"]["Widget"][currentSelected.data(0,101)]

            def updateProperty(widgetName, property, value):
                if property == "@Value_Src" or property == "@Index_Src" or property == "@Visible_Src":
                    if value == "None":
                        currentItem[property] = 0
                    else:
                        for data in self.watchData.modelSourceData[str(currentProject["data"]["FaceProject"]["@DeviceType"])]:
                            if data["@Name"] == value:
                                try:
                                    currentItem[property] = int(data["@ID"], 0)
                                except:
                                    currentItem[property] = int(data["@ID"])
                                break
                        else:
                            self.showDialog("warning", "Invalid source name!")
                            return
                elif property == "@Alignment":
                    alignmentList = ["Left", "Center", "Right"]
                    currentItem[property] = str(alignmentList.index(value))
                elif property == "@Name":
                    if value == widgetName:
                        return
                    elif currentProject["canvas"].getObject(value):
                        self.showDialog("info", "Another widget has this name! Please change it to something else.")
                        return
                    else:
                        # need to do this hack, otherwise order gets messed up
                        # i really need to stop using xmltodict, but its too engrained into the code
                        # that it becomes too hard to replace without breaking the hell out of everything
                        self.fprjProject.formatToList(currentProject["data"]["FaceProject"]["Screen"]["Widget"])
                        currentProject["data"]["FaceProject"]["Screen"]["Widget"][value] = currentItem
                        del currentProject["data"]["FaceProject"]["Screen"]["Widget"][currentItem[property]]
                        currentItem[property] = value
                elif isinstance(value, bool):
                    if value == True:
                        value = "1"
                    else:
                        value = "0"
                    currentItem[property] = value
                else:
                    currentItem[property] = value

                if property == "@Name":
                    self.propertiesWidget.clearOnRefresh = False
                    self.Explorer.updateExplorer(currentProject["data"])
                    currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
                    currentProject["canvas"].selectObject(value)
                else:
                    self.propertiesWidget.clearOnRefresh = False
                    currentProject["canvas"].reloadObject(widgetName, currentItem, currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
                    currentProject["canvas"].selectObject(widgetName)

            if self.ignoreHistoryInvoke:
                self.ignoreHistoryInvoke = False
                updateProperty(currentSelected.data(0,101), args[0], args[1])
            else:   
                if not currentItem.get(args[0]):
                    currentItem[args[0]] = ""
                command = CommandModifyProperty(currentItem["@Name"], args[0], currentItem[args[0]], args[1], updateProperty, f"Change property {args[0]} to {args[1]}")
                self.History.undoStack.push(command)
                self.ignoreHistoryInvoke = False
            
        # Setup properties widget
        with open("data/properties.json", encoding="utf8") as raw:
            propertiesSource = raw.read()
            self.propertyJson = json.loads(propertiesSource)
            self.propertiesWidget = PropertiesWidget(self, self.watchData.modelSourceList, self.watchData.modelSourceData)
            self.propertiesWidget.propertyChanged.connect(lambda *args: setProperty(args))
            self.ui.propertiesWidget.setWidget(self.propertiesWidget)

    def updateProperties(self, item, itemType=None):
        currentProject = self.getCurrentProject()
        if item and currentProject["data"]["FaceProject"]["Screen"]["Widget"].get(item) != None:
            if self.propertiesWidget.clearOnRefresh:
                self.propertiesWidget.loadProperties(self.propertyJson[itemType], currentProject["data"]["FaceProject"]["Screen"]["Widget"][item], self.resourceImages, currentProject["data"]["FaceProject"]["@DeviceType"])
            else:
                self.propertiesWidget.clearOnRefresh = True
        else:
            if self.propertiesWidget.clearOnRefresh:
                self.propertiesWidget.clearProperties()

    def updateObjectProperty(self, name, property, value):
        currentProject = self.getCurrentProject()
        for index, object in enumerate(currentProject["data"]["FaceProject"]["Screen"]["Widget"]):
            if object["@Name"] == name:
                object[property] = value
                break
        self.propertiesWidget.propertyItems[property].setText(value)

    def setupScaffold(self):
        with open("data/default/defaultItems.json", encoding="utf8") as raw:
            self.defaultSource = raw.read()
        self.defaultScaffold = json.loads(self.defaultSource)

    def setupNewProjectDialog(self):
        def check():
            if self.newProjectUi.projectName.text() != "":
                if self.newProjectUi.folderLocation.text() != "":
                    self.newProjectUi.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                else:
                    self.newProjectUi.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            else:
                self.newProjectUi.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        def openFolderDialog():
            location = QFileDialog.getExistingDirectory(self, _('Select Folder...'), "")
            self.newProjectUi.folderLocation.setText(str(location))

        check()
        self.newProjectUi.deviceSelection.addItems(self.watchData.models)
        self.newProjectUi.projectName.textChanged.connect(check)
        self.newProjectUi.folderLocation.textChanged.connect(check)
        self.newProjectUi.folderShow.clicked.connect(openFolderDialog)

    def changeSelectionInExplorer(self, name):
        if isinstance(name, str):
            self.Explorer.items[name].setSelected(True)
        elif isinstance(name, list):
            for item in name:
                index = self.Explorer.indexFromItem(self.Explorer.items[item.data(0)])
                self.Explorer.items[name].setSelected(True)

    def createWatchfaceWidget(self, id):
        count = 0
        currentProject = self.getCurrentProject()

        if not currentProject.get("data"):
            return
        
        if not currentProject["data"]["FaceProject"]["Screen"].get("Widget"):
            currentProject["data"]["FaceProject"]["Screen"]["Widget"] = {}

        for key in currentProject["data"]["FaceProject"]["Screen"]["Widget"]:
            if "widget-" in key:
                count += 1

        defaultScaffold = json.loads(self.defaultSource)
        widgetData = defaultScaffold[id]
        widgetData["@Name"] = "widget-" + str(count)
        widgetData["@X"] = int(currentProject["canvas"].scene().sceneRect().width()/2 - int(widgetData["@Width"])/2)
        widgetData["@Y"] = int(currentProject["canvas"].scene().sceneRect().height()/2 - int(widgetData["@Height"])/2)
        self.Explorer.updateExplorer(currentProject["data"])
        if self.ignoreHistoryInvoke:
            self.ignoreHistoryInvoke = False
        else:
            def commandFunc(type, key, object=None):
                if type == "undo":
                    currentProject["data"]["FaceProject"]["Screen"]["Widget"].pop(key)   
                elif type == "redo":
                    print(currentProject["data"]["FaceProject"]["Screen"]["Widget"])
                    currentProject["data"]["FaceProject"]["Screen"]["Widget"][key] = object
                currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
                self.Explorer.updateExplorer(currentProject["data"])

            command = CommandAddWidget(widgetData["@Name"], widgetData, commandFunc, f"Add object {widgetData['@Name']}")
            self.History.undoStack.push(command)
        currentProject["canvas"].selectObject(widgetData["@Name"])

    def changeSelectedWatchfaceWidgetLayer(self, changeType):
        currentProject = self.getCurrentProject()
        currentCanvasSelected = []

        if currentProject == None or not currentProject.get("canvas"):
            return

        for item in currentProject["canvas"].getSelectedObjects():
            currentCanvasSelected.append(item.data(0))

        if currentCanvasSelected == []:
            return

        prevData = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
        newData = prevData.copy()

        newData = self.fprjProject.formatToList(newData)

        for index, obj in enumerate(self.fprjProject.formatToList(prevData)):
            print(obj["@Name"], currentCanvasSelected)
            if obj["@Name"] in currentCanvasSelected:
                newData.pop(newData.index(obj))
                if changeType == "raise" and index + 1 < len(prevData):
                    newData.insert(index + 1, obj)
                elif changeType == "lower" and index - 1 >= 0:
                    newData.insert(index - 1, obj)
                elif changeType == "top":
                    newData.append(obj)
                elif changeType == "bottom":
                    newData.insert(0, obj)

        newData = self.fprjProject.formatToKeys(newData)

        def commandFunc(data):
            projectWidgets = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
            currentProject["data"]["FaceProject"]["Screen"]["Widget"] = data
            currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
            self.Explorer.updateExplorer(currentProject["data"])

        command = CommandModifyProjectData(prevData, newData, commandFunc, f"Change object/s order through ModifyProjectData command")
        self.History.undoStack.push(command)

    def deleteSelectedWatchfaceWidgets(self):
        currentProject = self.getCurrentProject()
        if not currentProject.get("canvas"):
            return

        prevData = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
        newData = prevData.copy()

        for item in currentProject["canvas"].getSelectedObjects():
            newData.pop(item.data(0))

        if self.ignoreHistoryInvoke:
            self.ignoreHistoryInvoke = False
        else:
            def commandFunc(data):
                currentProject["data"]["FaceProject"]["Screen"]["Widget"] = data
                currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
                self.Explorer.updateExplorer(currentProject["data"])

            command = CommandModifyProjectData(prevData, newData, commandFunc, f"Delete objects through ModifyProjectData command")
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
            self.clipboard.append(currentProject["data"]["FaceProject"]["Screen"]["Widget"][object.data(0)])

    def pasteWatchfaceWidgets(self):
        currentProject = self.getCurrentProject()

        if not currentProject.get("data") or self.clipboard == []:
            return

        for item in self.clipboard:
            prevData = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
            newData = prevData.copy()
            count = 0

            for key in currentProject["data"]["FaceProject"]["Screen"]["Widget"]:
                if item["@Name"] in key:
                     count += 1

            modifiedItem = item.copy()

            if count > 0:
                name_suffix = ' - Copy'
                index = 1

                modifiedItem["@Name"] = f"{item['@Name']}{name_suffix}{count}"

            newData[modifiedItem["@Name"]] = modifiedItem

            def commandFunc(data):
                currentProject["data"]["FaceProject"]["Screen"]["Widget"] = data
                currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
                self.Explorer.updateExplorer(currentProject["data"])
                currentProject["canvas"].selectObject(modifiedItem["@Name"])

            command = CommandModifyProjectData(prevData, newData, commandFunc, f"Paste objects through ModifyProjectData command")
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
                self.updateProperties(currentCanvasSelected[0], self.Explorer.items[currentCanvasSelected[0]].data(0, 100))
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
                self.updateProperties(currentExplorerSelected[0], self.Explorer.items[currentExplorerSelected[0]].data(0, 100))
            else:
                self.updateProperties(False)

            self.selectionDebounce = False

    def createNewWorkspace(self, directory, xmlPath, data, imagePath):
        # projects are technically "tabs"
        self.previousSelected = None
        if self.projects.get(directory):
            self.ui.workspace.setCurrentIndex(self.ui.workspace.indexOf(self.projects[directory]['canvas']))
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
                widget = currentProject["data"]["FaceProject"]["Screen"]["Widget"][object.data(0)]
                
                if int(widget["@X"]) == round(object.pos().x()) and int(widget["@Y"]) == round(object.pos().y()):
                    return
                
                prevPosObject = {
                    "Name": widget["@Name"],
                    "X": widget["@X"],
                    "Y": widget["@Y"]
                }
                currentPosObject = {
                    "Name": object.data(0),
                    "X": round(object.pos().x()),
                    "Y": round(object.pos().y())
                }
                prevPos.append(prevPosObject)
                currentPos.append(currentPosObject)
            
            if "*" not in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(), self.ui.workspace.tabText(self.ui.workspace.currentIndex())+"*")
                self.fileChanged = True
                currentProject["hasFileChanged"] = True

            def commandFunc(objects):
                widgetList = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
                for object in objects:
                    widgetList[object["Name"]]["@X"] = int(object["X"])
                    widgetList[object["Name"]]["@Y"] = int(object["Y"])
                currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Interpolation"]["value"])
                currentProject["canvas"].selectObjectsFromPropertyList(objects)

            command = CommandModifyPosition(prevPos, currentPos, commandFunc, f"Change object pos")
            self.History.undoStack.push(command)

        # Setup Project
        self.projectXML = xml
        self.Explorer.clear()
            
        # Create a Canvas (QGraphicsScene & QGraphicsView)
        canvas = Canvas(data["FaceProject"]["@DeviceType"], self.settings["Canvas"]["Antialiasing"]["value"], self.settings["Canvas"]["ClipDeviceShape"]["value"], self.ui, self)

        # Create the project
        canvas.setAcceptDrops(True)
        canvas.scene().selectionChanged.connect(lambda: self.updateProjectSelections("canvas"))
        canvas.onObjectChange.connect(propertyChange)
        canvas.onObjectPosChange.connect(posChange)

        # Add Icons
        icon = QIcon(":/Dark/folder-clock.png")

        success = True

        # Render objects onto the canvas
        if data is not False:
            success = canvas.loadObjects(data, imagePath, self.settings["Canvas"]["Interpolation"]["value"])
            
        if success[0]:
            self.projects[directory] = {
                "type": "workspace",
                "canvas": canvas, 
                "data": data, 
                "directory": directory,
                "path": xmlPath,
                "imageFolder": imagePath, 
                "hasFileChanged": False
            }

            widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(canvas)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)
            widget.setLayout(layout)

            if data["FaceProject"]["Screen"]["@Title"] == "":
                name = os.path.basename(xmlPath)
            else:
                name = data["FaceProject"]["Screen"]["@Title"]

            index = self.ui.workspace.addTab(widget, icon, name)
            self.ui.workspace.setTabToolTip(index, directory)
            self.ui.workspace.setCurrentIndex(index)
            canvas.setFrameShape(QFrame.Shape.NoFrame)
        else:
            self.showDialog("error", "Cannot render project!" + success[1], success[1])

    def createNewCodespace(self, name, path, text, language):
        # Creates a new instance of QScintilla in a Codespace (code workspace)
        def textChanged():
            self.fileChanged = True
            if "*" not in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(), self.ui.workspace.tabText(self.ui.workspace.currentIndex())+"*")

        widget = QWidget()
        editor = Editor(widget, self.palette(), language)
        editor.setText(text)
        editor.textChanged.connect(textChanged)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
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
        # Connect menu actions

        # file
        self.ui.actionNewFile.triggered.connect(self.newProject)
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
        self.ui.actionZoom_In.triggered.connect(lambda: self.zoomCanvas("in"))
        self.ui.actionZoom_Out.triggered.connect(lambda: self.zoomCanvas("out"))
        self.ui.actionFull_Screen.triggered.connect(self.toggleFullscreen)

        # compile
        self.ui.actionBuild.triggered.connect(lambda: self.compileProject(0))
        self.ui.actionUnpack.triggered.connect(self.decompileProject)

        # help
        self.ui.actionDocumentation.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://ooflet.github.io/docs", QUrl.ParsingMode.TolerantMode)))
        self.ui.actionAbout_MiFaceStudio.triggered.connect(self.showAboutWindow)
        self.ui.actionAbout_Qt.triggered.connect(lambda: QMessageBox.aboutQt(self))
        self.ui.actionThirdPartyNotice.triggered.connect(self.showThirdPartyNotices)

        # settings
        self.settingsButtonBox.accepted.connect(lambda: self.saveSettings(True))

    def clearWindowState(self):
        reply = QMessageBox.question(self, 'Confirm Clear', _("Are you sure you want to reset all dock widget positions?"), QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            settings = QSettings("Mi Create", "Workspace")
            settings.setValue("geometry", None)
            settings.setValue("state", None)
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) 

    def newProject(self):
        self.newProjectDialogAccepted = False

        def accept():
            self.newProjectDialogAccepted = True

        self.newProjectDialog.accepted.connect(accept)

        # Get where to save the project
        self.newProjectDialog.exec()
        
        if self.newProjectDialogAccepted:
            # Get file location from dialog
            file = self.newProjectUi.folderLocation.text()
            projectName = self.newProjectUi.projectName.text()
            watchModel = self.newProjectUi.deviceSelection.currentText()

            # Clear dialog text
            self.newProjectUi.folderLocation.setText("")
            self.newProjectUi.projectName.setText("")
            
            file_extension = QFileInfo(file).suffix()
            isFprj = False

            # Check if file was selected
            if file:
                accepted = True
                if file[0] != "C" and file[0] != "/":
                    reply = QMessageBox.question(self, 'Confirm Path', _("Are you sure you want to create your project in the directory of this program?"), QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        accepted = True
                    else:
                        accepted = False

                if accepted:
                    newProject = self.fprjProject.create(file, self.watchData.modelID[str(watchModel)], projectName)
                    if newProject[0]:
                        project = self.fprjProject.load(newProject[1])
                        if project[0]:
                            try:
                                self.createNewWorkspace(os.path.dirname(newProject[1]), newProject[1], project[1], project[2])    
                            except Exception as e:
                                self.showDialog("error", _("Failed to createNewWorkspace: ") + e, traceback.format_exc())
                        else:
                            print(project[1], project[2])
                            self.showDialog("error", _('Cannot open project: ')+{project[1]}, project[2])
                    else:
                        self.showDialog("error", _("Failed to create a new project: ") + newProject[1], newProject[2])

    def openProject(self, event, file=None): 
        # Get where to open the project from
        if file == None:
            file = QFileDialog.getOpenFileName(self, _('Open Project...'), "%userprofile%/", "Watchface Project (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        # Check if file was selected
        if file[0]:
            if file_extension == "fprj":
                project = self.fprjProject.load(file[0])
                if project[0]:
                    try:
                        self.createNewWorkspace(os.path.dirname(file[0]), file[0], project[1], project[2])    
                    except Exception as e:
                        self.showDialog("error", _("Failed to open project: ") + str(e), traceback.format_exc())
                else:
                    self.showDialog("error", _('Cannot open project: ') + project[1], project[2])

    def saveProjects(self, projectsToSave):
        if projectsToSave == "all":
            for index, project in enumerate(self.projects.items()):
                project = project[1]
                if project["hasFileChanged"]:
                    if not project.get("data"):
                        return
                    success, message = self.fprjProject.save(project["path"], project["data"])
                    if not success:
                        self.showDialog("error", _("Failed to save project: ")+str(message))
                        
        elif projectsToSave == "current":
            currentIndex = self.ui.workspace.currentIndex()
            currentProject = self.getCurrentProject()

            if currentProject.get("data"):
                success, message = self.fprjProject.save(currentProject["path"], currentProject["data"])
                if success:
                    self.statusBar().showMessage(_("Project saved at ")+currentProject["path"], 2000)
                    self.fileChanged = False
                    currentProject["hasFileChanged"] = False
                else:
                    self.statusBar().showMessage(_("Failed to save: ")+str(message), 10000)
                    self.showDialog("error", _("Failed to save project: ")+str(message))
            elif currentProject.get("editor"):
                try:
                    with open(currentProject["path"], "w", encoding="utf8") as file:
                        file.write(currentProject["editor"].text())
                    self.statusBar().showMessage(_("Project saved at ")+currentProject["path"], 2000)
                except Exception as e:
                    self.statusBar().showMessage(_("Failed to save: ")+str(e), 10000)
                    self.showDialog("error", _("Failed to save project: ")+str(e))

            if "*" in self.ui.workspace.tabText(self.ui.workspace.currentIndex()):
                self.ui.workspace.setTabText(self.ui.workspace.currentIndex(), self.ui.workspace.tabText(self.ui.workspace.currentIndex()).replace("*", ""))

    
    def compileProject(self, stage):
        if not self.getCurrentProject().get("data"):
            return

        if stage == 0:
            currentProject = self.getCurrentProject()

            self.currentCompileState = 0

            self.compileUi.buttonBox.clear()

            self.compileUi.buttonBox.addButton("Next", QDialogButtonBox.ButtonRole.AcceptRole)
            self.compileUi.buttonBox.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)

            self.compileUi.watchfaceName.setText(currentProject["data"]["FaceProject"]["Screen"]["@Title"])
            self.compileUi.thumbnailLocation.addItems(self.resourceImages)
            self.compileUi.thumbnailLocation.setCurrentText(currentProject["data"]["FaceProject"]["Screen"]["@Bitmap"])

            self.compileDialog.setModal(True)
            self.compileDialog.show()
            self.compileUi.stackedWidget.setCurrentIndex(0)
        elif stage == 1:
            if self.currentCompileState == 0:
                currentProject = self.getCurrentProject()
                currentProject["data"]["FaceProject"]["Screen"]["@Title"] = self.compileUi.watchfaceName.text()
                currentProject["data"]["FaceProject"]["Screen"]["@Bitmap"] = self.compileUi.thumbnailLocation.currentText()

                reply = self.showDialog("question", _("Save project to file before building?"), "", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard, QMessageBox.StandardButton.Save)
                if reply == QMessageBox.StandardButton.Save:
                    self.saveProjects("current")

                compileDirectory = os.path.join(os.path.dirname(currentProject["path"]), "output")
                self.compileUi.stackedWidget.setCurrentIndex(2)

                self.compileUi.buttonBox.clear()
                self.compileUi.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
                self.compileUi.buttonBox.setDisabled(True)
                self.compileUi.textEdit.setReadOnly(True)
                self.compileUi.textEdit.clear()

                def append(text):
                    # append to output without a redundant newline
                    self.compileUi.textEdit.setText(self.compileUi.textEdit.toPlainText()+text)

                def error():
                    append(f"Internal error occured: {process.errorString()}")
                    self.compileUi.buttonBox.setDisabled(False)

                formattedDir = compileDirectory.replace("\\", "/")
                append(f"Please read https://ooflet.github.io/docs/quickstart/testing to see how you can test your project\n\n")
                process = self.fprjProject.compile(currentProject["path"], compileDirectory, "compiler/compile.exe")
                process.readyReadStandardOutput.connect(lambda: append(bytearray(process.readAll()).decode("utf-8")))
                process.finished.connect(lambda: self.compileUi.buttonBox.setDisabled(False))
                process.errorOccurred.connect(error)
                
                self.currentCompileState = 1

            elif self.currentCompileState == 1:
                self.compileDialog.close()


    def decompileProject(self):
        self.showDialog("error", "Will add later, apologies.")
        # self.showDialog("warning", "Please note that images may be glitched when unpacking.")
        # file = QFileDialog.getOpenFileName(self, 'Unpack File...', "%userprofile%/", "Compiled Watchface Binaries (*.face)")

        # subprocess.run(f'{currentDir}/compiler/unpack.exe  "{file[0]}"')
        # self.showDialog("info", "Decompile success! Would you like to open")

    def editProjectXML(self):
        currentProject = self.getCurrentProject()
        pprint(currentProject.get("data"))

        if not currentProject.get("data"):
            return
        
        data = deepcopy(currentProject["data"])
        data["FaceProject"]["Screen"]["Widget"] = self.fprjProject.formatToList(data["FaceProject"]["Screen"]["Widget"])

        pprint(currentProject.get("data"))

        raw = xmltodict.unparse(data)
        dom = xml.dom.minidom.parseString(raw)
        pretty_xml = dom.toprettyxml()
        if self.projects.get(currentProject["path"]):
            self.ui.workspace.setCurrentIndex(self.ui.workspace.indexOf(self.projects[currentProject["path"]]["editor"]))
            return
        self.createNewCodespace("Project XML", currentProject["path"], pretty_xml, XMLLexer)

    def showColorDialog(self):
        color = QColorDialog.getColor(Qt.white, self, "Select Color")

    def showFontSelect(self):
        font = QFontDialog.getFont(self, "Select Font")

    def showSettings(self):
        self.settingsWidget.loadProperties(self.settings)
        self.settingsDialog.exec()

    def showAboutWindow(self):
        dialog = QMessageBox(self)
        dialog.setText(f'<html><head/><body><p>Mi Create {currentVersion}<br/><a href="https://github.com/ooflet/Mi-Create/"><span style=" text-decoration: underline; color:#55aaff;">https://github.com/ooflet/Mi-Create/</span></a></p><p>tostr 2024</p></body></html>')
        dialog.setIconPixmap(QPixmap(":/Images/MiCreate48x48.png"))
        dialog.setWindowTitle("About Mi Create")
        dialog.exec()

    def showThirdPartyNotices(self):
        dialog = QMessageBox(self)
        dialog.setText('<html><head/><body><p><span style=" text-decoration: underline;">Third Party Notices</span></p><p><a href="https://www.riverbankcomputing.com/software/pyqt/"><span style=" text-decoration: underline; color:#55aaff;"> Qt6 + PyQt6</span></a> - Under GPLv3 License<br/><a href="https://lucide.dev"><span style=" text-decoration: underline; color:#55aaff;">Lucide Icons</span></a> - Under MIT License<br/>m0tral\'s Compiler - Under explicit permission</p></body></html>')
        dialog.setWindowTitle("Third Party Notices")
        dialog.exec()

    def showDialog(self, type, text, detailedText="", buttons=None, defaultButton=None):
        MessageBox = QMessageBox(self)
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
            logging.error("Detailed output: "+detailedText)
            logging.error(f"Error dump: \nprojects: {pformat(self.projects)}\n------------------------\nsettings: {pformat(self.settings)}")
            MessageBox.setIcon(QMessageBox.Icon.Critical)
        
        if buttons != None:
            MessageBox.setStandardButtons(buttons)
            MessageBox.setDefaultButton(defaultButton)
            result = MessageBox.exec()
            return result
        else:
            MessageBox.exec()

if __name__ == "__main__":
    logging.debug("-- Starting Mi Create --")

    app = QApplication(sys.argv)

    pixmap = QPixmap(":/Images/MiCreateSplash.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    if sys.argv[1:] == ["--ResetSettings"]:
        QSettings("Mi Create", "Settings").clear()
        QSettings("Mi Create", "Workspace").clear()
        logging.info("Settings reset")
        time.sleep(1)

    try:
        main_window = MainWindow()
    except Exception as e:
        error_message = "Critical error during initialization: "+traceback.format_exc()
        logging.error(error_message)
        QMessageBox.critical(None, 'Error', error_message, QMessageBox.StandardButton.Ok)
        sys.exit(1)

    if sys.argv[1:] != []:
        logging.debug("Opening file from argument 1")
        main_window.openProject(None, sys.argv[1:])

    main_window.show()
    splash.finish(main_window)
    if main_window.settings["General"]["CheckUpdate"]["value"] == True:
        main_window.checkForUpdates()
    sys.exit(app.exec())
    