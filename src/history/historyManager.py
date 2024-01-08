from typing import Any
from PySide6.QtCore import Signal

class historySystem:
    def __init__(self):
        self.history = []
        self.index = -1
        self.undoMode = False

    def addToHistory(self, widgetName, property, value, prevValue):
        print("add property " + property)
        if self.index != (len(self.history) - 1) and self.index != -1:
            print("property removing!!!")
            elementsToRemove = len(self.history) - self.index - 1
            for i in range(elementsToRemove):
                print("property removed at index " + str(self.index + 1))
                self.history.pop(self.index + 1)

        print("property append")
        self.history.append([widgetName, property, value, prevValue])
        self.index = len(self.history) - 1
        print("index " + str(self.index))


    def undo(self):
        if self.undoMode == False:
            self.undoMode = True
            return self.history[self.index]

        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        print(self.history)

    def redo(self):
        if self.undoMode == True:
            self.undoMode = False
            return self.history[self.index]

        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        print(self.history)
    