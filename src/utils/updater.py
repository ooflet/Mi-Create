# Updater for Mi Create
# tostr 2024

import os
import sys
import requests
import tempfile
import threading
import subprocess

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QProgressBar, QLabel

class Updater(QDialog):
    updateProgress = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Mi Create")
        self.installComplete = False

        self.setFixedSize(400, 60)

        self.text = QLabel(self)
        self.progressBar = QProgressBar(self)

        self.widgetLayout = QVBoxLayout()
        self.widgetLayout.addWidget(self.text, 0)
        self.widgetLayout.addWidget(self.progressBar, 1)

        self.setLayout(self.widgetLayout)

        self.updateProgress.connect(lambda progress: self.progressBar.setValue(progress))

        self.downloadThread = threading.Thread(target=self.startDownload, args=[self.startInstall])
        self.downloadThread.daemon = True
        self.downloadThread.start()

        self.show()

    def startDownload(self, callback):
        url = "https://github.com/ooflet/Mi-Create/releases/latest/download/setup.exe"
        filename = os.path.basename(url)
        filename = filename.replace('?', '_')

        self.text.setText("Downloading...")
        self.progressBar.setRange(0, 0)

        temp_folder = tempfile.gettempdir()
        self.temp_file = os.path.join(temp_folder, filename)

        total_size = 0
        block_size = 1024
        current_size = 0

        with requests.get(url, stream=True) as r:
            total_size = int(r.headers.get("content-length", 0))
            self.progressBar.setRange(0, total_size)
            r.raise_for_status()
            with open(self.temp_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    current_size += len(chunk)
                    self.text.setText(f"Downloading... {round(current_size/1000000)} MB/{round(total_size/1000000)} MB")
                    self.updateProgress.emit(current_size)
                    f.write(chunk)
            
            callback()

    def updateValue(self, progress):
        self.progressBar.setValue(progress)

    def startInstall(self):
        self.progressBar.setRange(0, 0)
        self.installComplete = True
        self.progressBar.deleteLater()
        self.text.deleteLater()
        try:
            subprocess.run(self.temp_file)
        except:
            pass
        sys.exit(0)