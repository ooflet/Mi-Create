import os

from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from win10toast import ToastNotifier
from threading import Thread
import qtmodern.styles
import qtmodern.windows
import winsound
import traceback
import subprocess

from window_ui import Ui_MainWindow
from about_ui import Ui_Dialog as Ui_AboutDialog
from credit_ui import Ui_Dialog as Ui_ThirdPartyNoticesDialog
from preferences_ui import Ui_Dialog as Ui_Preferences

currentVersion = '0.0.1b'
notification = ToastNotifier()

class Canvas(QGraphicsView):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.preferences_dialog = QDialog()
        self.preferences = Ui_Preferences()
        self.preferences.setupUi(self.preferences_dialog)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.canvas = Canvas()
        self.setupWidgets()
        self.setupWorkspace()

        self.loadSettings()
        self.loadTheme()

        self.statusBar().showMessage("Ready", 3000)

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def saveSettings(self):
        settings = QSettings("Tostr.inc", "MiFaceStudio")
        settings.setValue("theme", self.preferences.themeComboBox.currentText())
        settings.setValue("language", self.preferences.languageComboBox.currentText())

    def loadSettings(self):
        settings = QSettings("Tostr.inc", "MiFaceStudio")
        theme = settings.value("theme", "Dark")
        language = settings.value("language", "English")
        self.preferences.themeComboBox.setCurrentText(theme)
        self.preferences.languageComboBox.setCurrentText(language)

    def launchUpdater(self):
        def execute_installer_script():
            # Path to the installer script
            current_path = os.getcwd()
            installer_script = current_path+"\\updater\\updater.py"
            subprocess.run(["python", installer_script])

        execute_installer_script()
        sys.exit()

    def checkForUpdates(self):
        version = '0.0.2b'
        if version > currentVersion:
            if version[-1] == 'u':
                self.showDialogue('info', f'An urgent update {version} was released! The app will now update.')
                self.launchUpdater()
            else:
                reply = QMessageBox.question(self, 'Message', f'A new update has been found ({version}). Would you like to update now?', QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    self.launchUpdater()


    def loadTheme(self):
        themeName = self.preferences.themeComboBox.currentText()
        app = QApplication.instance()
        if themeName == "Light":
            qtmodern.styles.light(app=app)
            self.showDialogue('info', 'Message', 'Icons in light theme have not been implemented yet. Sorry!')
        else:
            qtmodern.styles.dark(app=app)

    

    def setupWorkspace(self):
        # ...
        # Connect the drag and drop events to the canvas
        self.ui.canvas.dragEnterEvent = self.canvas_dragEnterEvent
        self.ui.canvas.dragMoveEvent = self.canvas_dragMoveEvent
        self.ui.canvas.dropEvent = self.canvas_dropEvent

    def canvas_dragEnterEvent(self, event):
        # Call the dragEnterEvent of the Canvas class
        self.ui.canvas.dragEnterEvent(event)

    def canvas_dragMoveEvent(self, event):
        # Call the dragMoveEvent of the Canvas class
        self.ui.canvas.dragMoveEvent(event)

    def canvas_dropEvent(self, event):
        # Call the dropEvent of the Canvas class
        self.ui.canvas.dropEvent(event)

    def setupWidgets(self):
        # file
        self.ui.actionNewFile.triggered.connect(self.newProject)
        self.ui.actionOpenFile.triggered.connect(self.openProject)
        self.ui.actionPreferences.triggered.connect(self.showPreferences)
        self.ui.actionExit.triggered.connect(self.close)

        # compile
        self.ui.actionCompile.triggered.connect(self.compileProject)

        # help
        self.ui.actionAbout_MiFaceStudio.triggered.connect(self.showAboutWindow)
        self.ui.actionAbout_Qt.triggered.connect(lambda: QMessageBox.aboutQt(self))
        self.ui.actionThirdPartyNotice.triggered.connect(self.showThirdPartyNotices)

        # test
        self.ui.actionshowAboutWindow.triggered.connect(self.showAboutWindow)
        self.ui.actionshowDefaultInfoDialog.triggered.connect(lambda: self.showDialogue("error", "Default Info Dialog", "No cause for alarm, this is a test dialogue!"))
        self.ui.actionshowToast.triggered.connect(lambda: notification.show_toast("Test", "This is a test notification!", duration = 5, threaded = False))
        self.ui.actionshowColorDialog.triggered.connect(self.showColorDialog)
        self.ui.actionshowSelectFont.triggered.connect(self.showFontSelect)
        self.ui.actionInstaller.triggered.connect(self.launchUpdater)

        # preferences
        self.preferences.buttonBox.accepted.connect(self.saveAndLoadPreferences)

    def saveAndLoadPreferences(self):
        self.saveSettings()
        self.loadSettings()
        self.loadTheme()

    def newProject(self):
        file = QFileDialog.getSaveFileName(self, 'New Project...', "", "Watch dial project (*.dial);;Legacy Face project files (*.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        if file_extension == "fprj":
            self.showDialogue('warning', file[0], 'The project was created using the legacy .fprj format. To preserve compatibility, some features will not be available.')
            pass
        else:
            pass

    def openProject(self):
        file = QFileDialog.getOpenFileName(self, 'Open Project...', "%userprofile%\\", "Watchface project files (*.mifp *.fprj)")
        file_extension = QFileInfo(file[0]).suffix()

        if file_extension == "fprj":
            self.showDialogue('warning', file[0], 'The selected file uses the legacy .fprj format. To preserve compatibility, some features will not be available.')
            pass
        else:
            pass


    def compileProject(self):
        location = QFileDialog.getSaveFileName(self, 'Compile Project To...', "", "Binary file (*.bin)")

    def showColorDialog(self):
        options = QColorDialog.ColorDialogOptions()
        color = QColorDialog.getColor(Qt.green, self, "Select Color", options)

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
            error_message = f"An error occurred: {e} at line {lineno}."
        else:
            error_message = f"An error occurred: {e}"
        QMessageBox.critical(None, 'Error', error_message, QMessageBox.Ok)
        sys.exit(1)

    main_window.showMaximized()
    splash.finish(main_window)

    sys.exit(app.exec())