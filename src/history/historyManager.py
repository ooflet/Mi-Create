from typing import Any
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand, QUndoStack

class historySystem:
    def __init__(self):
        self.undoStack = QUndoStack()

class CommandAddWidget(QUndoCommand):
    def __init__(self, data, objectIndex, objectData, description):
        super(CommandModifyProperty, self).__init__(description)
        self.data = data
        self.objectIndex = objectIndex
        self.objectData = objectData

    def redo(self):
        self.data.insert(self.objectIndex, self.objectData)

    def undo(self):
        self.data.pop(self.objectIndex)

class CommandDeleteWidget(QUndoCommand):
    def __init__(self, data, objectIndex, objectData, description):
        super(CommandModifyProperty, self).__init__(description)
        self.data = data
        self.objectIndex = objectIndex
        self.objectData = objectData

    def redo(self):
        self.data.pop(self.objectIndex)

    def undo(self):
        self.data.insert(self.objectIndex, self.objectData)

class CommandMoveWidget(QUndoCommand):
    def __init__(self, inputX, inputY, prevX, prevY, currentX, currentY, description):
        super(CommandModifyProperty, self).__init__(description)
        self.inputX = inputX
        self.inputY = inputY
        self.prevX = prevX
        self.prevY = prevY
        self.currentX = currentX
        self.currentY = currentY

    def redo(self):
         self.inputX.setValue(int(self.currentX))
         self.inputY.setValue(int(self.currentY))

    def undo(self):
        self.inputX.setValue(int(self.prevX))
        self.inputY.setValue(int(self.prevY))

class CommandModifyProperty(QUndoCommand):
    def __init__(self, object, previousString, currentString, description):
        super(CommandModifyProperty, self).__init__(description)
        propertyField = self.propertiesWidget.propertyItems[property]
        
        self.inputObject = inputObject
        self.previousValue = previousString
        self.currentValue = currentString

    def redo(self):
        if self.inputObject.metaObject().className() == "QSpinBox":
            self.inputObject.setValue(int(self.currentValue))              
        elif self.inputObject.metaObject().className() == "QCheckBox":
            self.inputObject.setChecked(self.currentValue)
        else:
            self.inputObject.setText(self.currentValue)

    def undo(self):
        if self.inputObject.metaObject().className() == "QSpinBox":
            self.inputObject.setValue(int(self.previousValue))              
        elif self.inputObject.metaObject().className() == "QCheckBox":
            self.inputObject.setChecked(self.previousValue)
        else:
            self.inputObject.setText(self.previousValue)
    