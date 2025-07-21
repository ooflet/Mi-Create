import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QLineEdit, QComboBox, QCheckBox, QFrame, QFileDialog, QScrollArea
)
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtCore import Qt

from widgets.switch import SwitchControl

os.chdir(os.path.dirname(
    os.path.realpath(__file__)))  # switch working directory to program location so that data files can be found


class PaletteTester(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSS + Palette Theme Tester")
        self.setMinimumSize(900, 550)

        self.palette = QPalette()
        self.themes = {}  # Optional, to support theme selection like in your code

        layout = QHBoxLayout(self)

        # QSS Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Paste your QSS stylesheet here...")
        layout.addWidget(self.editor, 1)

        # Preview Widgets
        preview_container = QVBoxLayout()
        self.preview_frame = QFrame()
        preview_layout = QVBoxLayout(self.preview_frame)

        self.preview_widgets = [
            QLabel("Label Preview"),
            QLineEdit("LineEdit Preview"),
            QPushButton("Button Preview"),
            QComboBox(),
            QCheckBox("CheckBox Preview"),
            SwitchControl()
        ]
        self.preview_widgets[3].addItems(["Option 1", "Option 2", "Option 3"])

        for widget in self.preview_widgets:
            preview_layout.addWidget(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.preview_frame)
        preview_container.addWidget(scroll)
        preview_container.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply QSS")
        reset_btn = QPushButton("Reset")
        load_json_btn = QPushButton("Load colorScheme.json")
        btn_layout.addWidget(load_json_btn)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(reset_btn)
        preview_container.addLayout(btn_layout)

        layout.addLayout(preview_container, 1)

        apply_btn.clicked.connect(self.apply_qss)
        reset_btn.clicked.connect(self.reset_qss)
        load_json_btn.clicked.connect(self.load_palette_from_json)

        self.reset_qss()

    def apply_qss(self):
        self.setStyleSheet(self.editor.toPlainText())

    def reset_qss(self):
        self.editor.setPlainText("")
        self.setStyleSheet("")
        QApplication.instance().setPalette(QApplication.style().standardPalette())

    def load_palette_from_json(self):
        #file_path, _ = QFileDialog.getOpenFileName(self, "Open colorScheme.json", "", "JSON files (*.json)")
        file_path = "themes/Default/data/Dark/colorScheme.json"
        if not file_path:
            return

        try:
            with open(file_path) as f:
                color_scheme = json.load(f)
            self.palette = QPalette()

            for group, roles in color_scheme.items():
                for role, color in roles.items():
                    qcolor = QColor(*color)
                    if group == "Disabled":
                        self.palette.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, role), qcolor)
                    else:
                        self.palette.setColor(getattr(QPalette.ColorRole, role), qcolor)

            QApplication.instance().setPalette(self.palette)

            # Look for style.qss in same directory
            qss_path = os.path.join(os.path.dirname(file_path), "style.qss")
            if os.path.exists(qss_path):
                with open(qss_path) as sf:
                    self.editor.setPlainText(sf.read())
                self.apply_qss()
        except Exception as e:
            print(f"Failed to load palette: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tester = PaletteTester()
    tester.show()
    sys.exit(app.exec())
