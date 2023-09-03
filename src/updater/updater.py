from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QThread, Signal, Slot
from updater_ui import Ui_UpdaterWindow
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import winsound
import traceback
import sys
import os
import tempfile
import subprocess

def setIndecisive(self, text):
    self.ui.UpdateStatus.setText(text)
    self.ui.progressBar.setMinimum(0)
    self.ui.progressBar.setMaximum(0)
    self.ui.progressBar.setValue(0)

def setDecisive(self, text):
    self.ui.UpdateStatus.setText(text)
    self.ui.progressBar.setMinimum(0)
    self.ui.progressBar.setMaximum(100)
    self.ui.progressBar.setValue(0)

class DownloadThread(QThread):
    setTotalProgress = Signal(int)
    setCurrentProgress = Signal(int)
    succeeded = Signal()
    failed = Signal(str)  # Define a custom signal for download failure

    def __init__(self, url, filename, chunkSize=8192):
        super().__init__()
        self.url = url
        self.filename = filename
        self.chunkSize = chunkSize

    def run(self):
        readBytes = 0

        try:
            with urlopen(self.url) as r:
                self.setTotalProgress.emit(int(r.info()["Content-Length"]))
                with open(self.filename, "ab") as f:
                    while True:
                        chunk = r.read(self.chunkSize)
                        if chunk is None:
                            continue
                        elif chunk == b"":
                            break
                        f.write(chunk)
                        readBytes += len(chunk)
                        self.setCurrentProgress.emit(readBytes)
        except (URLError, HTTPError) as e:
            self.failed.emit(str(e))  # Emit the failure signal
            return

        self.succeeded.emit()

class InstallThread(QThread):
    complete = Signal()
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        subprocess.run(self.filename+" /verysilent")
        self.complete.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_UpdaterWindow()
        self.ui.setupUi(self)
        setIndecisive(self, 'Getting update package...')

        self.download_thread = None
        self.warning = True

    def startDownload(self):
        url = "https://github.com/ooflet/Mi-Face-Studio/releases/latest/download/Mi.Face.Studio.Setup.exe"
        self.filename = os.path.basename(url)
        self.filename = self.filename.replace('?', '_')

        setDecisive(self, 'Downloading...')
        self.download_thread = DownloadThread(url, self.filename)
        self.download_thread.setTotalProgress.connect(self.updateTotalProgress)
        self.download_thread.setCurrentProgress.connect(self.updateCurrentProgress)
        self.download_thread.succeeded.connect(self.install)
        self.download_thread.failed.connect(self.handleDownloadFailed)

        # Start the thread
        self.download_thread.start()

    @Slot(int)
    def updateTotalProgress(self, total):
        self.ui.progressBar.setMaximum(total)

    @Slot(int)
    def updateCurrentProgress(self, current):
        self.ui.progressBar.setValue(current)

    @Slot()
    def install(self):
        self.download_thread.wait()
        self.download_thread.deleteLater()
        self.download_thread = None

        try:
            # Save the downloaded file in the temporary folder
            temp_folder = tempfile.gettempdir()
            temp_file = os.path.join(temp_folder, self.filename)
            if os.path.exists(temp_file):
                os.remove(temp_file)
            os.rename(self.filename, temp_file)

            # Execute the downloaded file from the temporary folder

            setIndecisive(self, 'Installing...')

            self.install_thread = InstallThread(temp_file)
            self.install_thread.complete.connect(lambda: sys.exit())

            self.install_thread.start()
            

        except FileExistsError as e:
            winsound.PlaySound('SystemHand', winsound.SND_ALIAS | winsound.SND_ASYNC)
            QMessageBox.critical(None, 'Error', f"An error occurred: {e}", QMessageBox.Ok)
            sys.exit(1)

    @Slot(str)
    def handleDownloadFailed(self, error):
        winsound.PlaySound('SystemHand', winsound.SND_ALIAS | winsound.SND_ASYNC)
        QMessageBox.critical(None, 'Error', f"An error occurred: {error}", QMessageBox.Ok)
        sys.exit(1)

app = QtWidgets.QApplication(sys.argv)
#app.setStyle('Fusion')
main_window = MainWindow()
main_window.setWindowFlags(Qt.FramelessWindowHint)
main_window.show()
try:
    main_window.startDownload()
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

sys.exit(app.exec())
