# Properties Widget for Mi Create
# tostr 2023

# Use a properties "scaffold" with the widget when creating

import sys

sys.path.append("..")

import os
import gettext
import shutil
import traceback
import logging
from typing import Any
from PySide6.QtWidgets import (QStyledItemDelegate, QWidget, QFileDialog, QTreeWidget, QFrame, QHeaderView, 
                               QDialog, QDialogButtonBox, QVBoxLayout, QListWidgetItem, QTreeWidgetItem, QLineEdit, 
                               QSpinBox, QComboBox, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QColor, QPen, QGuiApplication, QIcon, QPalette
from pprint import pprint

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
    propertyChanged = Signal(Any, Any)
    def __init__(self, window, resourceWidget=None, srcList=None, srcData=None, screen=None):
        super().__init__()

        self.clearOnRefresh = True

        def closeResourceDialog():
            self.currentPropertyInput.setText(self.resourceDialogUI.imageSelect.currentItem().text())
            self.resourceDialog.close()

        def addResource():
            file = QFileDialog.getOpenFileName(self, 'Open Image...', "%userprofile%\\", "Image File (*.png *.jpeg *.bmp)")
            if file[0]:
                shutil.copyfile(file[0], os.path.join(self.imageFolder, os.path.basename(file[0])))
                self.reloadResourceImages()
                self.currentPropertyInput.setText(os.path.basename(file[0]))

        def search():
            filter_text = self.resourceDialogUI.searchBar.text()
            visible_items = []
            for x in range(self.resourceDialogUI.imageSelect.count()): 
                item = self.resourceDialogUI.imageSelect.item(x)
                if filter_text.lower() in item.text().lower():
                    item.setHidden(False)
                    visible_items.append(x)
                else:
                    item.setHidden(True)
            if filter_text != "":
                self.resourceDialogUI.imageSelect.setCurrentRow(visible_items[0])
            else:
                [self.resourceDialogUI.imageSelect.setCurrentItem(x) for x in self.resourceDialogUI.imageSelect.findItems(self.currentPropertyInput.text(), Qt.MatchExactly)]

        self.propertyItems = {}
        self.imageListCategories = []
        self.imageFolder = ""
        self.currentPropertyInput = None

        self.sourceList = srcList
        self.sourceData = srcData
        self.primaryScreen = screen

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setFrameShape(QFrame.NoFrame)
        self.treeWidget.setRootIsDecorated(True)
        self.treeWidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setUniformRowHeights(True)

        self.treeWidget.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.treeWidget.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.treeWidget.header().resizeSection(0, 145)
        self.treeWidget.setHeaderLabels(["Property", "Value"])
        self.treeWidget.setItemDelegate(GridDelegate())
        self.treeWidget.setStyleSheet("QTreeWidget::item{height:24px;}")

        if resourceWidget != None:
            self.resourceDialog = QDialog(window)
            self.resourceDialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
            self.resourceDialogUI = resourceWidget()
            self.resourceDialogUI.setupUi(self.resourceDialog)
            self.resourceDialogUI.searchBar.textChanged.connect(search)
            self.resourceDialogUI.addImage.clicked.connect(addResource)
            apply = self.resourceDialogUI.buttonBox.button(QDialogButtonBox.Apply)
            apply.clicked.connect(closeResourceDialog)

        layout = QVBoxLayout(self)
        layout.addWidget(self.treeWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    @staticmethod
    def loadLanguage(language):
        translation = gettext.translation('properties', localedir='locales', languages=[language])
        translation.install()
        global _
        _ = translation.gettext

    def reloadResourceImages(self):
        self.resourceDialogUI.imageSelect.clear()
        for filename in os.listdir(self.imageFolder):
            file = os.path.join(self.imageFolder, filename)
            if os.path.isfile(file):
                logging.debug("Creating file entry for "+os.path.basename(file))
                item = QListWidgetItem(QIcon(file), os.path.basename(file))
                item.setSizeHint(QSize(item.sizeHint().width(), 64))
                self.resourceDialogUI.imageSelect.addItem(item)
    
    def sendPropertyChangedSignal(self, property, value):
        self.propertyChanged.emit(property, value)

    def addProperty(self, srcProperty, name, valueWidget, parent):
        item = QTreeWidgetItem(parent, [_(name), ""])
        self.treeWidget.setItemWidget(item, 1, valueWidget)
        self.propertyItems[srcProperty] = valueWidget
        item.setExpanded(True)

    def createLineEdit(self, text, disabled, propertySignalDisabled, srcProperty=""):
        def onDeselect():
            lineEdit.clearFocus()
            self.treeWidget.setCurrentItem(None)
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, lineEdit.text())

        lineEdit = QLineEdit(self)
        lineEdit.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        lineEdit.setText(text)
        lineEdit.setDisabled(disabled)
        lineEdit.editingFinished.connect(onDeselect)
        return lineEdit
    
    def createResourceEdit(self, text, disabled, propertySignalDisabled, srcProperty=""):
        def onSelect():
            screenX = self.primaryScreen.size().width()
            screenY = self.primaryScreen.size().height()
            posX = resourceEdit.mapToGlobal(QPoint(0,22)).x() - 150
            posY = resourceEdit.mapToGlobal(QPoint(0,22)).y()
            if posX + 300 > screenX:
                posX = posX - ((posX + 300) - screenX)
            if posY + 325 > screenY:
                posY = posY - 325
            resourceEdit.clearFocus()
            self.currentPropertyInput = resourceEdit
            self.resourceDialog.setGeometry(posX, posY, 300, 325)
            [self.resourceDialogUI.imageSelect.setCurrentItem(x) for x in self.resourceDialogUI.imageSelect.findItems(resourceEdit.text(), Qt.MatchExactly)]
            self.resourceDialogUI.searchBar.setFocus()
            self.resourceDialog.exec()

        def onDeselect():
            resourceEdit.clearFocus()
            self.treeWidget.setCurrentItem(None)  

        resourceEdit = QLineEdit(self)
        resourceEdit.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        resourceEdit.setText(text)
        resourceEdit.setDisabled(disabled)
        resourceEdit.mousePressEvent = lambda event: onSelect()
        if not propertySignalDisabled:
            resourceEdit.textChanged.connect(lambda *event: self.sendPropertyChangedSignal(srcProperty, resourceEdit.text()))
        return resourceEdit

    def createSpinBox(self, text, disabled, propertySignalDisabled, srcProperty, minVal=-9999, maxVal=9999):
        def onChanged():
            if not propertySignalDisabled:
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
    
    def createComboBox(self, items, selected, srcProperty, editable):
        def onChanged():
            self.sendPropertyChangedSignal(srcProperty, comboBox.currentText())

        comboBox = QComboBox(self)
        comboBox.addItems(items)
        if editable:
            comboBox.setEditable(True)
            comboBox.setStyleSheet("background-color: rgba(0, 0, 0, 0); ")
        if selected:
            if not selected.isnumeric():
                comboBox.setCurrentIndex(items.index(selected))
            else:
                comboBox.setCurrentIndex(int(selected))
        comboBox.currentTextChanged.connect(onChanged)
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

    def addCategories(self, properties, data, parent, device):
        for key, value in properties.items():
            if isinstance(value, dict):
                # category
                categoryItem = self.createCategory(_(key), parent)
                self.addCategories(value, data, categoryItem, device)  # Recursively add sub-categories
            else:
                ignorePropertyCreation = False
                # property
                propertyValue = None
                if data != None and data.get(key) != None:
                    propertyValue = data.get(key)
                else:
                    propertyValue = value[2]
                inputWidget = None
                
                if value[1] == "disabled":
                    inputWidget = self.createLineEdit(propertyValue, True, False, key)
                elif value[1] == "text":
                    inputWidget = self.createLineEdit(propertyValue, False, False, key)
                elif value[1] == "img":
                    inputWidget = self.createResourceEdit(propertyValue, False, False, key)
                elif value[1] == "combobox":
                    inputWidget = self.createComboBox(value[3], propertyValue, key, False)
                elif value[1] == "imglist":
                    self.imageCategories = []

                    def imagesChanged(stringIndex, image, index):
                        print("img change")
                        imageString = f"({stringIndex}):{image}"
                        if len(imageList) <= index:
                            image[index] = imageString
                        else:
                            imageList.insert(index, imageString)
                        completeString = '|'.join(imageList)
                        self.sendPropertyChangedSignal(key, completeString)

                    def createImageCategories(imageList, imageCount):
                        for index in range(0, imageCount):
                            imageCategory = self.createCategory("Image"+str(index), parent)
                            imageInput = self.createResourceEdit("", False, True, key)
                            indexInput = self.createSpinBox(None, False, True, key)
                            self.addProperty("", "Image", imageInput, imageCategory)
                            self.addProperty("", "Index", indexInput, imageCategory)
                            self.imageCategories.append([imageCategory, imageInput, indexInput])

                            print(len(imageList), index)
                            if len(imageList) - 1 > index:
                                print("more")
                                image = imageList[index]
                                values = image.split(":")
                                try:
                                    indexInput.setValue(int(values[0].strip("()"))) 
                                    imageInput.setText(values[1])             
                                    imageInput.textChanged.connect(lambda text, indexInput=self.imageCategories[index][2], index=index: imagesChanged(indexInput.text(), text, index))
                                    indexInput.textChanged.connect(lambda text, imageInput=self.imageCategories[index][1], index=index: imagesChanged(text, imageInput.text(), index))
                                except Exception as e:
                                    print(traceback.format_exc())
                                    return False, traceback.format_exc()
                            else:
                                print("less")
                                imageInput.textChanged.connect(lambda text, indexInput=self.imageCategories[index][2], index=index: imagesChanged(indexInput.text(), text, index))
                                indexInput.textChanged.connect(lambda text, imageInput=self.imageCategories[index][1], index=index: imagesChanged(text, imageInput.text(), index))
 
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

                elif value[1] == "numlist":
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
                        imageInput = self.createResourceEdit(text, False, True)
                        if definedText == None:
                            self.addProperty("", "Number "+str(index), imageInput, parent)
                        else:
                            self.addProperty("", definedText, imageInput, parent)
                        imageInput.textChanged.connect(lambda text, index=index: updateNumberList(index, text))

                    for index in range(0, 10):
                        createInput(index)

                    createInput(10, "Negative Sign")

                elif value[1] == "int":
                    inputWidget = self.createSpinBox(propertyValue, False, False, key, int(value[3]), int(value[4]))
                elif value[1] == "bool":
                    inputWidget = self.createCheckBox(propertyValue, key)
                elif value[1] == "src":
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
                if not ignorePropertyCreation:
                    self.addProperty(key, value[0], inputWidget, parent)
                inputWidget = None

    def loadProperties(self, properties, data=None, device=None, scrollTo=None):
        self.treeWidget.clear()
        self.propertyItems = {}
        if data == None:
            self.addCategories(properties, data, None, device)
        else:
            self.addCategories(properties["properties"], data, None, device)
        if scrollTo != None:
            self.treeWidget.scrollContentsBy(0, scrollTo)

    def clearProperties(self):
        self.treeWidget.clear()