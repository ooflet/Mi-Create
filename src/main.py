# Mi Create
# tostr 2023

# TODO
# Rewrite the quite bad tab system currently in place
# Opening multiple projects is useless
# And that allows the explorer to also display any apps placed in the project
# Plus, its more simpler for me to use

# Make so that data files are automatically created by the program, not manually bundled in.

# Also, bundle in higher quality icons or use SVG versions they look very bad on Windows scale > 100%

# Also add in a js/lua autocomplete to monaco, will be useful for turning the app into a full fledged IDE
# But thats against trying to make the project as simple as it possibly can, would it?
# Too many features, and new users immediately overwhelmed, need to open documentation for every feature lmao

# Make application compatible with Linux/macOS

import os
import pdb
import gettext

from PySide6.QtWidgets import (QMainWindow, QDialog, QMessageBox, QApplication, QGraphicsScene, QPushButton, 
                               QDialogButtonBox, QTreeWidgetItem, QFileDialog, QToolButton, QToolBar, QWidget, QVBoxLayout, 
                               QFrame, QColorDialog, QFontDialog, QSplashScreen)
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices
from PySide6.QtCore import Qt, QSettings, QSize, QUrl, QFileInfo

from pprint import pprint
import xml.dom.minidom
import xmltodict
import threading
import logging
import subprocess
import json
import theme.styles as theme
import traceback

from updater.updater import Updater
from project.projectManager import watchData, fprjProject
from widgets.canvas import Canvas, ObjectIcon
from widgets.properties import PropertiesWidget
from monaco.monaco_widget import MonacoWidget

# resource import required because it sets up the icons even though its not called
import resources.icons_rc

from window_ui import Ui_MainWindow
from dialog.preferences_ui import Ui_Dialog as Ui_Preferences
from dialog.newProject_ui import Ui_Dialog as Ui_NewProject
from dialog.resourceDialog_ui import Ui_Dialog as Ui_ResourceDialog
from dialog.compileDialog_ui import Ui_Dialog as Ui_CompileDialog

logging.basicConfig(level=logging.DEBUG)

_ = gettext.gettext

#windll = ctypes.windll.kernel32
currentDir = os.getcwd()
currentVersion = '0.0.1-pre-alpha-2'
#currentLanguage = locale.windows_locale[windll.GetUserDefaultUILanguage()]

languages = ["English", "繁體中文", "简体中文", "Русский"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.closeWithoutWarning = False
        #self.showDialogue("info", "Thank you for beta testing! Please report any bugs using the bug report menu in the Help tab.")

        # Setup Preferences Dialog 
        self.preferencesDialog = QDialog(self) 
        self.preferences = Ui_Preferences() 
        self.preferences.setupUi(self.preferencesDialog) 
 
        # Setup New Project Dialog 
        self.newProjectDialog = QDialog(self) 
        self.newProjectUi = Ui_NewProject() 
        self.newProjectUi.setupUi(self.newProjectDialog) 
 
        # Setup Compile Project Dialog 
        self.compileDialog = QDialog(self) 
        self.compileUi = Ui_CompileDialog() 
        self.compileUi.setupUi(self.compileDialog) 
 
        # Setup Viewports (tabs) 
        self.viewports = {} 
 
        # Setup WatchData 
        self.watchData = watchData() 
 
        # Setup Project 
        self.project = None 
        self.projectXML = None 
 
        # Setup Main Window 
        self.ui = Ui_MainWindow() 
        self.ui.setupUi(self) 
        self.setupScaffold() 
        self.setupWidgets() 
        self.setupWorkspace() 
        self.setupExplorer() 
        self.setupProperties() 
        self.setupNewProjectDialog() 
        self.loadWindowState() 
        self.loadSettings() 
        self.loadTheme() 
        self.statusBar().showMessage("Ready", 3000) 

    def closeEvent(self, event): 
        if self.closeWithoutWarning == False: 
            # Ask user if they want to exit 
            quit_msg = "Are you sure you want to exit Mi Create?" 
            reply = QMessageBox.question(self, 'Mi Create', quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.saveWindowState()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def getCurrentViewport(self):
        currentIndex = self.ui.workspace.currentIndex()
        currentViewport = self.viewports[self.ui.workspace.tabText(currentIndex)]
        return currentViewport

    def saveWindowState(self):
        settings = QSettings("Mi Create", "Workspace")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())

    def loadWindowState(self):
        settings = QSettings("Mi Create", "Workspace")
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("state"))

    def saveSettings(self):
        settings = QSettings("Mi Create", "Preferences")
        settings.setValue("theme", self.preferences.themeComboBox.currentText())
        settings.setValue("language", self.preferences.languageComboBox.currentText())

    def loadSettings(self):
        settings = QSettings("Mi Create", "Preferences")
        theme = settings.value("theme", "Dark")
        language = settings.value("language", "English")
        self.preferences.themeComboBox.setCurrentText(theme)
        self.preferences.languageComboBox.setCurrentText(language)

    def launchUpdater(self):
        self.closeWithoutWarning = True
        self.close()
        Updater().start()
        sys.exit()

    def checkForUpdates(self):
        # Contacts GitHub server for current version and compares installed to current version
        version = currentVersion
        if version > currentVersion:
            if version[-1] == 'u':
                self.showDialogue('info', f'An urgent update {version} was released! The app will now update.')
                self.launchUpdater()
            else:
                reply = QMessageBox.question(self, f'A new update has been found (v{version}). Would you like to update now?', QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    self.launchUpdater()


    def loadTheme(self):
        # Loads theme from themeComboBox element. Later on will load the theme from the QSettings directly
        themeName = self.preferences.themeComboBox.currentText()
        app = QApplication.instance()
        if themeName == "Light":
            theme.light(app)
            self.showDialogue('info', 'Icons in light theme have not been implemented yet. Sorry!')
        elif themeName == "Dark":
            theme.dark(app)

    def setupWorkspace(self):
        # Fires when tab closes
        def handleTabClose(index):
            reply = QMessageBox.question(self, 'Mi Create', 'Are you sure you want to close this tab?', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                currentWidget = self.ui.workspace.widget(index)
                currentTabName = self.ui.workspace.tabText(index)

                if isinstance(currentWidget, MonacoWidget):
                    currentWidget.setParent(None)
                    currentWidget.close()
                    currentWidget.deleteLater()
                elif isinstance(currentWidget, QGraphicsScene):
                    viewportData = self.viewports.pop(currentTabName)
                    viewport = viewportData[0]
                    viewport.setParent(None)
                    viewport.close()
                    viewport.deleteLater()
                
                self.ui.workspace.removeTab(index)
                if self.viewports.get(currentTabName):
                    del self.viewports[currentTabName]

        # Fires when tab changes
        def handleTabChange(index): 
            tabName = self.ui.workspace.tabText(index)
            self.setWindowTitle(tabName+" - Mi Create")
            if self.viewports.get(tabName):
                tabData = self.viewports[tabName] 
                if tabData[0] != False:
                    self.updateExplorer(tabData[1])
                    self.propertiesWidget.imageFolder = tabData[2]
                    threading.Thread(target=self.propertiesWidget.reloadResourceImages).start()
                else:
                    self.clearExplorer()
                    self.updateProperties(False)
            else:
                self.clearExplorer()
                self.updateProperties(False)

        # setup compile dialog
        
        okButton = QPushButton()
        okButton.setText("OK")

        self.compileUi.buttonBox.addButton(okButton, QDialogButtonBox.AcceptRole)

        # Initialize Monaco WebView. This also starts the app in "OpenGL mode".
        self.monaco = MonacoWidget()
        self.ui.workspace.addTab(self.monaco, "init")

        # Connect objects in the Insert menu to actions
        self.ui.actionImage.triggered.connect(lambda: self.addObjectToCurrentCanvas("30"))
        self.ui.actionImage_List.triggered.connect(lambda: self.addObjectToCurrentCanvas("31"))
        self.ui.actionDigital_Number.triggered.connect(lambda: self.addObjectToCurrentCanvas("32"))

        # Connect links in the welcome screen to actions
        self.ui.NewProject.linkActivated.connect(lambda: self.ui.actionNewFile.trigger())
        self.ui.OpenProject.linkActivated.connect(lambda: self.ui.actionOpenFile.trigger())
        self.ui.actionNewTab.triggered.connect(lambda: self.createNewCodespace("test", "work?", "python"))

        # Connect tab changes
        self.ui.workspace.tabCloseRequested.connect(handleTabClose)
        self.ui.workspace.currentChanged.connect(handleTabChange)

    def setupExplorer(self):
        def updateExplorerSelection():
            currentIndex = self.ui.workspace.currentIndex()
            if self.viewports.get(self.ui.workspace.tabText(currentIndex)):
                selected = False
                currentViewport = self.getCurrentViewport()
                #print(currentViewport[0].getSelectedObject())
                for x in currentViewport[0].items():
                    if currentViewport[0].getSelectedObject() != []:
                        # check if current selected object is not already selected
                        if x.data(0) == currentViewport[0].getSelectedObject()[0]:
                            selected = True

                if not selected:
                    for x in self.ui.Explorer.selectedItems():
                        currentViewport[0].selectObject(x.text(0))

        self.ui.Explorer.itemSelectionChanged.connect(updateExplorerSelection)

    def clearExplorer(self):
        self.ui.Explorer.clear()

    def updateExplorer(self, data):
        def createItem(x):
            objectIcon = QIcon()
            if ObjectIcon().icon.get(x["@Shape"]):
                objectIcon.addFile(ObjectIcon().icon[x["@Shape"]], QSize(), QIcon.Normal, QIcon.Off)
                object = QTreeWidgetItem(root)
                object.setText(0, x["@Name"])
                object.setIcon(0, objectIcon)
                object.setFlags(object.flags() | Qt.ItemIsEditable)
                object.setData(0, 100, x["@Shape"])
                object.setData(0, 101, x["@Name"])
                self.explorer[x["@Name"]] = object
            else:
                self.showDialogue("error", f"Widget {x['@Shape']} not implemented in ObjectIcon(), please report as issue.")

        self.explorer = {}
        self.ui.Explorer.clear()
        self.ui.Explorer.setAnimated(True)
        icon = QIcon()
        icon.addFile(u":/Dark/watch.png", QSize(), QIcon.Normal, QIcon.Off)
        name = None
        if data["FaceProject"]["Screen"]["@Title"] == "":
            name = "Watchface"
        else:
            name = data["FaceProject"]["Screen"]["@Title"]
        root = QTreeWidgetItem(self.ui.Explorer)
        root.setText(0, name)
        root.setIcon(0, icon)
        root.setData(0, 100, "00")
        root.setFlags(root.flags() | Qt.ItemIsEditable)
        if data["FaceProject"]["Screen"].get("Widget") != None:
            if type(data["FaceProject"]["Screen"].get("Widget")) == list:
                for x in data["FaceProject"]["Screen"]["Widget"]:
                    createItem(x)      
            else:
                createItem(data["FaceProject"]["Screen"].get("Widget"))  
            
        self.ui.Explorer.expandAll()

    def setupProperties(self):
        def setProperty(args):
            print(args[0], args[1])
            currentViewport = self.getCurrentViewport()
            currentSelected = self.ui.Explorer.currentItem()
            currentItem = None
            if type(currentViewport[1]["FaceProject"]["Screen"]["Widget"]) == list:
                for i in currentViewport[1]["FaceProject"]["Screen"]["Widget"]:
                    if i["@Name"] == currentSelected.data(0,101):
                        currentItem = i
                        break
                else:
                    self.showDialogue("error", "Failed to obtain currentItem", "No object found in widget list that has the name of currently selected graphics item: "+str(currentViewport[1]["FaceProject"]["Screen"]["Widget"]))
            else:
                currentItem = currentViewport[1]["FaceProject"]["Screen"]["Widget"]

            if args[0] == "@Value_Src" or args[0] == "@Index_Src" or args[0] == "@VisibleSrc":
                for x in self.watchData.modelSourceData[str(currentViewport[1]["FaceProject"]["@DeviceType"])]:
                    if x["@Name"] == args[1]:
                        try:
                            currentItem[args[0]] = int(x["@ID"], 0)
                        except:
                            currentItem[args[0]] = int(x["@ID"])

            else:
                currentItem[args[0]] = args[1]
                currentViewport[0].setObjectProperty(currentSelected.data(0,101), args[0], args[1])

        # Setup properties widget
        with open("data\\properties.json", encoding="utf8") as raw:
            propertiesSource = raw.read()
            self.propertyJson = json.loads(propertiesSource)
            self.propertiesWidget = PropertiesWidget(self, Ui_ResourceDialog, self.watchData.modelSourceList, self.watchData.modelSourceData, QApplication.instance().primaryScreen())
            self.propertiesWidget.propertyChanged.connect(lambda *args: setProperty(args))
            self.ui.propertiesWidget.setWidget(self.propertiesWidget)

    def updateProperties(self, item):
        if item:
            currentViewport = self.getCurrentViewport()
            # data(0,100) is objectID, data(0,101) is name
            if type(currentViewport[1]["FaceProject"]["Screen"]["Widget"]) == list:
                for index, object in enumerate(currentViewport[1]["FaceProject"]["Screen"]["Widget"]):
                    if object["@Name"] == item.data(0,101):
                        self.propertiesWidget.loadProperties(self.propertyJson[item.data(0, 100)], currentViewport[1]["FaceProject"]["Screen"]["Widget"][index], currentViewport[1]["FaceProject"]["@DeviceType"])
                        break
                else:
                    self.showDialogue("error", "Error occured during property update: Object not found!", f'Unable to find {object["@Name"]}.')
            else:
                if currentViewport[1]["FaceProject"]["Screen"]["Widget"]["@Name"] == item.data(0,101):
                    self.propertiesWidget.loadProperties(self.propertyJson[item.data(0, 100)], currentViewport[1]["FaceProject"]["Screen"]["Widget"], currentViewport[1]["FaceProject"]["@DeviceType"])
        else:
            self.propertiesWidget.clearProperties() 

    def updateObjectProperty(self, name, property, value):
        currentViewport = self.getCurrentViewport()
        for index, object in enumerate(currentViewport[1]["FaceProject"]["Screen"]["Widget"]):
            if object["@Name"] == name:
                object[property] = value
                break
        self.propertiesWidget.propertyItems[property].setText(value)

    def setupScaffold(self):
        with open("data\\default\\defaultItems.json", encoding="utf8") as raw:
            self.defaultSource = raw.read()
        self.defaultScaffold = json.loads(self.defaultSource)

    def setupNewProjectDialog(self):
        def check():
            if self.newProjectUi.projectName.text() != "":
                if self.newProjectUi.folderLocation.text() != "":
                    self.newProjectUi.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                else:
                    self.newProjectUi.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            else:
                self.newProjectUi.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        def openFolderDialog():
            location = QFileDialog.getExistingDirectory(self, 'Select Folder...', "")
            self.newProjectUi.folderLocation.setText(str(location))

        check()
        self.newProjectUi.deviceSelection.addItems(self.watchData.models)
        self.newProjectUi.projectName.textChanged.connect(check)
        self.newProjectUi.folderLocation.textChanged.connect(check)
        self.newProjectUi.folderShow.clicked.connect(openFolderDialog)

    def changeSelectionInExplorer(self, name):
        self.ui.Explorer.setCurrentItem(self.explorer[name])

    def addObjectToCurrentCanvas(self, id):
        count = 0
        currentViewport = self.getCurrentViewport()
        widgetData = self.defaultScaffold[id]
        if not currentViewport[1]["FaceProject"]["Screen"].get("Widget"):
            currentViewport[1]["FaceProject"]["Screen"]["Widget"] = []
        elif type(currentViewport[1]["FaceProject"]["Screen"].get("Widget")) == dict:
            currentViewport[1]["FaceProject"]["Screen"]["Widget"] = [currentViewport[1]["FaceProject"]["Screen"]["Widget"]]
        for key in currentViewport[1]["FaceProject"]["Screen"]["Widget"]:
            if "widget-" in key["@Name"]:
                count += 1
        widgetData["@Name"] = "widget-" + str(count)
        widgetData["@X"] = int(currentViewport[0].scene.sceneRect().width()/2 - int(widgetData["@Width"])/2)
        widgetData["@Y"] = int(currentViewport[0].scene.sceneRect().height()/2 - int(widgetData["@Height"])/2)
        currentViewport[1]["FaceProject"]["Screen"]["Widget"].append(widgetData) 
        currentViewport[0].loadObjectsFromData(currentViewport[1], currentViewport[2], self.preferences.AntialiasingEnabled.isChecked())
        self.updateExplorer(currentViewport[1])
        currentViewport[0].selectObject(widgetData["@Name"])

    def createNewWorkspace(self, name, isFprj, data, xml): 
        # data[0] is watchface data while data[1] is image data
        # Viewports are technically "tabs"
        self.previousSelected = None
        if not self.viewports.get(name):
            def selectionChange(viewport):
                if viewport.scene.selectedItems() != []:
                    for x in viewport.scene.selectedItems():
                        if self.previousSelected != viewport.scene.selectedItems():
                            self.previousSelected = viewport.scene.selectedItems()
                            #print(viewport.scene.selectedItems())
                            self.changeSelectionInExplorer(x.data(0))
                            self.updateProperties(self.explorer[x.data(0)])
                            break
                else:
                    self.previousSelected = None
                    self.ui.Explorer.currentItem().setSelected(False)
                    self.updateProperties(False)

            def objectDeleted(objectName):
                print("del")
                currentViewport = self.getCurrentViewport()
                if type(currentViewport[1]["FaceProject"]["Screen"]["Widget"]) == list:
                    for index, obj in enumerate(currentViewport[1]["FaceProject"]["Screen"]["Widget"]):
                        if obj["@Name"] == objectName:
                            currentViewport[1]["FaceProject"]["Screen"]["Widget"].pop(index)
                elif type(currentViewport[1]["FaceProject"]["Screen"]["Widget"]) == dict:
                    currentViewport[1]["FaceProject"]["Screen"]["Widget"] = []

            def propertyChange(objectName, propertyName, propertyValue):
                propertyField = self.propertiesWidget.propertyItems[propertyName]

                if isinstance(propertyValue, list):
                    propertyValue = propertyValue[0]

                if propertyField.metaObject().className() == "QSpinBox":
                    propertyField.setValue(int(propertyValue))
                else:
                    propertyField.setText(propertyValue)

            # Setup Project
            self.projectXML = xml
            self.ui.Explorer.clear()
                
            # Create a Canvas (QGraphicsScene & QGraphicsView)
            viewport = Canvas(data[0]["FaceProject"]["@DeviceType"], self.preferences.AntialiasingEnabled.isChecked(), self.preferences.DeviceOutlineVisible.isChecked(), self.ui.menuInsert)

            # Create the viewport
            viewport.setAcceptDrops(True)
            viewport.scene.selectionChanged.connect(lambda: selectionChange(viewport))
            viewport.objectChanged.connect(propertyChange)
            viewport.objectDeleted.connect(objectDeleted)
            #viewport.objectAdded.connect(addObjectOnDrop)

            # Add Icons
            if isFprj:
                icon = QPixmap(":/Dark/folder-clock.png")
            else:
                icon = QPixmap(":/Dark/file-clock.png")

            success = True

            # Render objects onto the canvas
            if data is not False:
                success = viewport.loadObjectsFromData(data[0], data[1], self.preferences.AntialiasingEnabled.isChecked())
                
            if success[0]:
                # When retreving data from viewports, keep in mind:
                # viewport[0] is the Canvas object
                # viewport[1] is the Fprj data
                # viewport[2] is the path to the image folder
                # viewport[3] contains whether the object is in the Fprj format (deprecated)
                # viewport[4] contains the xml source
                self.viewports[name] = [viewport, data[0], data[1], isFprj, xml]

                # Setup Insert Menu
                insertButton = QToolButton()
                insertButton.setMenu(self.ui.menuInsert)
                insertButton.setPopupMode(QToolButton.InstantPopup)
                insertButton.setIcon(QPixmap(":Dark/plus.png"))
                insertButton.setText("Create Widget")
                insertButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

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
                layout.addWidget(viewport)
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                widget.setLayout(layout)

                index = self.ui.workspace.addTab(widget, icon, name)
                self.ui.workspace.setCurrentIndex(index)
                viewport.setFrameShape(QFrame.NoFrame)
            else:
                self.showDialogue("error", f"Cannot render project! {success[1]}", success[1])
        else:
           self.ui.workspace.setCurrentIndex(self.ui.workspace.indexOf(self.viewports[name][0]))

    def createNewCodespace(self, name, text, language, options={"cursorSmoothCaretAnimation":"on"}):
        # Setup Insert Menu
        insertButton = QToolButton()
        insertButton.setPopupMode(QToolButton.InstantPopup)
        insertButton.setIcon(QPixmap(":Dark/save.png"))
        insertButton.setText("Save")

        # Creates a new instance of Monaco in a Codespace (code workspace)
        editor = MonacoWidget()
        editor.setText(text)
        editor.setLanguage(language)
        editor.setEditorOptions(options)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(editor)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        widget.setLayout(layout)

        icon = QPixmap(":/Dark/file-code-2.png")
        index = self.ui.workspace.addTab(widget, icon, name)
        self.ui.workspace.setCurrentIndex(index)

    def setupWidgets(self):
        # Connect menu actions

        # file
        self.ui.actionNewFile.triggered.connect(self.newProject)
        self.ui.actionOpenFile.triggered.connect(self.openProject)
        self.ui.actionSave.triggered.connect(self.saveCurrentProject)
        self.ui.actionExit.triggered.connect(self.close)

        # edit
        self.ui.actionProject_XML_File.triggered.connect(self.editProjectXML)
        self.ui.actionPreferences.triggered.connect(self.showPreferences)

        # compile
        self.ui.actionBuild.triggered.connect(self.compileProject)
        self.ui.actionUnpack.triggered.connect(self.decompileProject)

        # help
        self.ui.actionDocumentation.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://ooflet.github.io/docs", QUrl.TolerantMode)))
        self.ui.actionAbout_MiFaceStudio.triggered.connect(self.showAboutWindow)
        self.ui.actionAbout_Qt.triggered.connect(lambda: QMessageBox.aboutQt(self))
        self.ui.actionThirdPartyNotice.triggered.connect(self.showThirdPartyNotices)

        # test
        self.ui.actionshowAboutWindow.triggered.connect(self.showAboutWindow)
        self.ui.actionshowDefaultInfoDialog.triggered.connect(lambda: self.showDialogue("error", "No cause for alarm, this is a test dialogue!"))
        self.ui.actionshowColorDialog.triggered.connect(self.showColorDialog)
        self.ui.actionshowToast.triggered.connect(lambda: self.setWindowState(Qt.WindowMinimized))
        self.ui.actionshowSelectFont.triggered.connect(self.showFontSelect)
        self.ui.actionInstaller.triggered.connect(self.launchUpdater)

        # preferences
        self.preferences.clearWindow.clicked.connect(self.clearWindowState)
        self.preferences.openDataFolder.clicked.connect(lambda *event: subprocess.Popen(f'explorer /select, data"'))
        self.preferences.reinstall.clicked.connect(self.launchUpdater)
        self.preferences.buttonBox.accepted.connect(self.saveAndLoadPreferences)

    def clearWindowState(self):
        reply = QMessageBox.question(self, 'Confirm Clear', "This will clear the positions of dock widgets/windows and restart the app. Confirm?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            settings = QSettings("Mi Create", "Workspace")
            settings.setValue("geometry", None)
            settings.setValue("state", None)
            os.execl(sys.executable, sys.executable, *sys.argv)

    def saveAndLoadPreferences(self):
        self.saveSettings()
        self.loadSettings()
        self.loadTheme()

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
                    reply = QMessageBox.question(self, 'Confirm Path', "Your project will be created in the install directory of this program. Confirm?", QMessageBox.Yes, QMessageBox.No)
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
                                self.createNewWorkspace(newProject[1], True, [project[1], project[2]], project[3])    
                            except Exception as e:
                                self.showDialogue("error", f"Failed to createNewWorkspace: {e}.", traceback.format_exc())
                        else:
                            self.showDialogue("error", f'Cannot open project: {project[1]}.', project[2])
                    else:
                        self.showDialogue("error", f"Failed to create a new project: {newProject[1]}.", newProject[2])

    def openProject(self): 
        # Get where to open the project from
        file = QFileDialog.getOpenFileName(self, 'Open Project...', "%userprofile%\\", "Watchface Project (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        # Check if file was selected
        if file[0]:
            if file_extension == "fprj":
                project = fprjProject.load(file[0])
                if project[0]:
                    try:
                        self.createNewWorkspace(file[0], True, [project[1], project[2]], project[3])    
                    except Exception as e:
                        self.showDialogue("error", f"Failed to open project: {e}.", traceback.format_exc())
                else:
                    self.showDialogue("error", f'Cannot open project: {project[1]}.', project[2])

    def saveCurrentProject(self):
        currentIndex = self.ui.workspace.currentIndex()
        currentName = self.ui.workspace.tabText(currentIndex)
        currentViewport = self.getCurrentViewport()

        raw = xmltodict.unparse(currentViewport[1])
        dom = xml.dom.minidom.parseString(raw) # or xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml()

        try:
            with open(currentName, "w", encoding="utf8") as file:
                file.write(pretty_xml)
            self.statusBar().showMessage("Project saved at "+currentName, 2000)
        except Exception as e:
            self.statusBar().showMessage("Failed to save: "+str(e), 10000)
            self.showDialogue("error", "Failed to save project: "+str(e))

    def compileProject(self):
        if self.viewports.get(self.ui.workspace.tabText(self.ui.workspace.currentIndex())) and not self.ui.workspace.tabText == "Welcome":
            reply = QMessageBox.question(self, 'Mi Create', "Save project before building?", QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.saveCurrentProject()
            QApplication.processEvents()
            
            currentIndex = self.ui.workspace.currentIndex()
            currentName = self.ui.workspace.tabText(currentIndex)
            compileDirectory = os.path.join(os.path.dirname(currentName), "output")

            self.compileUi.buttonBox.setDisabled(True)
            self.compileUi.textEdit.setReadOnly(True)
            self.compileUi.stackedWidget.setCurrentIndex(1)
            self.compileDialog.setModal(True)
            self.compileDialog.show()
            QApplication.processEvents()

            result = fprjProject.compile(currentName, compileDirectory, "compiler\\compile.exe")
            self.compileUi.buttonBox.setDisabled(False)
            self.compileUi.textEdit.setText(str(result))
            self.compileUi.stackedWidget.setCurrentIndex(2)

        else:
            self.showDialogue("error", "Failed to build project: No project is open!")
        

    def decompileProject(self):
        self.showDialogue("error", "Will add later, apologies.")
        # self.showDialogue("warning", "Please note that images may be glitched when unpacking.")
        # file = QFileDialog.getOpenFileName(self, 'Unpack File...', "%userprofile%\\", "Compiled Watchface Binaries (*.face)")

        # subprocess.run(f'{currentDir}\\compiler\\unpack.exe  "{file[0]}"')
        # self.showDialogue("info", "Decompile success! Would you like to open")

    def editProjectXML(self):
        if self.viewports.get(self.ui.workspace.tabText(self.ui.workspace.currentIndex())) and not self.ui.workspace.tabText == "Welcome":
            self.createNewCodespace("Project XML", self.viewports[self.ui.workspace.tabText(self.ui.workspace.currentIndex())][4], "xml")
        else:
            self.showDialogue("error", "Failed to open project XML: No project is open!")

    def showColorDialog(self):
        color = QColorDialog.getColor(Qt.white, self, "Select Color")

    def showFontSelect(self):
        font = QFontDialog.getFont(self, "Select Font")

    def showPreferences(self):
        self.loadSettings()
        self.preferencesDialog.exec()

    def showAboutWindow(self):
        dialog = QMessageBox(self)
        dialog.setText(f'<html><head/><body><p>Mi Create v{currentVersion}<br/><a href="https://github.com/ooflet/Mi-Create/"><span style=" text-decoration: underline; color:#55aaff;">https://github.com/ooflet/Mi-Create/</span></a></p><p>made with 💖 by tostr</p></body></html>')
        dialog.setIconPixmap(QPixmap(":/Images/MiCreate48x48.png"))
        dialog.setWindowTitle("About Mi Create")
        dialog.exec()

    def showThirdPartyNotices(self):
        dialog = QMessageBox(self)
        dialog.setText('<html><head/><body><p><span style=" text-decoration: underline;">Third Party Notices</span></p><p><a href="https://lucide.dev"><span style=" text-decoration: underline; color:#55aaff;">Lucide Icons</span></a> - Under MIT License<br/><a href="https://github.com/gmarull/qtmodern/tree/master"><span style=" text-decoration: underline; color:#55aaff;">qtmodern</span></a> - Under MIT License<br/>m0tral Compiler - Under explicit permission</p></body></html>')
        dialog.setWindowTitle("Third Party Notices")
        dialog.exec()

    def showDialogue(self, type, text, detailedText=""):
        MessageBox = QMessageBox(self)
        MessageBox.setWindowTitle("Mi Create")
        MessageBox.setWindowIcon(QPixmap(":/Images/MiCreate48x48.png"))
        MessageBox.setText(text)
        MessageBox.setDetailedText(detailedText)
        if type == "info":
            MessageBox.setIcon(QMessageBox.Information)
        elif type == "question":
            MessageBox.setIcon(QMessageBox.Question)
        elif type == "warning":
            logging.warning(text)
            MessageBox.setIcon(QMessageBox.Warning)
        elif type == "error":
            logging.error(text+"\nDetailed output: "+detailedText)
            MessageBox.setIcon(QMessageBox.Critical)
        MessageBox.exec()
            
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # splash
    pixmap = QPixmap(":/Images/MiCreateSplash.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    try:
        main_window = MainWindow()
        main_window.monaco.setParent(None)
        main_window.monaco.close()
        main_window.monaco.deleteLater()
    except Exception as e:
        error_message = f"Critical error during initialization: {traceback.format_exc()}"
        logging.error(error_message)
        QMessageBox.critical(None, 'Error', error_message, QMessageBox.Ok)
        sys.exit(1)

    main_window.show()
    splash.finish(main_window)
    main_window.checkForUpdates()

    sys.exit(app.exec())