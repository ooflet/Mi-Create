# Mi Create
# tostr 2023-2024

# TODO
# Put documentation on code, its a dog's breakfast out in the source code

# Rewrite the quite bad tab system currently in place
# Opening multiple projects is useless
# And that allows the explorer to also display any apps placed in the project
# Plus, its more simpler for me to use

# Switch watchface render framework from QGraphicsFramework to Qt Quick

# Also, bundle in higher quality icons or use SVG versions they look very bad on Windows scale > 100%

import os
import sys
import gettext

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from PyQt6.QtWidgets import (QMainWindow, QDialog, QInputDialog, QMessageBox, QApplication, QGraphicsScene, QPushButton, 
                               QDialogButtonBox, QTreeWidgetItem, QFileDialog, QToolButton, QToolBar, QWidget, QVBoxLayout, 
                               QFrame, QColorDialog, QFontDialog, QSplashScreen, QGridLayout, QLabel, QListWidgetItem,
                               QSpacerItem, QSizePolicy, QAbstractItemView, QUndoView)
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QDrag
from PyQt6.QtCore import Qt, QSettings, QSize, QUrl, QFileInfo, QItemSelectionModel
from PyQt6.PyQtAds import CDockWidget

from pprint import pformat
import xml.dom.minidom
import configparser
import xmltodict
import threading
import logging
if "__compiled__" in globals():
    logging.basicConfig(level=logging.DEBUG, filemode="w", filename="data/app.log", format="%(asctime)s %(module)s.py:%(lineno)d %(threadName)-10s %(levelname)s %(message)s")
else:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(module)s.py:%(lineno)d %(threadName)-10s %(levelname)s %(message)s")
import json
import theme.styles as theme
import traceback

from translate import QCoreApplication
from utils.updater import Updater
from utils.project import watchData, fprjProject
from utils.history import historySystem, CommandAddWidget, CommandModifyProperty, CommandModifyPosition, CommandDeleteWidget
from utils.listviewdelegate import ResourceListDelegate
from widgets.canvas import Canvas, ObjectIcon
from widgets.explorer import Explorer
from widgets.properties import PropertiesWidget
from widgets.editor import Editor, XMLLexer

from translate import QCoreApplication

import resources.icons_rc # resource import required because it sets up the icons

from window_ui import Ui_MainWindow
from dialog.newProject_ui import Ui_Dialog as Ui_NewProject
from dialog.resourceDialog_ui import Ui_Dialog as Ui_ResourceDialog
from dialog.compileDialog_ui import Ui_Dialog as Ui_CompileDialog

_ = gettext.gettext

currentDir = os.getcwd()
currentVersion = '0.3-beta'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        print(QIcon().themeSearchPaths())

        self.fileChanged = False
        self.clipboard = None
        self.stagedChanges = []
        self.selectionDebounce = False

        # Setup Settings
        logging.debug("Loading App Settings")
        
        def close():
            self.settingsDialog.close()
            self.stagedChanges = []

        # Setup Language
        
        # Language[0] is language name
        # Language[1] is language directory
        # Language[2] is authorMessage
        # Language[3] is author contact details
        self.languages = []
        self.languageNames = []

        config = configparser.ConfigParser()
        logging.debug("Initializing Language Files")
        for file in os.listdir("locales"):
            languageDir = os.path.join("locales", file)
            if os.path.isdir(languageDir):
                logging.debug("Language directory found: "+languageDir)
                config.read_file(open(os.path.join(languageDir, "CONFIG.ini"), encoding="utf8"))
                self.languages.append([config.get('config', 'language'), languageDir, config.get('config', 'authorMessage'), config.get('config', 'contact')])
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
        self.loadSettings() 

        rawSettings = QSettings("Mi Create", "Preferences")
        if "Language" not in rawSettings.allKeys():
            item, accepted = QInputDialog().getItem(self, "Mi Create", "Select Language", self.languageNames, 0)
            if accepted and not item == "":
                self.stagedChanges.append(["Language", item])
                self.saveSettings(False)
                
        self.settingsWidget.loadProperties(self.settings)
        self.settingsWidget.propertyChanged.connect(lambda property, value: self.stagedChanges.append([property, value]))
        self.loadTheme() 

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
        self.historySystem = historySystem()
        self.ignoreHistoryInvoke = False
        self.undoLayout = QVBoxLayout()
        self.undoDialog = QDialog(self)
        self.undoView = QUndoView(self.historySystem.undoStack)
        self.undoLayout.addWidget(self.undoView)
        self.undoDialog.setLayout(self.undoLayout)
        self.undoDialog.show()
 
        # Setup Project 
        self.project = None 
        self.projectXML = None 

        # Setup Dialog 
        logging.debug("Initializing pre-compiled dialogs")
 
        # Setup New Project Dialog 
        self.newProjectDialog = QDialog(self) 
        self.newProjectUi = Ui_NewProject() 
        self.newProjectUi.setupUi(self.newProjectDialog) 
 
        # Setup Compile Project Dialog 
        def accepted():
            if self.currentCompileState == 0:
                currentProject = self.getCurrentProject()
                currentProject["data"]["FaceProject"]["Screen"]["@Title"] = self.compileUi.watchfaceName.text()
                currentProject["data"]["FaceProject"]["Screen"]["@Bitmap"] = self.compileUi.thumbnailLocation.text()

                reply = QMessageBox.question(self, 'Mi Create', _("Save project before building?"), QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.saveProjects("current")

                compileDirectory = os.path.join(os.path.dirname(currentProject["path"]), "output")

                self.compileUi.buttonBox.clear()
                self.compileUi.buttonBox.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
                self.compileUi.buttonBox.setDisabled(True)
                self.compileUi.textEdit.setReadOnly(True)
                self.compileUi.stackedWidget.setCurrentIndex(1)
                QApplication.processEvents()

                result = fprjProject.compile(currentProject["path"], compileDirectory, "compiler/compile.exe")
                self.compileUi.buttonBox.setDisabled(False)
                self.compileUi.textEdit.setText(str(result))
                self.compileUi.stackedWidget.setCurrentIndex(2)
                self.currentCompileState = 1

            elif self.currentCompileState == 1:
                self.compileDialog.close()

        self.compileDialog = QDialog(self) 
        self.compileUi = Ui_CompileDialog() 
        self.compileUi.setupUi(self.compileDialog) 
        self.compileUi.buttonBox.accepted.connect(accepted)
        self.compileUi.buttonBox.rejected.connect(lambda: self.compileDialog.close())
 
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
            logging.debug("Saving Window State")
            self.saveWindowState()
            logging.debug("Quitting")
            event.accept()

        if self.fileChanged == True: 
            quit_msg = _("You have unsaved project(s) open. Save and quit?")
            reply = QMessageBox.warning(self, 'Mi Create', quit_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Yes:
                logging.debug("Saving all unsaved projects") 
                self.saveProjects("all")
                quitWindow()
            
            elif reply == QMessageBox.StandardButton.No:
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

    def getCurrentProject(self):
        currentIndex = self.ui.workspace.currentIndex()
        currentProject = self.projects.get(self.ui.workspace.tabText(currentIndex))
        if currentProject == None:
            self.showDialogue("error", "Failed to retrieve currentProject!", f"Unable to find {self.ui.workspace.tabText(currentIndex)} in list of projects: {str(self.projects)}")
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

    def saveSettings(self, retranslate):
        settings = QSettings("Mi Create", "Preferences")
        for property, value in self.stagedChanges:
            settings.setValue(property, value)

        self.loadSettings()
        self.settingsDialog.close()
        self.loadTheme()
        if retranslate:
            self.loadLanguage(True)

    def loadSettings(self):
        settings = QSettings("Mi Create", "Preferences")
        with open("data/settings.json") as file:
            self.settings = json.load(file)
            logging.debug("settings.json loaded")
            self.settings["General"]["Theme"][3] = ["Dark", "Light"]
            self.settings["General"]["Language"][3] = self.languageNames

        for key in settings.allKeys():
            for category, properties in self.settings.items():
                for property, value in properties.items():
                    if key == property:
                        logging.debug("Property load "+property)
                        if settings.value(key) == "true":
                            value[2] = True
                        elif settings.value(key) == "false":
                            value[2] = False
                        else:
                            value[2] = settings.value(key)

    def loadLanguage(self, retranslate):
        selectedLanguage = None
        for language in self.languages:
            if language[0] == self.settings["General"]["Language"][2]:
                selectedLanguage = language
                break

        if selectedLanguage != None:
            translation = gettext.translation('main', localedir='locales', languages=[os.path.basename(selectedLanguage[1])])
            translation.install()
            global _ # fetch global _ variable
            _ = translation.gettext
            QCoreApplication.loadLanguage(os.path.basename(selectedLanguage[1]))
            self.propertiesWidget.loadLanguage(os.path.basename(selectedLanguage[1]))
            self.ui.retranslateUi(self) # function on each precompiled window/dialog
            self.compileUi.retranslateUi(self.compileDialog)
            self.newProjectUi.retranslateUi(self.newProjectDialog)
            # retranslate relies on the coreGettext script
            # coreGettext reimplements CoreApplication's translate function to rely on gettext
        else:
            self.showDialogue("error", "Current selected language not found!")

    def launchUpdater(self):
        self.closeWithoutWarning = True
        self.close()
        Updater().start()
        sys.exit()

    def checkForUpdates(self):
        # Contacts GitHub server for current version and compares installed to current version
        # I haven't bothered to make this work yet
        version = currentVersion
        if version > currentVersion:
            if version[-1] == 'u':
                self.showDialogue('info', _('An urgent update {version} was released! The app will now update.').format(version=version))
                self.launchUpdater()
            else:
                reply = QMessageBox.question(self, _('A new update has been found (v{version}). Would you like to update now?').format(version=version), QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    self.launchUpdater()


    def loadTheme(self):
        # Loads theme from settings table
        themeName = self.settings["General"]["Theme"][2]
        app = QApplication.instance()
        if themeName == "Light":
            theme.light(app)
            self.showDialogue('info', 'Icons in light theme have not been implemented yet. Sorry!')
        elif themeName == "Dark":
            theme.dark(app)

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

    def reloadImages(self, imageFolder, reset):
        if reset:
            self.ui.resourceList.clear()
        else:
            self.ui.resourceList.clear()
            for filename in os.listdir(imageFolder):
                file = os.path.join(imageFolder, filename)
                if os.path.isfile(file):
                    logging.debug("Creating file entry for "+os.path.basename(file))
                    item = QListWidgetItem(QIcon(file), os.path.basename(file))
                    item.setData(0, os.path.basename(file))
                    item.setSizeHint(QSize(64, 64))

                    self.ui.resourceList.addItem(item)

    def setupWorkspace(self):
        # Fires when tab closes
        def handleTabClose(index):
            def delWidget():
                if isinstance(currentWidget, Editor):
                    logging.debug("Editor widget found! Deleting") 
                    currentWidget.setParent(None)
                    currentWidget.close()
                    currentWidget.deleteLater()
                elif isinstance(currentWidget, QGraphicsScene):
                    logging.debug("Project viewport found! Deleting") 
                    projectData = self.projects.pop(currentTabName)
                    project = projectData[0]
                    project.setParent(None)
                    project.close()
                    project.deleteLater()
                
                self.ui.workspace.removeTab(index)
                if self.projects.get(currentTabName):
                    del self.projects[currentTabName]
                self.fileChanged = False

            currentWidget = self.ui.workspace.widget(index)
            currentTabName = self.ui.workspace.tabText(index)
            if self.projects.get(currentTabName) and self.projects[currentTabName]["hasFileChanged"]:
                reply = QMessageBox.warning(self, 'Mi Create', 'This tab has unsaved changes. Save and close?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                if reply == QMessageBox.StandardButton.Yes:
                    self.saveProjects("current")
                    delWidget()
                elif reply == QMessageBox.StandardButton.No:
                    delWidget()
            else:
                delWidget()

        # Fires when tab changes
        def handleTabChange(index):
            tabName = self.ui.workspace.tabText(index)
            self.setWindowTitle(tabName+" - Mi Create")
            if self.projects.get(tabName):
                tabData = self.projects[tabName]
                if tabData.get("canvas") != None:
                    self.Explorer.updateExplorer(tabData["data"])
                    logging.debug("Explorer updated") 
                    thread = threading.Thread(target=lambda: self.reloadImages(tabData["imageFolder"], False))
                    thread.start()
                    
                else:
                    self.clearExplorer()
                    self.updateProperties(False)
                    self.reloadImages(None, True)
            else:
                self.clearExplorer()
                self.updateProperties(False)
                self.reloadImages(None, True)
        
        # setup resourceList

        def startDrag(supportedActions):
            listsQModelIndex = self.ui.resourceList.selectedIndexes()
            if listsQModelIndex:
                dataQMimeData = self.ui.resourceList.model().mimeData(listsQModelIndex)
                if not dataQMimeData:
                    return None
                dragQDrag = QDrag(self.ui.resourceList)
                # dragQDrag.setPixmap(QtGui.QPixmap('test.jpg')) # <- For put your custom image here
                dragQDrag.setMimeData(dataQMimeData)
                defaultDropAction = Qt.DropAction.IgnoreAction
                if ((supportedActions & Qt.DropAction.CopyAction) and (self.ui.resourceList.dragDropMode() != QAbstractItemView.DragDropMode.InternalMove)):
                    defaultDropAction = Qt.DropAction.CopyAction
                dragQDrag.exec(supportedActions, defaultDropAction)

        self.ui.resourceList.startDrag = startDrag

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
        self.Explorer = Explorer(self, ObjectIcon())
        self.ui.explorerWidget.setWidget(self.Explorer)
        self.Explorer.itemSelectionChanged.connect(lambda: self.updateProjectSelections("explorer"))

    def clearExplorer(self):
        self.Explorer.clear()

    def setupProperties(self):
        def setProperty(args):
            currentProject = self.getCurrentProject()
            if not currentProject.get("data"):
                return
            currentSelected = self.Explorer.currentItem()
            currentItem = None
            currentProject["hasFileChanged"] = True
            self.fileChanged = True
            logging.debug(f"Set property {args[0]}, {args[1]} for widget {currentSelected.data(0,101)}")
            if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) == list:
                for i in currentProject["data"]["FaceProject"]["Screen"]["Widget"]:
                    if i["@Name"] == currentSelected.data(0,101):
                        currentItem = i
                        break
                else:
                    self.showDialogue("error", _("Failed to obtain currentItem"), _("No object found in widget list that has the name of currently selected graphics item: ")+str(currentProject["data"]["FaceProject"]["Screen"]["Widget"]))
            else:
                currentItem = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
        
            def updateProperty(widgetName, property, value):
                if property == "@Value_Src" or property == "@Index_Src" or property == "@Visible_Src":
                    for x in self.watchData.modelSourceData[str(currentProject["data"]["FaceProject"]["@DeviceType"])]:
                        if x["@Name"] == value:
                            try:
                                currentItem[property] = int(x["@ID"], 0)
                            except:
                                currentItem[property] = int(x["@ID"])
                else:
                    currentItem[property] = value

                if property == "@Name":
                    self.Explorer.updateExplorer(currentProject["data"])
                    currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Antialiasing"][2])
                    self.propertiesWidget.clearProperties()
                else:
                    self.propertiesWidget.clearOnRefresh = False
                    currentProject["canvas"].reloadObject(widgetName, currentItem, currentProject["imageFolder"], self.settings["Canvas"]["Antialiasing"][2])
                    currentProject["canvas"].selectObject(widgetName)

            if self.ignoreHistoryInvoke:
                self.ignoreHistoryInvoke = False
            else:   
                command = CommandModifyProperty(currentItem["@Name"], args[0], currentItem[args[0]], args[1], updateProperty, f"Change property {args[0]} to {args[1]}")
                self.historySystem.undoStack.push(command)
                self.ignoreHistoryInvoke = False
            
            updateProperty(currentSelected.data(0,101), args[0], args[1])

        # Setup properties widget
        with open("data/properties.json", encoding="utf8") as raw:
            propertiesSource = raw.read()
            self.propertyJson = json.loads(propertiesSource)
            self.propertiesWidget = PropertiesWidget(self, Ui_ResourceDialog, self.watchData.modelSourceList, self.watchData.modelSourceData, QApplication.instance().primaryScreen())
            self.propertiesWidget.propertyChanged.connect(lambda *args: setProperty(args))
            self.ui.propertiesWidget.setWidget(self.propertiesWidget)

    def updateProperties(self, item, itemType=None):
        print("update", item)
        if item:
            if self.propertiesWidget.clearOnRefresh:
                currentProject = self.getCurrentProject()
                if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) == list:
                    for index, object in enumerate(currentProject["data"]["FaceProject"]["Screen"]["Widget"]):
                        if object["@Name"] == item:
                            self.propertiesWidget.loadProperties(self.propertyJson[itemType], currentProject["data"]["FaceProject"]["Screen"]["Widget"][index], currentProject["data"]["FaceProject"]["@DeviceType"])
                            break
                    else:
                        return
                else:
                    if currentProject["data"]["FaceProject"]["Screen"]["Widget"]["@Name"] == item:
                        self.propertiesWidget.loadProperties(self.propertyJson[itemType], currentProject["data"]["FaceProject"]["Screen"]["Widget"], currentProject["data"]["FaceProject"]["@DeviceType"])        
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
        if type(name) == str:
            self.Explorer.items[name].setSelected(True)
        elif type(name) == list:
            for item in name:
                index = self.Explorer.indexFromItem(self.Explorer.items[item.data(0)])
                self.Explorer.items[name].setSelected(True)

    def createWatchfaceWidget(self, id):
        count = 0
        currentProject = self.getCurrentProject()

        if not currentProject.get("data"):
            return
        
        if not currentProject["data"]["FaceProject"]["Screen"].get("Widget"):
            currentProject["data"]["FaceProject"]["Screen"]["Widget"] = []
        elif type(currentProject["data"]["FaceProject"]["Screen"].get("Widget")) == dict:
            currentProject["data"]["FaceProject"]["Screen"]["Widget"] = [currentProject["data"]["FaceProject"]["Screen"]["Widget"]]

        for key in currentProject["data"]["FaceProject"]["Screen"]["Widget"]:
            if "widget-" in key["@Name"]:
                count += 1

        defaultScaffold = json.loads(self.defaultSource)
        widgetData = defaultScaffold[id]
        widgetData["@Name"] = "widget-" + str(count)
        widgetData["@X"] = int(currentProject["canvas"].scene.sceneRect().width()/2 - int(widgetData["@Width"])/2)
        widgetData["@Y"] = int(currentProject["canvas"].scene.sceneRect().height()/2 - int(widgetData["@Height"])/2)
        self.Explorer.updateExplorer(currentProject["data"])
        if self.ignoreHistoryInvoke:
            self.ignoreHistoryInvoke = False
        else:
            def commandFunc(type, index, object=None):
                if type == "undo":
                    currentProject["data"]["FaceProject"]["Screen"]["Widget"].pop(index)   
                elif type == "redo":
                    currentProject["data"]["FaceProject"]["Screen"]["Widget"].insert(index, object)
                currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Antialiasing"][2])
                self.Explorer.updateExplorer(currentProject["data"])

            command = CommandAddWidget(len(currentProject["data"]["FaceProject"]["Screen"]["Widget"]), widgetData, commandFunc, f"Add object {widgetData['@Name']}")
            self.historySystem.undoStack.push(command)
        currentProject["canvas"].selectObject(widgetData["@Name"])

    def copyWatchfaceWidget(self):
        currentProject = self.getCurrentProject()
        if not currentProject.get("canvas"):
            return
        
        selectedObjects = currentProject["canvas"].getSelectedObject()

        for object in selectedObjects:
            if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) == dict:
                currentProject["data"]["FaceProject"]["Screen"]["Widget"] = [currentProject["data"]["FaceProject"]["Screen"]["Widget"]]
            result = list(filter(lambda widget: widget["@Name"] == object.data(0),  currentProject["data"]["FaceProject"]["Screen"]["Widget"]))
            self.clipboard = result

    def pasteWatchfaceWidget(self):
        currentProject = self.getCurrentProject()

        if not currentProject.get("data") or self.clipboard == None:
            return

        if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) == dict:
            currentProject["data"]["FaceProject"]["Screen"]["Widget"] = [currentProject["data"]["FaceProject"]["Screen"]["Widget"]]

        item = None

        for item in self.clipboard:
            sameNameWidgets = [widget for widget in currentProject["data"]["FaceProject"]["Screen"]["Widget"] if widget["@Name"] == item["@Name"]]
            count = len(sameNameWidgets)

            modifiedItem = item.copy()

            if count > 0:
                name_suffix = ' - Copy'
                index = 1

                while any(f"{item['@Name']}{name_suffix * index}" == widget["@Name"] for widget in currentProject["data"]["FaceProject"]["Screen"]["Widget"]):
                    index += 1

                modifiedItem["@Name"] = f"{item['@Name']}{name_suffix * index}"

            currentProject["data"]["FaceProject"]["Screen"]["Widget"].append(modifiedItem)
            currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Antialiasing"][2])
            self.Explorer.updateExplorer(currentProject["data"])
            currentProject["canvas"].selectObject(modifiedItem["@Name"])

    def updateProjectSelections(self, subject):
        print(subject)
        currentProject = self.getCurrentProject()
        currentCanvasSelected = []
        currentExplorerSelected = []

        if not currentProject.get("canvas") or self.selectionDebounce:
            return

        for item in currentProject["canvas"].scene.selectedItems():
            currentCanvasSelected.append(item.data(0))
            logging.debug(currentProject["canvas"].scene.selectedItems())
            logging.debug(currentCanvasSelected)

        for item in self.Explorer.selectedItems():
            currentExplorerSelected.append(item.data(0, 101))
            logging.debug(currentExplorerSelected)

        if set(currentCanvasSelected) == set(currentExplorerSelected):
            return
        
        if subject == "canvas":
            print("no return")
            if len(currentCanvasSelected) > 1:
                print(">1")
                for item in currentCanvasSelected:
                    self.selectionDebounce = True
                    self.Explorer.items[item].setSelected(True)
                    self.selectionDebounce = False
            elif len(currentCanvasSelected) == 1:
                print("1")
                self.selectionDebounce = True
                self.Explorer.setCurrentItem(self.Explorer.items[currentCanvasSelected[0]])
                self.selectionDebounce = False
            else:
                print("none")
                self.selectionDebounce = True
                self.Explorer.setCurrentItem(None)
                self.selectionDebounce = False

            if len(currentCanvasSelected) == 1:
                self.updateProperties(currentCanvasSelected[0], self.Explorer.items[currentCanvasSelected[0]].data(0, 100))
            else:
                self.updateProperties(False)

        elif subject == "explorer":
            for item in currentExplorerSelected:
                self.selectionDebounce = True
                currentProject["canvas"].selectObject(currentExplorerSelected[0])
                self.selectionDebounce = False

            if currentExplorerSelected == [] or currentExplorerSelected[0] == None:
                return

            if len(currentExplorerSelected) == 1:
                self.updateProperties(currentExplorerSelected[0], self.Explorer.items[currentExplorerSelected[0]].data(0, 100))
            else:
                self.updateProperties(False)

        logging.debug(f"currentCanvasSelected: {currentCanvasSelected} | currentExplorerSelected: {currentExplorerSelected} isSame: {set(currentCanvasSelected) == set(currentExplorerSelected)}")

    def createNewWorkspace(self, name, path, data, imagePath):
        # projects are technically "tabs"
        self.previousSelected = None
        if self.projects.get(name):
            self.ui.workspace.setCurrentIndex(self.ui.workspace.indexOf(self.projects[name]['canvas']))
            return

        def objectDeleted():
            currentProject = self.getCurrentProject()
            currentObject = None
            indexList = []

            if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) == list:
                for item in currentProject["canvas"].getSelectedObject():
                    result = list(filter(lambda widget: widget["@Name"] == item.data(0), currentProject["data"]["FaceProject"]["Screen"]["Widget"]))
                    currentObject = result
                    for item in result:
                        indexList.append(currentProject["data"]["FaceProject"]["Screen"]["Widget"].index(item))

            if self.ignoreHistoryInvoke:
                self.ignoreHistoryInvoke = False
            else:
                def commandFunc(historyType, indexes, object=None):
                    currentProjectWidget = currentProject["data"]["FaceProject"]["Screen"]["Widget"]
                    if historyType == "undo":
                        for i, item in enumerate(object):
                            if type(currentProjectWidget) == list:
                                currentProjectWidget.insert(i, item)
                            elif type(currentProjectWidget) == dict:
                                currentProjectWidget = [currentProjectWidget]
                                currentProjectWidget.insert(i, item)
                    elif historyType == "redo":
                        for index in indexes:
                            print(index)
                            currentProjectWidget.pop(index)

                    currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Antialiasing"][2])
                    self.Explorer.updateExplorer(currentProject["data"])

                indexList.sort(reverse=True)
                command = CommandDeleteWidget(indexList, currentObject, commandFunc, f"Delete objects")
                self.historySystem.undoStack.push(command)
        
        def layerChange(objectName, changeType):
            currentProject = self.getCurrentProject()
            if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) != list:
                return
            
            widgets = currentProject["data"]["FaceProject"]["Screen"]["Widget"]

            for index, obj in enumerate(widgets):
                if obj["@Name"] == objectName:
                    if changeType == "raise" and index + 1 < len(widgets):
                        widgets[index], widgets[index + 1] = widgets[index + 1], obj
                    elif changeType == "lower" and index - 1 >= 0:
                        widgets[index], widgets[index - 1] = widgets[index - 1], obj
                    elif changeType == "top":
                        widgets.append(widgets.pop(index))
                    elif changeType == "bottom":
                        widgets.insert(0, widgets.pop(index))
                    break
                
            currentProject["canvas"].loadObjects(currentProject["data"], currentProject["imageFolder"], self.settings["Canvas"]["Antialiasing"][2])
            self.Explorer.updateExplorer(currentProject["data"])

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
            selectedObjects = currentProject["canvas"].getSelectedObject()
            prevPos = []
            currentPos = []

            for object in selectedObjects:
                if type(currentProject["data"]["FaceProject"]["Screen"]["Widget"]) == dict:
                    currentProject["data"]["FaceProject"]["Screen"]["Widget"] = [currentProject["data"]["FaceProject"]["Screen"]["Widget"]]
                result = list(filter(lambda widget: widget["@Name"] == object.data(0), currentProject["data"]["FaceProject"]["Screen"]["Widget"]))
                
                if int(result[0]["@X"]) == int(object.pos().x()):
                    return
                
                prevPosObject = {
                    "Name": result[0]["@Name"],
                    "X": result[0]["@X"],
                    "Y": result[0]["@Y"]
                }
                currentPosObject = {
                    "Name": object.data(0),
                    "X": object.pos().x(),
                    "Y": object.pos().y()
                }
                prevPos.append(prevPosObject)
                currentPos.append(currentPosObject)

            def commandFunc(objects):
                if len(objects) == 1:
                    propertyFieldX = self.propertiesWidget.propertyItems.get("@X")
                    propertyFieldY = self.propertiesWidget.propertyItems.get("@Y")

                    if not propertyFieldX or not propertyFieldY:
                        return

                    propertyFieldX.setValue(int(objects[0]["X"]))
                    propertyFieldY.setValue(int(objects[0]["Y"]))
                else:
                    for object in objects:
                        result = list(filter(lambda widget: widget["@Name"] == object["Name"], currentProject["data"]["FaceProject"]["Screen"]["Widget"]))
                        result[0]["@X"] = int(object["X"])
                        result[0]["@Y"] = int(object["Y"])

            command = CommandModifyPosition(prevPos, currentPos, commandFunc, f"Change object pos")
            self.historySystem.undoStack.push(command)

        # Setup Project
        self.projectXML = xml
        self.Explorer.clear()
            
        # Create a Canvas (QGraphicsScene & QGraphicsView)
        canvas = Canvas(data["FaceProject"]["@DeviceType"], self.settings["Canvas"]["Antialiasing"][2], self.settings["Canvas"]["DeviceOutline"][2], self.ui.menuInsert)

        # Create the project
        canvas.setAcceptDrops(True)
        canvas.scene.selectionChanged.connect(lambda: self.updateProjectSelections("canvas"))
        canvas.objectChanged.connect(propertyChange)
        canvas.objectPosChanged.connect(posChange)
        canvas.objectLayerChange.connect(layerChange)
        canvas.objectDeleted.connect(objectDeleted)
        #canvas.objectAdded.connect(addObjectOnDrop)

        # Add Icons
        icon = QIcon(":/Dark/folder-clock.png")


        success = True

        # Render objects onto the canvas
        if data is not False:
            success = canvas.loadObjects(data, imagePath, self.settings["Canvas"]["Antialiasing"][2])
            
        if success[0]:
            self.projects[name] = {
                "canvas": canvas, 
                "data": data, 
                "path": path,
                "imageFolder": imagePath, 
                "hasFileChanged": False
            }

            # Setup Insert Menu
            insertButton = QToolButton()
            insertButton.setMenu(self.ui.menuInsert)
            insertButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            insertButton.setIcon(QIcon(":Dark/plus.png"))
            insertButton.setText(_("Create Widget"))
            insertButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

            # Setup AOD Switch
            # AODSwitch = QToolButton()
            # AODSwitch.setIcon(QPixmap(":Dark/moon.png"))
            # AODSwitch.setIconSize(QSize(16,16))
            # AODSwitch.setText("Toggle AOD")
            # AODSwitch.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            # AODSwitch.setCheckable(True)

            canvasToolbar = QToolBar()
            canvasToolbar.setStyleSheet("background-color: palette(base); padding-left: 20px; ")
            canvasToolbar.addWidget(insertButton)
            # canvasToolbar.addWidget(AODSwitch)

            widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(canvasToolbar)
            layout.addWidget(canvas)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)
            widget.setLayout(layout)

            index = self.ui.workspace.addTab(widget, icon, name)
            self.ui.workspace.setCurrentIndex(index)
            canvas.setFrameShape(QFrame.Shape.NoFrame)
        else:
            self.showDialogue("error", "Cannot render project!" + success[1], success[1])

    def createNewCodespace(self, name, path, text, language):
        # Creates a new instance of QScintilla in a Codespace (code workspace)

        widget = QWidget()
        editor = Editor(widget, self.palette(), language)
        editor.setText(text)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(editor)
        widget.setLayout(layout)

        icon = QIcon(":/Dark/file-code-2.png")
        index = self.ui.workspace.addTab(widget, icon, name)
        self.projects[name] = {
            "hasFileChanged": False,
            "editor": editor,
            "path": path
        }
        self.ui.workspace.setCurrentIndex(index)

    def setupWidgets(self):
        # Connect menu actions

        # file
        self.ui.actionNewFile.triggered.connect(self.newProject)
        self.ui.actionOpenFile.triggered.connect(self.openProject)
        self.ui.actionSave.triggered.connect(lambda: self.saveProjects("current"))
        self.ui.actionExit.triggered.connect(self.close)

        # edit
        self.ui.actionCopy.triggered.connect(self.copyWatchfaceWidget)
        self.ui.actionPaste.triggered.connect(self.pasteWatchfaceWidget)
        self.ui.actionUndo.triggered.connect(lambda: self.historySystem.undoStack.undo())
        self.ui.actionRedo.triggered.connect(lambda: self.historySystem.undoStack.redo())
        self.ui.actionProject_XML_File.triggered.connect(self.editProjectXML)
        self.ui.actionPreferences.triggered.connect(self.showSettings)

        # view
        self.ui.actionFull_Screen.triggered.connect(self.toggleFullscreen)

        # compile
        self.ui.actionBuild.triggered.connect(self.compileProject)
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
                    newProject = fprjProject.create(file, self.watchData.modelID[str(watchModel)], projectName)
                    if newProject[0]:
                        project = fprjProject.load(newProject[1])
                        if project[0]:
                            try:
                                self.createNewWorkspace(newProject[1], newProject[1], project[1], project[2])    
                            except Exception as e:
                                self.showDialogue("error", _("Failed to createNewWorkspace: ") + e, traceback.format_exc())
                        else:
                            self.showDialogue("error", _('Cannot open project: ')+{project[1]}, project[2])
                    else:
                        self.showDialogue("error", _("Failed to create a new project: ") + newProject[1], newProject[2])

    def openProject(self, event, file=None): 
        # Get where to open the project from
        if file == None:
            file = QFileDialog.getOpenFileName(self, _('Open Project...'), "%userprofile%/", "Watchface Project (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        # Check if file was selected
        if file[0]:
            if file_extension == "fprj":
                project = fprjProject.load(file[0])
                if project[0]:
                    try:
                        self.createNewWorkspace(file[0], file[0], project[1], project[2])    
                    except Exception as e:
                        self.showDialogue("error", _("Failed to open project: ") + str(e), traceback.format_exc())
                else:
                    self.showDialogue("error", _('Cannot open project: ') + project[1], project[2])

    def saveProjects(self, projectsToSave):
        if projectsToSave == "all":
            for index, project in enumerate(self.projects.items()):
                project = project[1]
                if project["hasFileChanged"]:
                    if not project.get("data"):
                        return
                    raw = xmltodict.unparse(project["data"])
                    dom = xml.dom.minidom.parseString(raw)
                    pretty_xml = dom.toprettyxml()
                    try:
                        with open(self.ui.workspace.tabText(index), "w", encoding="utf8") as file:
                            file.write(pretty_xml)
                        self.fileChanged = False
                        project["hasFileChanged"] = False
                    except Exception as e:
                        self.statusBar().showMessage(_("Failed to save: ")+str(e), 10000)
                        self.showDialogue("error", _("Failed to save project: ")+str(e))
        elif projectsToSave == "current":
            currentIndex = self.ui.workspace.currentIndex()
            currentName = self.ui.workspace.tabText(currentIndex)
            currentProject = self.getCurrentProject()

            if currentProject.get("data"):
                success, message = fprjProject.save(currentName, currentProject["data"])
                if success:
                    self.statusBar().showMessage(_("Project saved at ")+currentName, 2000)
                    self.fileChanged = False
                    currentProject["hasFileChanged"] = False
                else:
                    self.statusBar().showMessage(_("Failed to save: ")+str(message), 10000)
                    self.showDialogue("error", _("Failed to save project: ")+str(message))
            elif currentProject.get("editor"):
                try:
                    with open(currentProject["path"], "w", encoding="utf8") as file:
                        file.write(currentProject["editor"].text())
                    self.statusBar().showMessage(_("Project saved at ")+currentProject["path"], 2000)
                except Exception as e:
                    self.statusBar().showMessage(_("Failed to save: ")+str(e), 10000)
                    self.showDialogue("error", _("Failed to save project: ")+str(e))
    
    def compileProject(self):
        tabText = self.ui.workspace.tabText(self.ui.workspace.currentIndex())
        if not self.getCurrentProject().get("data"):
            return

        currentProject = self.getCurrentProject()

        self.currentCompileState = 0

        self.compileUi.buttonBox.clear()

        self.compileUi.buttonBox.addButton("Next", QDialogButtonBox.ButtonRole.AcceptRole)
        self.compileUi.buttonBox.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)

        self.compileUi.watchfaceName.setText(currentProject["data"]["FaceProject"]["Screen"]["@Title"])
        self.compileUi.thumbnailLocation.setText(currentProject["data"]["FaceProject"]["Screen"]["@Bitmap"])

        self.compileDialog.setModal(True)
        self.compileDialog.show()
        self.compileUi.stackedWidget.setCurrentIndex(0)

    def decompileProject(self):
        self.showDialogue("error", "Will add later, apologies.")
        # self.showDialogue("warning", "Please note that images may be glitched when unpacking.")
        # file = QFileDialog.getOpenFileName(self, 'Unpack File...', "%userprofile%/", "Compiled Watchface Binaries (*.face)")

        # subprocess.run(f'{currentDir}/compiler/unpack.exe  "{file[0]}"')
        # self.showDialogue("info", "Decompile success! Would you like to open")

    def editProjectXML(self):
        currentProject = self.getCurrentProject()

        if not currentProject.get("data"):
            return

        raw = xmltodict.unparse(currentProject["data"])
        dom = xml.dom.minidom.parseString(raw)
        pretty_xml = dom.toprettyxml()
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
        dialog.setText(f'<html><head/><body><p>Mi Create v{currentVersion}<br/><a href="https://github.com/ooflet/Mi-Create/"><span style=" text-decoration: underline; color:#55aaff;">https://github.com/ooflet/Mi-Create/</span></a></p><p>tostr 2024</p></body></html>')
        dialog.setIconPixmap(QPixmap(":/Images/MiCreate48x48.png"))
        dialog.setWindowTitle("About Mi Create")
        dialog.exec()

    def showThirdPartyNotices(self):
        dialog = QMessageBox(self)
        dialog.setText('<html><head/><body><p><span style=" text-decoration: underline;">Third Party Notices</span></p><p><a href="https://www.riverbankcomputing.com/software/pyqt/"><span style=" text-decoration: underline; color:#55aaff;"> Qt6 + PyQt6</span></a> - Under GPLv3 License<br/><a href="https://lucide.dev"><span style=" text-decoration: underline; color:#55aaff;">Lucide Icons</span></a> - Under MIT License<br/>m0tral\'s Compiler - Under explicit permission</p></body></html>')
        dialog.setWindowTitle("Third Party Notices")
        dialog.exec()

    def showDialogue(self, type, text, detailedText=""):
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
            logging.error(f"Error dump: \ncurrentProject: {pformat(self.getCurrentProject())}\n------------------------\nprojectCanvasItems: {pformat((items := self.getCurrentProject().get('canvas')) and items.scene.items())}\n------------------------\nsettings: {pformat(self.settings)}")
            MessageBox.setIcon(QMessageBox.Icon.Critical)
        MessageBox.exec()
            
if __name__ == "__main__":
    logging.debug("-- Starting Mi Create --")

    app = QApplication(sys.argv)

    # splash
    pixmap = QPixmap(":/Images/MiCreateSplash.png")
    splash = QSplashScreen(pixmap)
    splash.show()

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
    main_window.checkForUpdates()

    sys.exit(app.exec())