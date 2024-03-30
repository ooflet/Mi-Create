import logging
from typing import Any
from PyQt6.QtGui import QUndoCommand, QUndoStack

class History:
    def __init__(self):
        self.undoStack = QUndoStack()

class CommandAddWidget(QUndoCommand):
    def __init__(self, objectIndex, objectData, commandFunc, description):
        super(CommandAddWidget, self).__init__(description)
        self.objectIndex = objectIndex
        self.objectData = objectData
        self.commandFunc = commandFunc

    def redo(self):
        self.commandFunc("redo", self.objectIndex, self.objectData)

    def undo(self):
        self.commandFunc("undo", self.objectIndex)

class CommandModifyProjectData(QUndoCommand):
    def __init__(self, prevData, newData, commandFunc, description):
        logging.debug(f"prevdata {prevData}, newdata {newData}")
        super(CommandModifyProjectData, self).__init__(description)
        self.prevData = prevData
        self.newData = newData
        self.commandFunc = commandFunc

    def redo(self):
        self.commandFunc(self.newData)

    def undo(self):
        self.commandFunc(self.prevData)

class CommandModifyProperty(QUndoCommand):
    def __init__(self, name, property, previousValue, currentValue, commandFunc, description):
        super(CommandModifyProperty, self).__init__(description)
        self.name = name
        self.property = property
        self.previousValue = previousValue
        self.currentValue = currentValue
        self.commandFunc = commandFunc

    def redo(self):
        self.commandFunc(self.name, self.property, self.currentValue)

    def undo(self):
        self.commandFunc(self.name, self.property, self.previousValue)
    
class CommandModifyPosition(QUndoCommand):
    def __init__(self, previousPosition, currentPosition, commandFunc, description):
        super(CommandModifyPosition, self).__init__(description)
        self.prevPos = previousPosition
        self.currentPos = currentPosition
        self.commandFunc = commandFunc

    def redo(self):
        self.commandFunc(self.currentPos)

    def undo(self):
        self.commandFunc(self.prevPos)