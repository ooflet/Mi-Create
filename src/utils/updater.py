import os
import requests
import tempfile
import threading
import subprocess

from PyQt6.QtCore import Qt, QSize, QMetaObject
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QLabel, QProgressBar, QWidget, QVBoxLayout

class Updater(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Updater")
        self.setWindowIcon(QIcon(":Images/MiCreate48x48.png"))
        self.resize(500, 300)
        self.setMinimumSize(QSize(500, 300))
        self.setMaximumSize(QSize(500, 300))

        self.widgetLayout = QVBoxLayout(self)
        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setContentsMargins(9,0,9,9)

        self.title = QLabel(self)
        self.title.setText("Updating...")
        self.title.setStyleSheet("QLabel { font-size: 18pt;}")

        self.status = QLabel(self)

        self.progress = QProgressBar(self)
        self.progress.setTextVisible(False)
        
        self.widgetLayout.addWidget(self.title)
        self.widgetLayout.addWidget(self.status)
        self.widgetLayout.addWidget(self.progress)
        self.setLayout(self.widgetLayout)
        self.downloadThread = threading.Thread(target=self.startDownload, args=[self.startInstall])
        self.downloadThread.start()
        self.exec()

    def startDownload(self, callback):
        url = "https://github.com/ooflet/Mi-Create/releases/latest/download/setup.exe"
        filename = os.path.basename(url)
        filename = filename.replace('?', '_')

        self.status.setText("Downloading...")
        self.progress.setRange(0, 0)

        temp_folder = tempfile.gettempdir()
        self.temp_file = os.path.join(temp_folder, filename)

        total_size = 0
        block_size = 1024
        current_size = 0

        with requests.get(url, stream=True) as r:
            total_size = int(r.headers.get("content-length", 0))
            self.progress.setRange(0, total_size)
            r.raise_for_status()
            with open(self.temp_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    current_size += len(chunk)
                    self.status.setText(f"Downloading... {round(current_size/1000000)} MB/{round(total_size/1000000)} MB")
                    self.progress.setValue(current_size)
                    f.write(chunk)
            
            callback()

    def startInstall(self):
        self.progress.setRange(0, 0)
        self.status.setText("Installing...")
        subprocess.run([self.temp_file, "/verysilent"])
        QMetaObject.invokeMethod(self, "close", Qt.ConnectionType.DirectConnection)