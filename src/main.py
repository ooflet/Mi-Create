# Mi Face Studio
# tostr 2023

import os

import PySide6.QtWidgets as QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtUiTools import *
from PySide6.QtCore import *

#from win10toast import ToastNotifier
import theme.styles as theme
import winsound
import traceback
import subprocess

from project.projectManager import dialProject, fprjProject
from widgets.canvas import Canvas, RectangleWidget
from widgets.properties import PropertiesWidget
from widgets.monaco.monaco_widget import MonacoWidget

from window_ui import Ui_MainWindow
from dialog.about_ui import Ui_Dialog as Ui_AboutDialog
from dialog.credit_ui import Ui_Dialog as Ui_ThirdPartyNoticesDialog
from dialog.preferences_ui import Ui_Dialog as Ui_Preferences

currentDir = os.getcwd()
currentVersion = '0.0.1-pre-alpha-1'
#notification = ToastNotifier()

languages = ["English", "繁體中文", "简体中文", "Русский"]
models = ["Mi Band 8"]

class Compile(QThread):
    complete = Signal()
    def __init__(self, source, output, name):
        super().__init__()
        self.source = source
        self.output = output
        self.name = name+".bin"

    def run(self):
        subprocess.run(f'compiler\compiler.exe compile "{self.source}" "{self.output}" "{self.name}" ')
        self.complete.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.closeWithoutWarning = False

        self.preferences_dialog = QDialog()
        self.preferences = Ui_Preferences()
        self.preferences.setupUi(self.preferences_dialog)

        self.viewports = {}

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupWidgets()
        self.setupWorkspace()
        self.loadWindowState()
        self.loadSettings()
        self.loadTheme()
        self.project = None
        self.statusBar().showMessage("Ready", 3000)

    def closeEvent(self, event):
        if self.closeWithoutWarning == False:
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
        def execute_installer_script():
            installer_script = currentDir+"\\updater\\updater.py"
            subprocess.run(["python", installer_script])

        self.closeWithoutWarning = True
        self.close()
        execute_installer_script()
        sys.exit()

    def checkForUpdates(self):
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
        themeName = self.preferences.themeComboBox.currentText()
        app = QApplication.instance()
        if themeName == "Light":
            #qdarktheme.setup_theme("light")
            theme.light(app)
            self.showDialogue('info', 'Message', 'Icons in light theme have not been implemented yet. Sorry!')
        elif themeName == "Dark":
            #qdarktheme.setup_theme()
            theme.dark(app)

    def createNewWorkspace(self, name, isFprj, data):
            viewport = Canvas()

            setattr(self, name, viewport)
            self.viewports[name] = viewport
            viewport.setAcceptDrops(True)

            testObject = RectangleWidget(0, 0, 50, 50, QColor(255,255,255,255))

            viewport.scene.addItem(testObject)

            if isFprj:
                icon = QPixmap(":/Dark/folder-clock.png")
            else:
                icon = QPixmap(":/Dark/file-clock.png")

            success = viewport.loadObjectsFromData(data)
            
            if success:
                index = self.ui.workspace.addTab(viewport, icon, name)
                self.ui.workspace.setCurrentIndex(index)
            else:
                self.showDialogue("error", "Message", "Cannot render project! Check that files are valid")

    def createNewCodespace(self, name, text):
        editor = MonacoWidget()
        editor.setTheme("vs-dark")
        editor.setText(text)
        icon = QPixmap(":/Dark/file-box.png")
        index = self.ui.workspace.addTab(editor, icon, name)
        self.ui.workspace.setCurrentIndex(index)

    def initializePropertiesWidget(self):
        properties_widget = PropertiesWidget()
        self.ui.attributesWidget.setWidget(properties_widget)

    def setupWorkspace(self):
        def handleTabClose(index):
            reply = QMessageBox.question(self, 'Message', 'Are you sure you want to close this tab?', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.ui.workspace.removeTab(index)

        self.ui.workspace.removeTab(1)
        self.ui.workspace.addTab(MonacoWidget(), "init")
        self.ui.workspace.removeTab(1)
        self.ui.NewProject.linkActivated.connect(lambda: self.ui.actionNewFile.trigger())
        self.ui.OpenProject.linkActivated.connect(lambda: self.ui.actionOpenFile.trigger())
        self.ui.actionNewTab.triggered.connect(lambda: self.createNewCodespace("test", "work?"))
        self.ui.workspace.tabCloseRequested.connect(handleTabClose)

        self.initializePropertiesWidget()

    def setupWidgets(self):
        # file
        self.ui.actionNewFile.triggered.connect(self.newProject)
        self.ui.actionOpenFile.triggered.connect(self.openProject)
        self.ui.actionPreferences.triggered.connect(self.showPreferences)
        self.ui.actionExit.triggered.connect(self.close)

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
        #self.ui.actionshowToast.triggered.connect(lambda: notification.show_toast("Test", "This is a test notification!", duration = 5, threaded = False))
        self.ui.actionshowColorDialog.triggered.connect(self.showColorDialog)
        self.ui.actionshowSelectFont.triggered.connect(self.showFontSelect)
        self.ui.actionInstaller.triggered.connect(self.launchUpdater)

        # preferences
        self.preferences
        self.preferences.buttonBox.accepted.connect(self.saveAndLoadPreferences)

    def saveAndLoadPreferences(self):
        self.saveSettings()
        self.loadSettings()
        self.loadTheme()

    def newProject(self):
        file = QFileDialog.getSaveFileName(self, 'New Project...', "", "Watch dial project (*.dial);;Legacy Face project files (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()
        isFprj = False

        if file[0]:
            if file_extension == "fprj":
                self.showDialogue('warning', file[0], 'The project was created using the legacy .fprj format. To preserve compatibility, some features will not be available.')
                isFprj = True

            watchModel = QInputDialog.getItem(self, "Watch Model", "Set Model:", models, 0, False)
            if watchModel[1]:
                project = dialProject.create(file[0])
                print(project)
                if project[0]:
                    self.createNewWorkspace(file[0], isFprj, project[1])
                else:
                    self.showDialogue("error", "Message", "Failed to create a new project: "+project[1])

    def openProject(self):
        file = QFileDialog.getOpenFileName(self, 'Open Project...', "%userprofile%\\", "Watchface projects (*.dial *.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        if file[0]:
            if file_extension == "fprj":
                self.showDialogue('warning', file[0], 'You are opening a .fprj file. To preserve compatibility, some features will not be available.')
                project = fprjProject.load(file[0])
                self.createNewWorkspace(file[0], True)
            else:
                project = dialProject.load(file[0])
                if project[0] == False:
                    self.showDialogue("error", file[0], f'Cannot open project: {project[1]}')
                else:
                    self.createNewWorkspace(file[0], False, project[2])    

    def compileProject(self):
        if self.project == None:
            self.showDialogue('error', 'Message', 'Failed to compile project: No project open!')
        else:
            location = QFileDialog.getSaveFileName(self, 'Compile Project To...', "", "Binary file (*.bin)")
            subprocess.run(f'{currentDir}\compiler\compiler.exe compile "{self.source}" "{location}" "{self.name}" ')
            self.showDialogue('info', 'Compile', location[0])

    def decompileProject(self):
        self.showDialogue("warning", "Message", "Please note that images may be glitched when unpacking.")
        file = QFileDialog.getOpenFileName(self, 'Unpack File...', "%userprofile%\\", "Compiled Watchface Binaries (*.bin *.FACE)")

        subprocess.run(f'{currentDir}\compiler\decompile.exe  "{file[0]}"')
        self.showDialogue("info", "Message", "Decompile success! Would you like to open")

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
        about.label_2.setText(f'<html><head/><body><p>Mi Face Studio v{currentVersion}<br/><a href="https://github.com/ooflet/Mi-Face-Studio/"><span style=" text-decoration: underline; color:#55aaff;">https://github.com/ooflet/Mi-Face-Studio/</span></a></p><p>made with ❤️ by tostr</p></body></html>')
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
        if type == "info":
            MessageBox.information(self, title, text, QMessageBox.Ok)
        elif type == "question":
            MessageBox.question(self, title, text, QMessageBox.Ok)
        elif type == "warning":
            MessageBox.warning(self, title, text, QMessageBox.Ok)
        elif type == "error":
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