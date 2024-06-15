# Code Editor for Mi Create
# ooflet <ooflet@proton.me>

# Responsible for the embedded code editor for editing XML projects and Lua/JS programs
# Powered by the Scintilla source code editing component
# Uses QScintilla bindings provided by Riverbank Computing's PyQt project

from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.Qsci import QsciScintilla, QsciLexerXML

class XMLLexer(QsciLexerXML):
    def __init__(self, parent, palette):
        super().__init__(parent)
        self.setFont(QFont("Courier New", 10))
        self.setColor(QColor(255,255,255), 0)
        self.setColor(QColor(78, 140, 191), 1)
        self.setColor(QColor(22, 195, 222), 2)
        self.setColor(QColor(83, 188, 237), 3)
        self.setColor(QColor(255, 255, 255), 4)
        self.setColor(QColor(255, 255, 255), 5)
        self.setColor(QColor(206, 145, 120), 6)
        self.setColor(QColor(255, 255, 255), 7)
        self.setColor(QColor(255, 255, 255), 8)
        self.setColor(QColor(255, 255, 255), 9)
        self.setColor(QColor(255, 255, 255), 10)
        self.setColor(QColor(170, 170, 170), 11)
        self.setColor(QColor(170, 170, 170), 12)
        self.setColor(QColor(170, 170, 170), 13)

class Editor(QsciScintilla):
    def __init__(self, parent, palette, lexer):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setLexer(lexer(self, palette))
        self.setFont(QFont("Courier New", 10))

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