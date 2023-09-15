# Mi Face Studio
# tostr 2023

import os

import PySide6.QtWidgets as QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import theme.styles as theme
import winsound
import traceback
import subprocess

from project.projectManager import watchData, dialProject, fprjProject
from widgets.canvas import Canvas, ObjectIcon
from widgets.properties import PropertiesWidget
from monaco.monaco_widget import MonacoWidget

import resources.icons_rc

from window_ui import Ui_MainWindow
from dialog.about_ui import Ui_Dialog as Ui_AboutDialog
from dialog.credit_ui import Ui_Dialog as Ui_ThirdPartyNoticesDialog
from dialog.preferences_ui import Ui_Dialog as Ui_Preferences

currentDir = os.getcwd()
currentVersion = '0.0.1-pre-alpha-1'

languages = ["English", "繁體中文", "简体中文", "Русский"]

class Compile(QThread):
    # Run compiler.exe in the binaries directory
    def __init__(self, source, output, name):
        super().__init__()
        self.source = source
        self.output = output
        self.name = name+".bin"

    def run(self):
        subprocess.run(f'compiler\compiler.exe compile "{self.source}" "{self.output}" "{self.name}" ')
        #self.complete.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.closeWithoutWarning = False

        # Setup Preferences Dialog
        self.preferences_dialog = QDialog()
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
        self.setupWidgets()
        self.setupWorkspace()
        self.loadWindowState()
        self.loadSettings()
        self.loadTheme()
        self.statusBar().showMessage("Ready", 3000)

    def closeEvent(self, event):
        if self.closeWithoutWarning == False:
            # Ask user if they want to exit
            quit_msg = "Are you sure you want to exit the program?"
            reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.saveWindowState()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def saveWindowState(self):
        settings = QSettings("tostr", "MiFaceStudio")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())

    def loadWindowState(self):
        settings = QSettings("tostr", "MiFaceStudio")
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("state"))

    def saveSettings(self):
        settings = QSettings("tostr", "MiFaceStudio")
        settings.setValue("theme", self.preferences.themeComboBox.currentText())
        settings.setValue("language", self.preferences.languageComboBox.currentText())

    def loadSettings(self):
        settings = QSettings("tostr", "MiFaceStudio")
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
                self.showDialogue('info', 'Message', f'An urgent update {version} was released! The app will now update.')
                self.launchUpdater()
            else:
                reply = QMessageBox.question(self, 'Message', f'A new update has been found (v{version}). Would you like to update now?', QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    self.launchUpdater()


    def loadTheme(self):
        # Loads theme from themeComboBox element. Later on will load the theme from the QSettings directly
        themeName = self.preferences.themeComboBox.currentText()
        app = QApplication.instance()
        if themeName == "Light":
            theme.light(app)
            self.showDialogue('info', 'Message', 'Icons in light theme have not been implemented yet. Sorry!')
        elif themeName == "Dark":
            theme.dark(app)

    def setupExplorer(self, data, isFprj):
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
        if data["FaceProject"]["Screen"].get("Widget") != None:
            for x in data["FaceProject"]["Screen"]["Widget"]:
                objectIcon = QIcon()

                if not ObjectIcon().icon.get(x["@Shape"]):
                    self.showDialogue("error", "Message", "Shape unsupported!")

                objectIcon.addFile(ObjectIcon().icon[x["@Shape"]], QSize(), QIcon.Normal, QIcon.Off)
                object = QTreeWidgetItem(root)
                object.setText(0, x["@Name"])
                object.setIcon(0, objectIcon)
                object.setFlags(object.flags() | Qt.ItemIsEditable)
        self.ui.Explorer.expandAll()

    def clearExplorer(self):
        self.ui.Explorer.clear()

    def createNewWorkspace(self, name, isFprj, data, xml):
        # Setup Project
        self.projectXML = xml
        self.ui.Explorer.clear()
        self.setupExplorer(data[0], isFprj)
            
        # Create a Canvas (QGraphicsScene & QGraphicsView)
        viewport = Canvas(data[0]["FaceProject"]["@DeviceType"], self.preferences.AntialiasingEnabled.isChecked(), self.preferences.DeviceOutlineVisible.isChecked())

        # Create the viewport
        setattr(self, name, viewport)
        self.viewports[name] = viewport
        viewport.setAcceptDrops(True)

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
            index = self.ui.workspace.addTab(viewport, icon, name)
            self.ui.workspace.setCurrentIndex(index)
            self.ui.workspace.currentWidget().setFrameShape(QFrame.NoFrame)
        else:
            self.showDialogue("error", "Message", "Cannot render project! Your project files are most likely corrupted.")

    def createNewCodespace(self, name, text):
        # Creates a new instance of Monaco in a Codespace (code workspace)
        editor = MonacoWidget()
        editor.setTheme("vs-dark")
        editor.setText(text)
        icon = QPixmap(":/Dark/file-code-2.png")
        index = self.ui.workspace.addTab(editor, icon, name)
        self.ui.workspace.setCurrentIndex(index)

    def initializePropertiesWidget(self):
        # Initializes properties widget
        properties_widget = PropertiesWidget()
        self.ui.attributesWidget.setWidget(properties_widget)

    def setupWorkspace(self):
        def handleTabChange(index):
            print(self.viewports)

        def handleTabClose(index):
            reply = QMessageBox.question(self, 'Message', 'Are you sure you want to close this tab?', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                currentWidget = self.ui.workspace.widget(index)
                if isinstance(currentWidget, MonacoWidget):
                    currentWidget.setParent(None)
                    currentWidget.close()
                    currentWidget.deleteLater()
                self.ui.workspace.removeTab(index)

        # Initialize Monaco WebView. This also starts the app in "OpenGL mode".
        self.monaco = MonacoWidget()
        self.ui.workspace.addTab(self.monaco, "init")
        self.ui.workspace.removeTab(1)

        # Connect links in the welcome screen to actions
        self.ui.NewProject.linkActivated.connect(lambda: self.ui.actionNewFile.trigger())
        self.ui.OpenProject.linkActivated.connect(lambda: self.ui.actionOpenFile.trigger())

        self.ui.actionNewTab.triggered.connect(lambda: self.createNewCodespace("test", "work?"))
        self.ui.workspace.currentChanged.connect(handleTabChange)
        self.ui.workspace.tabCloseRequested.connect(handleTabClose)

        self.initializePropertiesWidget()

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
        self.ui.actionshowDefaultInfoDialog.triggered.connect(lambda: self.showDialogue("error", "Default Critical Dialog", "No cause for alarm, this is a test dialogue!"))
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
        file = QFileDialog.getSaveFileName(self, 'New Project...', "", "Watch dial project (*.dial);;Legacy Face project files (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()
        isFprj = False

        # Check if file was selected
        if file[0]:
            # Check if fprj
            if file_extension == "fprj":
                self.showDialogue('warning', file[0], 'The project was created using the legacy .fprj format. To preserve compatibility, some elements such as text will be immediately converted into images.')
                isFprj = True

            # Get watch model
            watchModel = QInputDialog.getItem(self, "Watch Model", "Set Model:", watchData().models, 0, False)

            # Check if watch model was selected
            if watchModel[1]:
                print(list(watchData().modelID.keys())[list(watchData().modelID.values()).index(str(watchModel[0]))])
                newProject = dialProject.create(file[0], list(watchData().modelID.keys())[list(watchData().modelID.values()).index(str(watchModel[0]))])
                if newProject[0]:
                    project = dialProject.load(file[0])
                    if not project[0]:
                        self.showDialogue("error", file[0], f'Cannot open project: {project[1]}. Your project is most likely corrupted.')
                    else:
                        try:
                            self.createNewWorkspace(file[0], False, [project[2], project[1]], project[3])    
                        except Exception as e:
                            self.showDialogue("error", "Message", f"Failed to createNewWorkspace: {e}.")

                else:
                    self.showDialogue("error", "Message", f"Failed to create a new project: {project[1]}. There's something seriously wrong.")

    def openProject(self):
        # Get where to open the project from
        file = QFileDialog.getOpenFileName(self, 'Open Project...', "%userprofile%\\", "Watchface projects (*.dial *.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        # Check if file was selected
        if file[0]:
            if file_extension == "fprj":
                self.showDialogue('warning', file[0], 'You are opening a .fprj file. To preserve compatibility, some elements such as text will be immediately converted into images.')
                project = fprjProject.load(file[0])
                self.createNewWorkspace(file[0], True)
            else:
                # project[0] returns if the load was successful
                project = dialProject.load(file[0])
                if not project[0]:
                    self.showDialogue("error", file[0], f'Cannot open project: {project[1]}. Your project is most likely corrupted.')
                else:
                    try:
                        self.createNewWorkspace(file[0], False, [project[2], project[1]], project[3])    
                    except Exception as e:
                        self.showDialogue("error", "Message", f"Failed to open project: {e}.")

    def compileProject(self):
        # Check if there is a project open
        if self.project == None:
            self.showDialogue('error', 'Message', 'Failed to compile project: No project open!')
        else:
            location = QFileDialog.getSaveFileName(self, 'Compile Project To...', "", "Binary file (*.bin)")
            subprocess.run(f'{currentDir}\\bin\\compiler.exe compile "{self.source}" "{location}" "{self.name}" ')
            self.showDialogue('info', 'Compile', location[0])

    def decompileProject(self):
        self.showDialogue("warning", "Message", "Please note that images may be glitched when unpacking.")
        file = QFileDialog.getOpenFileName(self, 'Unpack File...', "%userprofile%\\", "Compiled Watchface Binaries (*.bin *.FACE)")

        subprocess.run(f'{currentDir}\\bin\\unpack.exe  "{file[0]}"')
        self.showDialogue("info", "Message", "Decompile success! Would you like to open")

    def editProjectXML(self):
        if self.projectXML:
            self.createNewCodespace("Project XML", str(self.projectXML))
        else:
            self.showDialogue("error", "Message", "Failed to open project XML: No project is open!")

    def showColorDialog(self):
        color = QColorDialog.getColor(Qt.white, self, "Select Color")

    def showFontSelect(self):
        font = QFontDialog.getFont(self, "Select Font")

    def showPreferences(self):
        self.loadSettings()
        self.preferences_dialog.exec()

    def showAboutWindow(self):
        dialog = QDialog()
        about = Ui_AboutDialog()
        about.setupUi(dialog)
        about.label_2.setText(f'<html><head/><body><p>Mi Face Studio v{currentVersion}<br/><a href="https://github.com/ooflet/Mi-Face-Studio/"><span style=" text-decoration: underline; color:#55aaff;">https://github.com/ooflet/Mi-Face-Studio/</span></a></p><p>made with 💖 by tostr</p></body></html>')
        dialog.exec()

    def showThirdPartyNotices(self):
        dialog = QDialog()
        about = Ui_ThirdPartyNoticesDialog()
        about.setupUi(dialog)
        dialog.exec()

    def showDialogue(self, type, title, text):
        sound_map = {
            "info": 'SystemAsterisk',
            "question": 'SystemAsterisk',
            "warning": 'SystemAsterisk',
            "error": 'SystemHand'
        }
        sound = sound_map.get(type, 'SystemHand')
        winsound.PlaySound(sound, winsound.SND_ALIAS | winsound.SND_ASYNC)
        MessageBox = QMessageBox()
        match type:
            case "info":
                MessageBox.information(self, title, text, QMessageBox.Ok)
            case "question":
                MessageBox.question(self, title, text, QMessageBox.Ok)
            case "warning":
                MessageBox.warning(self, title, text, QMessageBox.Ok)
            case "error":
                MessageBox.critical(self, title, text, QMessageBox.Ok)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # splash
    pixmap = QPixmap(":/Images/MiFaceStudioSplash.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    try:
        main_window = MainWindow()
        main_window.monaco.setParent(None)
        main_window.monaco.close()
        main_window.monaco.deleteLater()
    except Exception as e:
        winsound.PlaySound('SystemHand', winsound.SND_ALIAS | winsound.SND_ASYNC)
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            filename, lineno, _, _ = tb[-1]  # Get the last stack frame from the traceback
            error_message = f"code exploded: {e} at line {lineno}."
        else:
            error_message = f"code exploded: {e}"
        print(error_message)
        QMessageBox.critical(None, 'Error', error_message, QMessageBox.Ok)
        sys.exit(1)

    main_window.show()
    splash.finish(main_window)
    main_window.checkForUpdates()

    sys.exit(app.exec())