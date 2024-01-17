# Code Editor for Mi Create
# tostr 2024

# Responsible for the embedded code editor for editing XML projects and Lua/JS programs
# Powered by the Scintilla source code editing component
# Uses QScintilla bindings provided by Riverbank Computing's PyQt project

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import *

class XMLLexer(QsciLexerXML):
    def __init__(self, parent, palette):
        super().__init__(parent)
        self.setDefaultColor()

class Editor(QsciScintilla):
    def __init__(self, parent, palette, lexer):
        super().__init__(parent)

        self.setLexer(lexer(self))

        # Font
        self.scintillaFont = QFont("Courier New", 10)
        self.setFont(self.scintillaFont)

        # End of Line
        self.setEolMode(QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)

        # Caret
        self.setCaretLineVisible(True)
        self.setCaretForegroundColor(palette.color(QPalette.ColorRole.Text))
        self.setCaretLineBackgroundColor(palette.color(QPalette.ColorRole.AlternateBase))

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)    

        # Line num margin
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsBackgroundColor(palette.color(QPalette.ColorRole.Dark))
        self.setMarginsForegroundColor(palette.color(QPalette.ColorRole.Text))