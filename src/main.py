# Mi Create
# tostr 2023

# code is still very shitty, sorry

import os
import time
import pdb

import PySide6.QtWidgets as QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from playsound import playsound
from pprint import pprint
import threading
import logging
import json
import theme.styles as theme
import traceback
import subprocess
import locale
import ctypes

from project.projectManager import watchData, mprjProject, fprjProject
from widgets.canvas import Canvas, ObjectIcon, ResizeableObject
from widgets.properties import PropertiesWidget
#from widgets.listviewdelegate import ListStyledItemDelegate
from monaco.monaco_widget import MonacoWidget

# resource import required because it sets up the icons initially
import resources.icons_rc

from window_ui import Ui_MainWindow
from dialog.preferences_ui import Ui_Dialog as Ui_Preferences
logging.basicConfig(level=logging.DEBUG)

windll = ctypes.windll.kernel32
currentDir = os.getcwd()
currentVersion = '0.0.1-pre-alpha-1'
currentLanguage = locale.windows_locale[windll.GetUserDefaultUILanguage()]

languages = ["English", "繁體中文", "简体中文", "Русский"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.closeWithoutWarning = False
        #self.showDialogue("info", "Thank you for beta testing! Please report any bugs using the bug report menu in the Help tab.")

        # Setup Preferences Dialog
        self.preferences_dialog = QDialog(self)
        self.preferences = Ui_Preferences()
        self.preferences.setupUi(self.preferences_dialog)

        # Setup Viewports (tabs)
        self.viewports = {}

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
        self.loadWindowState()
        self.loadSettings()
        self.loadTheme()
        self.statusBar().showMessage("Ready", 3000)

    def closeEvent(self, event):
        if self.closeWithoutWarning == False:
            # Ask user if they want to exit
            threading.Thread(target=playsound, args=(os.path.join(currentDir, f'data\\resource_packs\\sounds\\question.wav'),), daemon=True).start()
            quit_msg = "Are you sure you want to exit Mi Create?"
            reply = QMessageBox.question(self, 'Confirm Exit', quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.saveWindowState()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def saveWindowState(self):
        settings = QSettings("Mi Create", "Preferences")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())

    def loadWindowState(self):
        settings = QSettings("Mi Create", "Preferences")
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
        # Launches the updater script to download and run install program
        def execute_installer_script():
            installer_script = currentDir+"\\updater\\updater.py"
            subprocess.run(["python", installer_script])

        self.closeWithoutWarning = True
        self.close()
        execute_installer_script()
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
            threading.Thread(target=playsound, args=(os.path.join(currentDir, f'data\\resource_packs\\sounds\\question.wav'),), daemon=True).start()
            reply = QMessageBox.question(self, 'Message', 'Are you sure you want to close this tab?', QMessageBox.Yes, QMessageBox.No)
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
                del self.viewports[currentTabName]

        # Fires when tab changes
        def handleTabChange(index): 
            tabName = self.ui.workspace.tabText(index)
            self.setWindowTitle(tabName+" - Mi Create")
            if not tabName == "Project XML" and not tabName == "Welcome":
                tabData = self.viewports[tabName] 
                if not tabData[0] == False:
                    self.updateExplorer(tabData[1])
                else:
                    self.clearExplorer()
                    self.updateProperties(False)
            else:
                self.clearExplorer()
                self.updateProperties(False)

        # Initialize Monaco WebView. This also starts the app in "OpenGL mode".
        self.monaco = MonacoWidget()
        self.ui.workspace.addTab(self.monaco, "init")
        #self.ui.workspace.removeTab(1)

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

    def setupToolbox(self):
        with open(currentDir+"\\data\\toolbox.json", "r") as toolboxSrc:
            self.toolboxSource = json.loads(toolboxSrc.read())

    def setupExplorer(self):
        def updateExplorerSelection():
            selected = False
            currentIndex = self.ui.workspace.currentIndex()
            currentViewport = self.viewports[self.ui.workspace.tabText(currentIndex)]
            #print(currentViewport[0].getSelectedObject())
            for x in currentViewport[0].items():
                if not currentViewport[0].getSelectedObject() == []:
                    if x.data(0) == currentViewport[0].getSelectedObject()[0]:
                        selected = True

            if not selected:
                for x in self.ui.Explorer.selectedItems():
                    currentViewport[0].selectObject(x.text(0))

        self.ui.Explorer.itemSelectionChanged.connect(updateExplorerSelection)

    def clearExplorer(self):
        self.ui.Explorer.clear()

    def updateExplorer(self, data):
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
        if not data["FaceProject"]["Screen"].get("Widget") == None:
            for x in data["FaceProject"]["Screen"]["Widget"]:
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
                    self.showDialogue("error", f"Unknown shape {x['@Shape']}, please report as issue.")
        
        self.ui.Explorer.expandAll()

    def setupProperties(self):
        def setProperty(args):
            currentIndex = self.ui.workspace.currentIndex()
            currentViewport = self.viewports[self.ui.workspace.tabText(currentIndex)]
            currentSelected = self.ui.Explorer.currentItem()
            # Look for currently selected item to change properties for using a generator expression
            currentItem = next((item for item in currentViewport[1]["FaceProject"]["Screen"]["Widget"] if item["@Name"] == currentSelected.data(0,101)), None)
            currentItem[args[0]] = args[1]
            currentViewport[0].setObjectProperty(currentSelected.data(0,101), args[0], args[1])

        # Setup properties widget
        with open(currentDir+"\\data\\properties.json") as raw:
            propertiesSource = raw.read()
            self.propertyJson = json.loads(propertiesSource)
            self.propertiesWidget = PropertiesWidget()
            self.propertiesWidget.propertyChanged.connect(lambda *args: setProperty(args))
            self.ui.propertiesWidget.setWidget(self.propertiesWidget)

    def updateProperties(self, item):
        print("update properties")
        if item:
            currentIndex = self.ui.workspace.currentIndex()
            currentViewport = self.viewports[self.ui.workspace.tabText(currentIndex)]
            # data(0,100) is objectID, data(0,101) is name
            for index, object in enumerate(currentViewport[1]["FaceProject"]["Screen"]["Widget"]):
                print(index, object)
                if object["@Name"] == item.data(0,101):
                    print("object[@Name] is equal to item.data(0,101)")
                    self.propertiesWidget.loadProperties(self.propertyJson[item.data(0, 100)], currentViewport[1]["FaceProject"]["Screen"]["Widget"][index])
                    break
            else:
                self.showDialogue("error", "Error occured during property update: Object not found!", f'{object["@Name"]} =\= {item.data(0,101)}')
        else:
            self.propertiesWidget.clearProperties() 

    def setupScaffold(self):
        with open(currentDir+"\\data\\default\\default.json") as raw:
            defaultSource = raw.read()
            self.defaultScaffold = json.loads(defaultSource)

    def changeSelectionInExplorer(self, name):
        self.ui.Explorer.setCurrentItem(self.explorer[name])

    def addObjectToCurrentCanvas(self, id):
        count = 0
        currentIndex = self.ui.workspace.currentIndex()
        currentViewport = self.viewports[self.ui.workspace.tabText(currentIndex)]
        for key in currentViewport[1]["FaceProject"]["Screen"]["Widget"]:
            if "widget-" in key["@Name"]:
                try:
                    # Try to extract the numeric part of the name and update the count accordingly.
                    widget_number = int(key["@Name"].split("-")[1])
                    count = max(count, widget_number + 1)
                except ValueError:
                    pass  # Ignore non-matching names
        widgetData = self.defaultScaffold[id]
        widgetData["@Shape"] = id
        widgetData["@Name"] = "widget-" + str(count)
        widgetData["@X"] = currentViewport[0].scene.sceneRect().width()/2 - int(widgetData["@Width"])/2
        widgetData["@Y"] = currentViewport[0].scene.sceneRect().height()/2 - int(widgetData["@Height"])/2
        currentViewport[1]["FaceProject"]["Screen"]["Widget"].append(widgetData) 
        currentViewport[0].loadObjectsFromData(currentViewport[1], currentViewport[2], self.preferences.AntialiasingEnabled.isChecked())
        self.updateExplorer(currentViewport[1])
        currentViewport[0].selectObject(widgetData["@Name"])

    def createNewWorkspace(self, name, isFprj, data, xml): 
        # data[0] is watchface data while data[1] is image data
        self.previousSelected = None
        if not self.viewports.get(name):
            def selectionChange(viewport):
                if not viewport.scene.selectedItems() == []:
                    print("selectedItems not []")
                    for x in viewport.scene.selectedItems():
                        print("viewport.scene.selectedItems")
                        print(x)
                        if not self.previousSelected == viewport.scene.selectedItems():
                            print("Not previously selected")
                            self.previousSelected = viewport.scene.selectedItems()
                            #print(viewport.scene.selectedItems())
                            self.changeSelectionInExplorer(x.data(0))
                            self.updateProperties(self.explorer[x.data(0)])
                            break
                else:
                    print("selected items is []")
                    self.previousSelected = None
                    self.ui.Explorer.currentItem().setSelected(False)
                    self.updateProperties(False)

            # Setup Project
            self.projectXML = xml
            self.ui.Explorer.clear()
                
            # Create a Canvas (QGraphicsScene & QGraphicsView)
            viewport = Canvas(data[0]["FaceProject"]["@DeviceType"], self.preferences.AntialiasingEnabled.isChecked(), self.preferences.DeviceOutlineVisible.isChecked(), self.ui.menuInsert)

            # Create the viewport
            viewport.setAcceptDrops(True)
            viewport.scene.selectionChanged.connect(lambda: selectionChange(viewport))
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
                
            if success:
                self.viewports[name] = [viewport, data[0], data[1], isFprj, xml]

                # Setup Insert Menu
                insertButton = QToolButton()
                insertButton.setMenu(self.ui.menuInsert)
                insertButton.setPopupMode(QToolButton.InstantPopup)
                insertButton.setIcon(QPixmap(":Dark/plus.png"))
                insertButton.setText("Insert Widget")
                insertButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

                insertToolbar = QToolBar()
                insertToolbar.setStyleSheet("background-color: rgb(42, 42, 42); padding-left: 20px; ")
                insertToolbar.addWidget(insertButton)

                widget = QWidget()
                layout = QVBoxLayout()
                layout.addWidget(insertToolbar)
                layout.addWidget(viewport)
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                widget.setLayout(layout)

                index = self.ui.workspace.addTab(widget, icon, name)
                self.ui.workspace.setCurrentIndex(index)
                viewport.setFrameShape(QFrame.NoFrame)
            else:
                self.showDialogue("error", "Cannot render project! Your project files are most likely corrupted.", "viewport.loadObjectsFromData did not return True")
        else:
            self.ui.workspace.setCurrentIndex(self.ui.workspace.indexOf(self.viewports[name][0]))

    def createNewCodespace(self, name, text, language, options={"cursorSmoothCaretAnimation":"on"}):
        # Setup Insert Menu
        insertButton = QToolButton()
        insertButton.setPopupMode(QToolButton.InstantPopup)
        insertButton.setIcon(QPixmap(":Dark/save.png"))
        insertButton.setText("Save")

        insertToolbar = QToolBar()
        #insertToolbar.setLayoutDirection(Qt.RightToLeft)
        insertToolbar.setStyleSheet("background-color: rgb(30, 30, 30)")
        insertToolbar.addWidget(insertButton)

        # Creates a new instance of Monaco in a Codespace (code workspace)
        editor = MonacoWidget()
        editor.setText(text)
        editor.setLanguage(language)
        editor.setEditorOptions(options)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(insertToolbar)
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
        self.ui.actionExit.triggered.connect(self.close)

        # edit
        self.ui.actionProject_XML_File.triggered.connect(self.editProjectXML)
        self.ui.actionPreferences.triggered.connect(self.showPreferences)

        # compile
        self.ui.actionCompile.triggered.connect(self.compileProject)
        self.ui.actionDecompile.triggered.connect(self.decompileProject)

        # help
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
        self.preferences.buttonBox.accepted.connect(self.saveAndLoadPreferences)

    def saveAndLoadPreferences(self):
        self.saveSettings()
        self.loadSettings()
        self.loadTheme()

    def newProject(self):
        # Get where to save the project
        file = QFileDialog.getSaveFileName(self, 'New Project...', "", "Mi Create project (*.mprj);;Legacy Face project files (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()
        isFprj = False

        # Check if file was selected
        if file[0]:
            # Check if fprj
            if file_extension == "fprj":
                self.showDialogue('warning', 'The project was created using the legacy .fprj format. To preserve compatibility, some elements such as text will be immediately converted into images.')
                isFprj = True

            # Get watch model
            watchModel = QInputDialog.getItem(self, "Watch Model", "Set Model:", watchData().models, 0, False)

            # Check if watch model was selected
            if watchModel[1]:
                newProject = mprjProject.create(file[0], list(watchData().modelID.keys())[list(watchData().modelID.values()).index(str(watchModel[0]))])
                if newProject[0]:
                    project = mprjProject.load(file[0])
                    if not project[0]:
                        self.showDialogue("error", f'Cannot open project: {project[1]}. Your project is most likely corrupted.', project[2])
                    else:
                        try:
                            self.createNewWorkspace(file[0], False, [project[2], project[1]], project[3])    
                        except Exception as e:
                            self.showDialogue("error", f"Failed to createNewWorkspace: {e}.", traceback.format_exc())

                else:
                    self.showDialogue("error", f"Failed to create a new project: {newProject[1]}. There's something seriously wrong.", newProject[2])

    def openProject(self): 
        # Get where to open the project from
        file = QFileDialog.getOpenFileName(self, 'Open Project...', "%userprofile%\\", "Watchface projects (*.mprj *.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        # Check if file was selected
        if file[0]:
            if file_extension == "fprj":
                self.showDialogue('warning', 'You are opening a .fprj file. To preserve compatibility, some elements such as text will be immediately converted into images.')
                project = fprjProject.load(file[0])
                self.createNewWorkspace(file[0], True)
            else:
                # project[0] returns if the load was successful
                project = mprjProject.load(file[0])
                if not project[0]:
                    self.showDialogue("error", f'Cannot open project: {project[1]}.', project[2])
                else:
                    try:
                        self.createNewWorkspace(file[0], False, [project[2], project[1]], project[3])    
                    except Exception as e:
                        self.showDialogue("error", f"Failed to open project: {e}.", traceback.format_exc())

    def compileProject(self):
        if self.viewports.get(self.ui.workspace.tabText(self.ui.workspace.currentIndex())) and not self.ui.workspace.tabText == "Welcome":
            location = QFileDialog.getExistingDirectory(self, 'Compile Project To...', "")
            if location[0]:
                # Create output dialog
                dialog = QDialog()
                layout = QVBoxLayout()
                output = QTextEdit()
                output.setMinimumSize(600,400)
                output.setReadOnly(True)
                buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
                layout.addWidget(output)
                layout.addWidget(buttonBox)
                dialog.setLayout(layout)

                currentIndex = self.ui.workspace.currentIndex()
                currentName = self.ui.workspace.tabText(currentIndex)

                print(currentDir+"\\compiler\\compile.exe")
                result = mprjProject.compile(currentName, location, currentDir+"\\compiler\\compile.exe")

                output.setText(str(result))
                buttonBox.accepted.connect(lambda: dialog.close())
                dialog.exec()
        else:
            self.showDialogue("error", "Failed to compile project: No project is open!")
        

    def decompileProject(self):
        self.showDialogue("error", "Will add later, apologies.")
        self.showDialogue("warning", "Please note that images may be glitched when unpacking.")
        file = QFileDialog.getOpenFileName(self, 'Unpack File...', "%userprofile%\\", "Compiled Watchface Binaries (*.bin *.FACE)")

        subprocess.run(f'{currentDir}\\compiler\\unpack.exe  "{file[0]}"')
        self.showDialogue("info", "Decompile success! Would you like to open")

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
        self.preferences_dialog.exec()

    def showAboutWindow(self):
        dialog = QMessageBox(self)
        dialog.setText(f'<html><head/><body><p>Mi Create v{currentVersion}<br/><a href="https://github.com/ooflet/Mi-Create/"><span style=" text-decoration: underline; color:#55aaff;">https://github.com/ooflet/Mi-Create/</span></a></p><p>made with 💖 by tostr</p></body></html>')
        dialog.setIconPixmap(QPixmap(":/Images/MiCreate48x48.png"))
        dialog.setWindowTitle("About Mi Create")
        dialog.exec()

    def showThirdPartyNotices(self):
        dialog = QMessageBox(self)
        dialog.setText('<html><head/><body><p><span style=" text-decoration: underline;">Third Party Notices</span></p><p><a href="https://lucide.dev"><span style=" text-decoration: underline; color:#55aaff;">Lucide Icons</span></a> - Under MIT License<br/><a href="https://github.com/gmarull/qtmodern/tree/master"><span style=" text-decoration: underline; color:#55aaff;">qtmodern</span></a> - Under MIT License<br/>EasyFace Compiler - Under explicit permission</p></body></html>')
        dialog.setWindowTitle("Third Party Notices")
        dialog.exec()

    def showDialogue(self, type, text, detailedText=""):
        threading.Thread(target=playsound, args=(os.path.join(currentDir, f'data\\resource_packs\\sounds\\{type}.wav'),), daemon=True).start()
        MessageBox = QMessageBox(self)
        match type:
            case "info":
                MessageBox.setWindowTitle("Mi Create")
                MessageBox.setWindowIcon(QPixmap(":/Images/MiCreate48x48.png"))
                MessageBox.setIcon(QMessageBox.Information)
                MessageBox.setText(text)
                MessageBox.exec()
            case "question":
                MessageBox.setWindowTitle("Mi Create")
                MessageBox.setWindowIcon(QPixmap(":/Images/MiCreate48x48.png"))
                MessageBox.setIcon(QMessageBox.Question)
                MessageBox.setText(text)
                MessageBox.exec()
            case "warning":
                logging.warning(text)
                MessageBox.setWindowTitle("Mi Create")
                MessageBox.setWindowIcon(QPixmap(":/Images/MiCreate48x48.png"))
                MessageBox.setIcon(QMessageBox.Warning)
                MessageBox.setText(text)
                MessageBox.exec()
            case "error":
                logging.error(text+"\n"+detailedText)
                MessageBox.setWindowTitle("Mi Create")
                MessageBox.setWindowIcon(QPixmap(":/Images/MiCreate48x48.png"))
                MessageBox.setIcon(QMessageBox.Critical)
                MessageBox.setText(text)
                MessageBox.setDetailedText(detailedText)
                MessageBox.exec()
            
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

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
        threading.Thread(target=playsound, args=(os.path.join(currentDir, f'data\\resource_packs\\sounds\\error.wav'),), daemon=True).start()
        error_message = f"Critical error during initialization: {traceback.format_exc()}"
        logging.error(error_message)
        QMessageBox.critical(None, 'Error', error_message, QMessageBox.Ok)
        sys.exit(1)

    main_window.show()
    splash.finish(main_window)
    main_window.checkForUpdates()

    sys.exit(app.exec())