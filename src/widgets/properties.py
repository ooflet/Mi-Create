# Properties Widget for Mi Create
# tostr 2023

# Use a properties "scaffold" with the widget when creating

import sys

sys.path.append("..")

import os
import gettext
import logging
import threading
from typing import Any
from PyQt6.QtWidgets import (QStyledItemDelegate, QWidget, QFileDialog, QTreeWidget, QFrame, QHeaderView, QPushButton,
                               QDialog, QDialogButtonBox, QVBoxLayout, QListWidgetItem, QTreeWidgetItem, QLineEdit, 
                               QSpinBox, QComboBox, QCheckBox, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize, QModelIndex
from PyQt6.QtGui import QColor, QPen, QGuiApplication, QIcon, QPalette, QStandardItemModel
from pprint import pprint

from translate import QCoreApplication

_ = gettext.gettext

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

        self.treeWidgetItems = []
        self.propertyItems = {}
        self.imageListCategories = []
        self.imageFolder = ""
        self.currentPropertyInput = None
        self.resourceList = []

        self.propertyStyleSheet = """
            QLineEdit {
                background-color: rgba(0, 0, 0, 0); 
                border-radius: 0px;
                padding-left: 2px;
            }

            QLineEdit:focus {
                background-color: palette(dark);
                border: 1px solid black;
            }

            QSpinBox {
                background-color: rgba(0, 0, 0, 0); 
                border-radius: 0px;
                padding-left: 2px;
            }

            QSpinBox::up-button {
                background-color: palette(dark);
                subcontrol-position: top right;
                width: 16px;
                border-style: none;
            }

            QSpinBox::up-arrow {
                image: url(:/Dark/up-arrow.png);
                width: 7px;
                height: 7px;
            }
            
            QSpinBox::down-button {
                background-color: palette(dark);
                subcontrol-position: bottom right;
                width: 16px;
                border-style: none;
            }

            QSpinBox::down-arrow {
                image: url(:/Dark/down-arrow.png);
                width: 7px;
                height: 7px;
            }
            
            QSpinBox:focus {
                background-color: palette(dark);
                border: 1px solid black;
            }

            QComboBox {
                background-color: rgba(0, 0, 0, 0); 
                border-radius: 0px;
                padding-left: 2px;
            }

            QComboBox:!editable {
                padding-left: 4px;
            }

            QComboBox::drop-down {
                background-color: palette(dark);
                border-style: none;
                width: 16px;
            }

            QComboBox::down-arrow {
                image: url(:/Dark/down-arrow.png);
                width: 7px;
                height: 7px;
            }

            QComboBox:focus {
                background-color: palette(dark);
                border: 1px solid black;
            }  
        """

        self.sourceList = srcList
        self.sourceData = srcData

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setFrameShape(QFrame.Shape.NoFrame)
        self.treeWidget.setRootIsDecorated(True)
        self.treeWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setUniformRowHeights(True)

        self.treeWidget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.treeWidget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.treeWidget.setHeaderLabels(["Property", "Value"])
        self.treeWidget.setItemDelegate(GridDelegate())
        self.treeWidget.setStyleSheet("QTreeWidget::item{height:24px;}")

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
        self.propertyChanged.emit(property, value)

    def addProperty(self, srcProperty, name, valueWidget, parent=None):
        if parent != None:
            item = QTreeWidgetItem(parent, [_(name), ""])
            self.treeWidget.setItemWidget(item, 1, valueWidget)
            self.propertyItems[srcProperty] = valueWidget
        else:
            item = QTreeWidgetItem()
            item.setText(0, _(name))
            self.treeWidget.addTopLevelItem(item)
            self.treeWidget.setItemWidget(item, 1, valueWidget)
            self.propertyItems[srcProperty] = valueWidget

        item.setExpanded(True)
        return item

    def createLineEdit(self, text, disabled, propertySignalDisabled, srcProperty=""):
        def onDeselect():
            lineEdit.clearFocus()
            self.treeWidget.setCurrentItem(None)
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, lineEdit.text())

        lineEdit = QLineEdit(self)
        lineEdit.setStyleSheet(self.propertyStyleSheet)
        lineEdit.setText(text)
        lineEdit.setDisabled(disabled)
        lineEdit.editingFinished.connect(onDeselect)
        return lineEdit
    
    def createButton(self, text, property):
        def onClick():
            self.sendPropertyChangedSignal(property, "click")

        button = QPushButton(self)
        button.setStyleSheet(self.propertyStyleSheet)
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

        def onChange(event):
            self.sendPropertyChangedSignal(srcProperty, resourceEdit.currentText())

        resourceEdit = QComboBox(self)
        resourceEdit.setEditable(True)
        resourceEdit.setAcceptDrops(True)
        resourceEdit.setStyleSheet(self.propertyStyleSheet)
        resourceEdit.addItems(resourceList)
        resourceEdit.setCurrentText(text)
        resourceEdit.setDisabled(disabled)
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

        spinBox = QSpinBox(self)
        spinBox.setStyleSheet(self.propertyStyleSheet)
        spinBox.setRange(minVal, maxVal)
        if text == None:
            text = "0"
        spinBox.setValue(int(text))
        spinBox.setDisabled(disabled)
        spinBox.valueChanged.connect(onChanged)
        spinBox.editingFinished.connect(onDeselect)
        return spinBox
    
    def createComboBox(self, items, selected, srcProperty, editable):
        def onChanged():
            comboBox.clearFocus()
            self.sendPropertyChangedSignal(srcProperty, comboBox.currentText())

        comboBox = QComboBox(self)
        comboBox.addItems(items)
        comboBox.setStyleSheet(self.propertyStyleSheet)
        if editable:
            comboBox.setEditable(True)
        else:
            comboBox.setCursor(Qt.CursorShape.PointingHandCursor)
        if selected:
            if not selected.isnumeric():
                comboBox.setCurrentIndex(items.index(selected))
            else:
                comboBox.setCurrentIndex(int(selected))
        comboBox.activated.connect(onChanged)
        return comboBox
    
    def createAlignmentComboBox(self, selected, srcProperty):
        items = ["Left", "Center", "Right"]

        def onChanged():
            self.sendPropertyChangedSignal(srcProperty, comboBox.currentText())

        comboBox = QComboBox(self)
        comboBox.addItems(items)
        if selected:
            comboBox.setCurrentIndex(int(selected))
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
        if checked == None or checked == "":
            checked = False
        checkBox.setChecked(checked)
        checkBox.stateChanged.connect(onChecked)
        return checkBox
    
    def createCategory(self, name, parent=None):
        item = QTreeWidgetItem()
        item.setText(0, name)
        if parent:
            parent.addChild(item)  # Add category as a child of the parent category
        else:
            self.treeWidget.addTopLevelItem(item)
        item.setExpanded(True)
        return item

    def addProperties(self, properties, data, resourceList, parent, device):
        for key, property in properties.items():
            if not property.get("string"):
                # category
                categoryItem = self.createCategory(_(key), parent)
                self.addProperties(property, data, resourceList, categoryItem, device)  # Recursively add sub-categories
            else:
                ignorePropertyCreation = False
                # property
                propertyValue = None
                if data != None and data.get(key) != None:
                    propertyValue = data.get(key)
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
                        imageString = f"({stringIndex}):{image}"
                        print(len(imageList), index)
                        if len(imageList) - 1 >= index:
                            imageList[index] = imageString
                        else:
                            imageList.insert(index, imageString)
                        completeString = '|'.join(imageList)
                        self.sendPropertyChangedSignal(key, completeString)

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
                                values = image.split(":")
                                if values[0] != "" and len(values) > 1:
                                    indexInput.setValue(int(values[0].strip("()"))) 
                                    imageInput.setCurrentText(values[1])             
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
                        deleteAllCategories()
                        createImageCategories(imageList, value)

                    ignorePropertyCreation = True
                    imageList = propertyValue.split("|")
                    imageAmountInput = self.createSpinBox(len(imageList), False, True, key, 0, 100)
                    imageAmountInput.textChanged.connect(lambda value=imageAmountInput.value(): updateImageAmount(value))
                    self.addProperty("", "Image Count", imageAmountInput, parent)

                    success, message = createImageCategories(imageList, len(imageList))

                    if not success:
                        QMessageBox.critical(None, "Properties", f"Error occured loading images: {message}")

                elif property["type"] == "numlist":
                    ignorePropertyCreation = True
                    imageList = propertyValue.split("|")

                    def updateNumberList(index, text):
                        if index >= len(imageList):
                            imageList.insert(index, text)
                        else:
                            imageList[index] = text
                        imageString = '|'.join(imageList)
                        self.sendPropertyChangedSignal(key, imageString)

                    def createInput(index, definedText=None):
                        text = ""
                        if index < len(imageList):
                            text = imageList[index]
                        imageInput = self.createResourceEdit(text, False, resourceList, True)
                        if definedText == None:
                            self.addProperty("", "Number "+str(index), imageInput, parent)
                        else:
                            self.addProperty("", definedText, imageInput, parent)
                        imageInput.currentTextChanged.connect(lambda *event, index=index: updateNumberList(index, imageInput.currentText()))

                    for index in range(0, 10):
                        createInput(index)

                    createInput(10, "Negative Sign")

                elif property["type"] == "int":
                    if len(property) < 5:
                        QMessageBox.critical(None, "Properties", f"Int property for {property['string']} requires a min/max val, provided in list 3/4 ")
                    inputWidget = self.createSpinBox(propertyValue, False, False, key, int(property["min"]), int(property["max"]))
                elif property["type"] == "bool":
                    inputWidget = self.createCheckBox(propertyValue, key)
                elif property["type"] == "src":
                    for x in self.sourceData[str(device)]:
                        if propertyValue != '':
                            try:
                                if int(x["@ID"], 0) == int(propertyValue):
                                    inputWidget = self.createComboBox(self.sourceList[str(device)], x["@Name"], key, True)
                                    break
                            except:
                                if int(x["@ID"]) == int(propertyValue):
                                    inputWidget = self.createComboBox(self.sourceList[str(device)], x["@Name"], key, True)
                                    break
                        else:
                            inputWidget = self.createComboBox(self.sourceList[str(device)], False, key, True)
                            break   
                    else:
                        QMessageBox.critical(None, "Properties", f"Data source not found.")
                        inputWidget = self.createComboBox(self.sourceList[str(device)], False, key, True)
                if not ignorePropertyCreation:
                    if property.get("visibleOn") != None:
                        if int(device) in property["visibleOn"]:
                            self.addProperty(key, property["string"], inputWidget, parent)

                    if property.get("enabledOn") != None:
                        # store in variables to allow for update function to access
                        enabledOn = property["enabledOn"]
                        updateWidget = inputWidget
                        # only works on bool properties for now
                        def update():
                            print(enabledOn)
                            if self.propertyItems[enabledOn[0]].isChecked() == enabledOn[1]:
                                updateWidget.setDisabled(False)
                                item.setDisabled(False)
                            else:
                                updateWidget.setDisabled(True)
                                item.setDisabled(True)

                        item = self.addProperty(key, property["string"], inputWidget, parent)
                        self.propertyItems[enabledOn[0]].stateChanged.connect(update)
                        update()

                    else:
                        self.addProperty(key, property["string"], inputWidget, parent)

                inputWidget = None

    def loadProperties(self, properties, data=None, resourceList=None, device=None, scrollTo=None):
        self.clearProperties()
        if data == None:
            self.addProperties(properties, data, resourceList, None, device)
        else:
            self.addProperties(properties["properties"], data, resourceList, None, device)
        if scrollTo != None:
            self.treeWidget.scrollContentsBy(0, scrollTo)

    def clearProperties(self):
        for item in self.propertyItems.values():
            item.setParent(None)
        self.treeWidget.clear()
        self.propertyItems = {}