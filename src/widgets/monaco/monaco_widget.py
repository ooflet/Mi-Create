from qtpy.QtCore import QObject, Signal, Slot, Property, QUrl
from qtpy.QtWebEngineWidgets import * 
from qtpy.QtWebChannel import *

from pathlib import Path
import json


class BaseBridge(QObject):
    initialized = Signal()
    sendDataChanged = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.active = False
        self.queue = []

    def send_to_js(self, name, value):
        if self.active:
            data = json.dumps(value)
            self.sendDataChanged.emit(name, data)
        else:
            self.queue.append((name, value))

    @Slot(str, str)
    def receive_from_js(self, name, value):
        data = json.loads(value)
        self.setProperty(name, data)

    @Slot()
    def init(self):
        self.initialized.emit()
        self.active = True
        for name, value in self.queue:
            self.send_to_js(name, value)

        self.queue.clear()

class EditorBridge(BaseBridge):
    valueChanged = Signal()
    languageChanged = Signal()
    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._value = ""
        self._language = ""
        self._theme = ""

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self.valueChanged.emit()

    def getLanguage(self):
        return self._language

    def setLanguage(self, language):
        self._language = language
        self.languageChanged.emit()

    def getTheme(self):
        return self._theme

    def setTheme(self, theme):
        self._theme = theme
        self.themeChanged.emit()  # Emit the theme change signal

    value = Property(str, fget=getValue, fset=setValue, notify=valueChanged)
    language = Property(
        str, fget=getLanguage, fset=setLanguage, notify=languageChanged
    )
    theme = Property(str, fget=getTheme, fset=setTheme, notify=themeChanged)


index = Path(__file__).parent / "index.html"

with open(index) as f:
    raw_html = f.read()


class MonacoPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        pass


class MonacoWidget(QWebEngineView):
    initialized = Signal()
    textChanged = Signal(str)
    themeChanged = Signal(str)  # Add a theme change signal

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        html = raw_html.replace('width:400px;', f'width:{self.size().width()}px;')
        html = raw_html.replace('height:400px;', f'height:{self.size().height()}px;')

        page = MonacoPage(parent=self)
        self.setPage(page)

        filename = Path(__file__).parent / "index.html"
        self.setHtml(html, QUrl.fromLocalFile(filename.as_posix()) )

        self._channel = QWebChannel(self)
        self._bridge = EditorBridge()

        self.page().setWebChannel(self._channel)
        self._channel.registerObject("bridge", self._bridge)

        self._bridge.initialized.connect(self.initialized)
        self._bridge.valueChanged.connect(lambda: self.textChanged.emit(self._bridge.value))
        self._bridge.themeChanged.connect(lambda: self.handleThemeChange("vs-dark"))  # Connect themeChanged signal to a slot

    def text(self):
        return self._bridge.value

    def setText(self, text):
        self._bridge.send_to_js("value", text)

    def language(self):
        return self._bridge.language

    def setLanguage(self, language):
        self._bridge.send_to_js("language", language)

    def handleThemeChange(self, theme):  # Implement the handleThemeChange method
        self.themeChanged.emit(theme)  # Emit the themeChanged signal with the new theme

    def setTheme(self, theme):
        self._bridge.send_to_js("theme", theme)