# Properties Widget for Mi Create
# ooflet <ooflet@proton.me>

# Use a properties "scaffold" with the widget when creating

import sys

sys.path.append("..")

import os
import gettext
import logging
import threading
from typing import Any
from utils.project import FprjProject, XiaomiProject

from PyQt6.QtWidgets import (QStyleOptionViewItem, QStyledItemDelegate, QWidget, QFileDialog, QTreeWidget, QFrame, QHeaderView, QPushButton,
                               QDialog, QDialogButtonBox, QVBoxLayout, QListWidgetItem, QTreeWidgetItem, QLineEdit, 
                               QSpinBox, QComboBox, QStyle, QCheckBox, QMessageBox, QAbstractItemView, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize, QModelIndex
from PyQt6.QtGui import QColor, QPen, QGuiApplication, QIcon, QPalette, QStandardItemModel
from pprint import pprint

from translate import QCoreApplication

_ = gettext.gettext

class TreeWidgetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        rect = option.rect  # Get the rectangle area of the item
        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        # Create a custom pen with a thickness of 1 pixel
        pen = QPen(QPalette().alternateBase().color())
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw horizontal line at the bottom of the cell
        painter.drawLine(left, bottom, right, bottom)

        # Draw vertical line at the right edge of the cell
        painter.drawLine(right, top, right, bottom)

        # Call the base class paint method to paint the item
        super().paint(painter, option, index)

class PropertiesWidget(QWidget):
    propertyChanged = pyqtSignal(object, object)
    def __init__(self, window, srcList=None, srcData=None):
        super().__init__()

        self.clearOnRefresh = True
        self.ignorePropertyChange = False

        self.treeWidgetItems = []
        self.propertyItems = {}
        self.imageListCategories = []
        self.imageFolder = ""
        self.currentPropertyInput = None
        self.resourceList = []

        self.sourceList = srcList
        self.sourceData = srcData

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setObjectName("propertiesList")
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setFrameShape(QFrame.Shape.NoFrame)
        self.treeWidget.setRootIsDecorated(True)
        self.treeWidget.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.treeWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeWidget.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.treeWidget.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setUniformRowHeights(True)
        
        self.treeWidget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.treeWidget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.treeWidget.setHeaderLabels(["Property", "Value"])
        self.treeWidget.setItemDelegate(TreeWidgetDelegate())

        # self.searchWidget = QLineEdit(self)
        # self.searchWidget.setPlaceholderText(QCoreApplication.translate("MainWindow", "Search..."))

        layout = QVBoxLayout(self)
        # layout.addWidget(self.searchWidget)
        layout.addWidget(self.treeWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def loadLanguage(self, language):
        translation = gettext.translation('properties', localedir='locales', languages=[language])
        translation.install()
        global _
        _ = translation.gettext
    
    def sendPropertyChangedSignal(self, property, value):
        if not self.ignorePropertyChange:
            self.propertyChanged.emit(property, value)
        else:
            self.ignorePropertyChange = False

    def addProperty(self, srcProperty, name, valueWidget, parent=None, inputSinker=None) -> QTreeWidgetItem:
        if parent != None:
            item = QTreeWidgetItem(parent, [_(name), ""])

            if inputSinker:
                self.treeWidget.setItemWidget(item, 1, inputSinker)
            else:        
                self.treeWidget.setItemWidget(item, 1, valueWidget)
            
            if srcProperty != "":
                self.propertyItems[srcProperty] = valueWidget
        else:
            item = QTreeWidgetItem()
            item.setText(0, _(name))

            self.treeWidget.addTopLevelItem(item)
            if inputSinker:
                self.treeWidget.setItemWidget(item, 1, inputSinker)
            else:        
                self.treeWidget.setItemWidget(item, 1, valueWidget)

            if srcProperty != "":
                self.propertyItems[srcProperty] = valueWidget

        item.setToolTip(0, _(name))
        item.setExpanded(True)
        return item

    def createLineEdit(self, text, disabled, propertySignalDisabled, srcProperty=""):
        def onDeselect():
            lineEdit.clearFocus()
            self.treeWidget.setCurrentItem(None)
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, lineEdit.text())

        lineEdit = QLineEdit(self)
        lineEdit.setObjectName("propertyField-input")
        lineEdit.setText(str(text))
        lineEdit.setDisabled(disabled)
        lineEdit.editingFinished.connect(onDeselect)
        return lineEdit
    
    def createButton(self, text, property):
        def onClick():
            self.sendPropertyChangedSignal(property, "click")

        button = QPushButton(self)
        button.setObjectName("propertyField-input")
        button.setText(text)
        button.clicked.connect(onClick)
        return button
    
    def createResourceEdit(self, text, disabled, resourceList, propertySignalDisabled, srcProperty=""):
        def dragEnterEvent(event):
            if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
                event.acceptProposedAction()

        def dragMoveEvent(event):
            if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
                event.acceptProposedAction()

        def dropEvent(event):
            model = QStandardItemModel()
            model.dropMimeData(event.mimeData(), Qt.DropAction.CopyAction, 0, 0, QModelIndex())
            if model.item(0, 0).data(0) in resourceList:
                resourceEdit.setCurrentIndex(resourceList.index(model.item(0, 0).data(0)))
            else:
                QMessageBox.information(None, "Properties", f"Image not found in resourceList!")

            event.acceptProposedAction()

        def wheelEvent(event):
            if resourceEdit.hasFocus():
                return QComboBox.wheelEvent(resourceEdit, event)
            else:
                event.ignore()

        def onChange(event):
            self.sendPropertyChangedSignal(srcProperty, resourceEdit.currentText())

        resourceEdit = QComboBox(self)
        resourceEdit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        resourceEdit.setEditable(True)
        resourceEdit.setAcceptDrops(True)
        resourceEdit.setObjectName("propertyField-input")
        resourceEdit.addItems(resourceList)
        resourceEdit.setCurrentText(text)
        resourceEdit.setDisabled(disabled)
        resourceEdit.wheelEvent = wheelEvent
        resourceEdit.dragEnterEvent = dragEnterEvent
        resourceEdit.dragMoveEvent = dragMoveEvent
        resourceEdit.dropEvent = dropEvent
        if not propertySignalDisabled:
            resourceEdit.currentTextChanged.connect(onChange)
        return resourceEdit

    def createSpinBox(self, text, disabled, propertySignalDisabled, srcProperty, minVal=-9999, maxVal=9999):
        def onChanged():
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, str(spinBox.value()))

        def onDeselect():
            spinBox.clearFocus()
            self.treeWidget.setCurrentItem(None)

        def wheelEvent(event):
            if spinBox.hasFocus():
                return QSpinBox.wheelEvent(spinBox, event)
            else:
                event.ignore()

        spinBox = QSpinBox(self)
        spinBox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        spinBox.setObjectName("propertyField-input")
        spinBox.setRange(minVal, maxVal)
        if text == None:
            text = "0"
        spinBox.setValue(int(text))
        spinBox.setDisabled(disabled)
        spinBox.wheelEvent = wheelEvent
        spinBox.valueChanged.connect(onChanged)
        spinBox.editingFinished.connect(onDeselect)
        return spinBox
    
    def createComboBox(self, items, selected, srcProperty, editable):
        def onChanged():
            comboBox.clearFocus()
            self.sendPropertyChangedSignal(srcProperty, comboBox.currentText())

        def wheelEvent(event):
            if comboBox.hasFocus():
                return QComboBox.wheelEvent(comboBox, event)
            else:
                event.ignore()

        comboBox = QComboBox(self)
        comboBox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        comboBox.addItems(items)
        comboBox.setObjectName("propertyField-input")
        comboBox.wheelEvent = wheelEvent

        if editable:
            comboBox.setEditable(True)
        else:
            comboBox.setCursor(Qt.CursorShape.PointingHandCursor)
            
        if selected:
            if selected.isnumeric():
                comboBox.setCurrentIndex(int(selected))
            else:
                if selected in items:
                    comboBox.setCurrentIndex(items.index(selected))

        comboBox.activated.connect(onChanged)
        return comboBox
    
    def createAlignmentComboBox(self, selected, srcProperty):
        items = ["Left", "Center", "Right"]

        def wheelEvent(event):
            if comboBox.hasFocus():
                return QComboBox.wheelEvent(comboBox, event)
            else:
                event.ignore()

        def onChanged():
            self.sendPropertyChangedSignal(srcProperty, comboBox.currentText())

        comboBox = QComboBox(self)
        comboBox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        comboBox.addItems(items)
        if selected:
            comboBox.setCurrentIndex(int(selected))
        comboBox.wheelEvent = wheelEvent
        comboBox.currentTextChanged.connect(onChanged)
        return comboBox

    def createCheckBox(self, checked, srcProperty, propertySignalDisabled=False):
        def onChecked():
            self.sendPropertyChangedSignal(srcProperty, checkBox.isChecked())

        def onClick():
            if checkBox.isChecked():
                checkBox.setChecked(False)
            else:
                checkBox.setChecked(True)

        if checked == "0":
            checked = False
        elif checked == "1":
            checked = True

        # prevent row from highlighting over mouse hover in input area using an input sinker
        inputSinker = QPushButton(self)
        inputSinker.setStyleSheet("background: none; border: none;")
        inputSinker.clicked.connect(onClick)

        checkBox = QCheckBox(inputSinker)
        checkBox.setObjectName("propertyField-input")
        if checked == None or checked == "":
            checked = False
        checkBox.setChecked(checked)
        if propertySignalDisabled == False:
            checkBox.stateChanged.connect(onChecked)
        return inputSinker, checkBox
    
    def createCategory(self, name, parent=None):
        item = QTreeWidgetItem()
        item.setText(0, name)
        if parent:
            parent.addChild(item)  # Add category as a child of the parent category
        else:
            self.treeWidget.addTopLevelItem(item)
        item.setExpanded(True)
        return item

    def addProperties(self, properties, project=None, widgetName=None, resourceList=None, parent=None, device=None):
        if project != None:
            widget = project.getWidget(widgetName)
            
        for key, property in properties.items():
            if not property.get("string"):
                # category
                categoryItem = self.createCategory(_(key), parent)
                self.addProperties(property, project, widgetName, resourceList, categoryItem, device)  # Recursively add sub-categories
            else:
                ignorePropertyCreation = False
                # property
                propertyValue = None
                if project != None and widget.getProperty(key) != None:
                    propertyValue = widget.getProperty(key)
                else:
                    propertyValue = property["value"]

                inputWidget = None
                
                if property["type"] == "disabled":
                    inputWidget = self.createLineEdit(propertyValue, True, False, key)
                elif property["type"] == "str":
                    inputWidget = self.createLineEdit(propertyValue, False, False, key)
                elif property["type"] == "btn":
                    inputWidget = self.createButton(propertyValue, key)
                elif property["type"] == "img":
                    inputWidget = self.createResourceEdit(propertyValue, False, resourceList, False, key)
                elif property["type"] == "list":
                    inputWidget = self.createComboBox(property["options"], propertyValue, key, False)
                elif property["type"] == "imglist":
                    self.imageCategories = []

                    def imagesChanged(stringIndex, image, index):
                        imageString = [stringIndex, image]
                        if len(propertyValue) - 1 >= index:
                            propertyValue[index] = imageString
                        else:
                            propertyValue.insert(index, imageString)
                        self.sendPropertyChangedSignal(key, propertyValue)

                    def createImageCategories(imageList, imageCount):
                        for index in range(0, imageCount):
                            imageCategory = self.createCategory("Image"+str(index), parent)
                            imageInput = self.createResourceEdit("", False, resourceList, True, key)
                            indexInput = self.createSpinBox(None, False, True, key)
                            self.addProperty("", "Image", imageInput, imageCategory)
                            self.addProperty("", "Index", indexInput, imageCategory)
                            self.imageCategories.append([imageCategory, imageInput, indexInput])

                            if len(imageList) > index:
                                image = imageList[index]
                                if image != None and len(image) > 1:
                                    indexInput.setValue(int(image[0])) 
                                    imageInput.setCurrentText(image[1])             
                                imageInput.currentTextChanged.connect(lambda event, indexInput=self.imageCategories[index][2], imageInput=self.imageCategories[index][1], index=index: imagesChanged(indexInput.text(), imageInput.currentText(), index))
                                indexInput.textChanged.connect(lambda text, imageInput=self.imageCategories[index][1], index=index: imagesChanged(text, imageInput.currentText(), index))
                            else:
                                imageInput.currentTextChanged.connect(lambda event, indexInput=self.imageCategories[index][2], imageInput=self.imageCategories[index][1], index=index: imagesChanged(indexInput.text(), imageInput.currentText(), index))
                                indexInput.textChanged.connect(lambda text, imageInput=self.imageCategories[index][1], index=index: imagesChanged(text, imageInput.currentText(), index))
 
                        return True, None

                    def deleteAllCategories():
                        for category in self.imageCategories:
                            category[0].parent().removeChild(category[0])

                        self.imageCategories = []

                    def updateImageAmount(value):
                        value = int(value)
                        prevLocation = self.treeWidget.verticalScrollBar().value()
                        deleteAllCategories()
                        createImageCategories(propertyValue, value)
                        self.treeWidget.verticalScrollBar().setValue(prevLocation)

                    ignorePropertyCreation = True
                    imageAmountInput = self.createSpinBox(len(propertyValue), False, True, key, 0, 100)
                    imageAmountInput.textChanged.connect(lambda value=imageAmountInput.value(): updateImageAmount(value))
                    self.addProperty("", "Image Count", imageAmountInput, parent)

                    success, message = createImageCategories(propertyValue, len(propertyValue))

                    if not success:
                        QMessageBox.critical(None, "Properties", f"Error occured loading images: {message}")

                elif property["type"] == "numlist":
                    ignorePropertyCreation = True

                    decimalList = []

                    checked = False

                    print(len(propertyValue))

                    if len(propertyValue) > 11:
                        checked = True

                    def toggled(checked):
                        if checked:
                            createDecimalInputList()
                        else:
                            for item in decimalList:
                                item.parent().removeChild(item)
                            decimalList.clear()

                    def updateNumberList(index, text):
                        if index >= len(propertyValue):
                            propertyValue.insert(index, text)
                        else:
                            propertyValue[index] = text
                        self.sendPropertyChangedSignal(key, propertyValue)

                    def createInput(index, definedText=None, isDecimal=False):
                        text = ""
                        if index < len(propertyValue):
                            text = propertyValue[index]
                        imageInput = self.createResourceEdit(text, False, resourceList, True)
                        if definedText == None:
                            item = self.addProperty("", f"{_('Number')} {str(index)}", imageInput, parent)
                        else:
                            item = self.addProperty("", definedText, imageInput, parent)
                        imageInput.currentTextChanged.connect(lambda *event, index=index: updateNumberList(index, imageInput.currentText()))
                        
                        if isDecimal:
                            decimalList.append(item)

                    def createDecimalInputList():
                        createInput(11, "Decimal Point", True)

                    showDecimalCheckbox = self.createCheckBox(checked, "", True)
                    showDecimalCheckbox[1].toggled.connect(toggled)

                    self.addProperty("", "Show Decimals", showDecimalCheckbox[0], parent)

                    for index in range(0, 10):
                        createInput(index)

                    createInput(10, "Negative Sign")
                    
                    if checked:
                        createDecimalInputList()

                elif property["type"] == "int":
                    if len(property) < 5:
                        QMessageBox.critical(None, "Properties", f"Int property for {property['string']} requires a min/max val")
                    inputWidget = self.createSpinBox(propertyValue, False, False, key, int(property["min"]), int(property["max"]))
                elif property["type"] == "bool":
                    inputSinker, inputWidget = self.createCheckBox(propertyValue, key)
                elif property["type"] == "src":
                    for x in self.sourceData[str(device)]:
                        if propertyValue != '':
                            if isinstance(propertyValue, int) or propertyValue.isnumeric():
                                if int(x["@ID"]) == int(propertyValue):
                                    inputWidget = self.createComboBox(self.sourceList[str(device)], x["@Name"], key, True)
                                    break
                            else:
                                if x["@ID"] == propertyValue:
                                    inputWidget = self.createComboBox(self.sourceList[str(device)], x["@Name"], key, True)
                                    break
                        else:
                            inputWidget = self.createComboBox(self.sourceList[str(device)], False, key, True)
                            break   

                    else:
                        QMessageBox.warning(None, "Properties", f"Data source not found.")
                        inputWidget = self.createComboBox(self.sourceList[str(device)], False, key, True)
                if not ignorePropertyCreation:
                    if property.get("visibleOn") != None:
                        if int(device) in property["visibleOn"]:
                            self.addProperty(key, property["string"], inputWidget, parent)

                    if property.get("changeState") != None:
                        # store in variables to allow for update function to access
                        changeState = property["changeState"]
                        updateWidget = inputWidget
                        # only works on bool properties for now
                        def update():
                            if self.propertyItems[changeState[0]].isChecked() == changeState[2]:
                                if changeState[1] == "disabled":
                                    updateWidget.setDisabled(False)
                                    updateWidget.setChecked(True)
                                    item.setDisabled(False)
                                elif changeState[1] == "visible":
                                    updateWidget.setChecked(True)
                                    item.setHidden(False)
                            else:
                                if changeState[1] == "disabled":
                                    updateWidget.setDisabled(True)
                                    updateWidget.setChecked(False)
                                    item.setDisabled(True)
                                elif changeState[1] == "visible":
                                    updateWidget.setChecked(False)
                                    item.setHidden(True)

                        item = self.addProperty(key, property["string"], inputWidget, parent, inputSinker)

                        self.propertyItems[changeState[0]].stateChanged.connect(update)
                        update()

                    else:
                        if isinstance(inputWidget, QCheckBox):
                            self.addProperty(key, property["string"], inputWidget, parent, inputSinker)
                        else:
                            self.addProperty(key, property["string"], inputWidget, parent)

                inputWidget = None

    def loadProperties(self, properties, project=None, widgetName=None, resourceList=None, device=None, scrollTo=None):
        self.clearProperties()
        if project == None:
            self.addProperties(properties) # for generic usage (like a config/settings menu)
                                           # make sure if using like this to not use special input fields like numlist
                                           # otherwise will crash, i will add error handling one day
        else:
            self.addProperties(properties["properties"], project, widgetName, resourceList, None, device)
        if scrollTo != None:
            self.treeWidget.scrollContentsBy(0, scrollTo)

    def clearProperties(self):
        for item in self.propertyItems.values():
            item.setParent(None)
        for item in self.imageListCategories:
            item.setParent(None)
        self.treeWidget.clear()
        self.propertyItems = {}