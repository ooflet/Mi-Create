from typing import Any
from PySide6.QtCore import Signal

class historySystem:
    def __init__(self):
        self.history = []
        self.index = -1
        self.undoMode = False

    def addToHistory(self, widgetName, property, value, prevValue):
        print("add property "+property)
        if self.index != (len(self.history) - 1) and self.index != -1:
            print("property removing!!!")
            for i in range((len(self.history) -1) - self.index):
                print("property remove at index "+str(self.index))
                self.history.pop((self.index - 1) + i)

        print("property append")
        self.history.append([widgetName, property, value, prevValue])
        self.index = len(self.history) - 1
        print("index "+str(self.index))

    def undo(self):
        if self.undoMode == False:
            self.undoMode = True
            print(self.index, len(self.history))
            return self.history[self.index]

        if self.index > 0:
            self.index -= 1
        return self.history[self.index]

    def redo(self):
        print(self.index, len(self.history))
        if self.undoMode == True:
            self.undoMode = False
            return self.history[self.index]

        if self.index < len(self.history) - 1:
            self.index += 1
        return self.history[self.index]
    