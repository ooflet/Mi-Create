# Properties Widget for Mi Create
# tostr 2023

import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen
from pprint import pprint

"""
TODO:
Properties.json will be a scaffold. Each property's third
argument is the actual data.

"""

class GridDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        rect = option.rect  # Get the rectangle area of the item
        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        # Create a custom pen with a thickness of 1 pixel
        pen = QPen(QColor(60,60,60))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw horizontal line at the bottom of the cell (except for the last row)
        if index.row() < index.model().rowCount() - 1:
            painter.drawLine(left, bottom, right, bottom)

        # Draw vertical line at the right edge of the cell
        painter.drawLine(right, top, right, bottom)

        # Call the base class paint method to paint the item
        super().paint(painter, option, index)

class PropertiesWidget(QWidget):
    propertyChanged = Signal(str, str)
    def __init__(self):
        super().__init__()

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setFrameShape(QFrame.NoFrame)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.treeWidget.setUniformRowHeights(True)

        self.treeWidget.setHeaderLabels(["Property", "Value"])
        self.treeWidget.setItemDelegate(GridDelegate())

        layout = QVBoxLayout(self)
        layout.addWidget(self.treeWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
    
    def sendPropertyChangedSignal(self, property, value):
        self.propertyChanged.emit(property, value)

    def addProperty(self, name, valueWidget):
        item = QTreeWidgetItem(self.treeWidget, [name, ""])
        self.treeWidget.setItemWidget(item, 1, valueWidget)

    def createLineEdit(self, text, disabled, srcProperty):
        def onDeselect():
            lineEdit.clearFocus()
            self.treeWidget.setCurrentItem(None)
            self.sendPropertyChangedSignal(srcProperty, lineEdit.text())

        lineEdit = QLineEdit(self)
        lineEdit.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        lineEdit.setText(text)
        lineEdit.setDisabled(disabled)
        lineEdit.editingFinished.connect(onDeselect)
        return lineEdit

    def createSpinBox(self, text, disabled, srcProperty, minVal=-9999, maxVal=9999):
        def onChanged():
            self.sendPropertyChangedSignal(srcProperty, str(spinBox.value()))

        def onDeselect():
            spinBox.clearFocus()
            self.treeWidget.setCurrentItem(None)

        spinBox = QSpinBox(self)
        spinBox.setStyleSheet("background-color: rgba(0, 0, 0, 0); ")
        spinBox.setRange(minVal, maxVal)
        if text == None:
            text = "0"
        spinBox.setValue(int(text))
        spinBox.setDisabled(disabled)
        spinBox.valueChanged.connect(onChanged)
        spinBox.editingFinished.connect(onDeselect)
        return spinBox
    
    def createComboBox(self, srcProperty):
        def onChanged():
            self.sendPropertyChangedSignal(srcProperty, comboBox.currentText())

        comboBox = QComboBox(self)
        comboBox.currentTextChanged.connect(onChanged)
        return comboBox
    
    def createCheckBox(self, checked, srcProperty):
        def onChecked():
            self.sendPropertyChangedSignal(srcProperty, checkBox.isChecked())

        if checked == "0":
            checked = False
        elif checked == "1":
            checked = True

        checkBox = QCheckBox(self)
        checkBox.setStyleSheet("padding-left: 4px")
        if checked == None:
            checked = False
        checkBox.setChecked(checked)
        checkBox.stateChanged.connect(onChecked)
        return checkBox
    
    def loadProperties(self, properties, data):
        print("Loading properties")
        self.treeWidget.clear()
        objectName = self.createLineEdit(properties["Shape"], True, "")
        self.addProperty("ObjectName", objectName)
        print("Added property")
        print("------------------------------------------------------")
        for key, value in properties["properties"].items():
            value[2] = data.get(key)
            match value[1]:
                case "disabled":
                    input = self.createLineEdit(value[2], True, key)
                    self.addProperty(value[0], input)
                case "text":
                    input = self.createLineEdit(value[2], False, key)
                    self.addProperty(value[0], input)
                case "int":
                    input = self.createSpinBox(value[2], False, key)
                    self.addProperty(value[0], input)
                case "bool":
                    input = self.createCheckBox(value[2], key)
                    self.addProperty(value[0], input)
                case "aint":
                    # alpha integer
                    input = self.createSpinBox(value[2], False, key, 0, 255)
                    self.addProperty(value[0], input)

    def clearProperties(self):
        self.treeWidget.clear()