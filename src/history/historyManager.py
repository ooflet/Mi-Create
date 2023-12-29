from typing import Any
from PySide6.QtCore import Signal

class historySystem:
    def __init__(self):
        self.history = []
        self.index = -1

    def addToHistory(self, widgetName, property, value):
        if self.index > len(self.history):
            for i in range(len(self.history) - self.index):
                self.history.pop(self.index + i + 1)
                
        self.history.append([widgetName, property, value])
        self.index = len(self.history)

    def undo(self):
        if self.index > 0:
            self.index -= 1
        return self.history[self.index]

    def redo(self):
        if self.index < len(self.history):
            self.index += 1
        return self.history[self.index]