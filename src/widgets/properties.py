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

from PyQt6.QtWidgets import (QStackedWidget, QStyledItemDelegate, QWidget, QFileDialog, QTreeWidget, QFrame, QHeaderView, QPushButton,
                               QHBoxLayout, QVBoxLayout, QScrollArea, QTreeWidgetItem, QLineEdit, QSizePolicy, QToolButton,
                               QSpinBox, QComboBox, QLabel, QCheckBox, QMessageBox, QAbstractItemView, QApplication, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize, QModelIndex
from PyQt6.QtGui import QColor, QPen, QPixmap, QIcon, QPalette, QStandardItemModel, QFontMetrics, QPainter
from pprint import pprint

from widgets.switch import SwitchControl
from widgets.layouts import FlowLayout
from utils.translate import Translator

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

class PropertiesFileEntry(QStackedWidget):
    def __init__(self, src, changeSignal, imageUploadFunction, propertyName=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("imageEntry")

        self.src = src
        self.propertyChanged = changeSignal

        # no image set

        def mousePress(event):
            imageUploadFunction()
            return QFrame.mousePressEvent(self.placeholderWidget, event)
        
        self.placeholderWidget = QFrame()
        self.placeholderWidget.mousePressEvent = mousePress
        self.placeholderWidget.setAcceptDrops(True) 
        self.placeholderWidget.setCursor(Qt.CursorShape.PointingHandCursor)

        self.placeholderLayout = QVBoxLayout(self.placeholderWidget)
        self.placeholderLayout.setSpacing(2)

        self.placeholderIcon = QLabel()
        self.placeholderIcon.setPixmap(QIcon().fromTheme("insert-image").pixmap(24, 24))
        self.placeholderIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if propertyName and propertyName != "Image":
            self.placeholderText = QLabel(f'Set {propertyName} Image')
        else:
            self.placeholderText = QLabel(f'Set Image')

        self.placeholderText.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.placeholderLayout.addStretch()
        self.placeholderLayout.addWidget(self.placeholderIcon)
        self.placeholderLayout.addWidget(self.placeholderText)
        self.placeholderLayout.addStretch()

        # image preview

        self.itemWidget = QWidget()
        self.itemLayout = QHBoxLayout(self.itemWidget)
        #self.itemLayout.setContentsMargins(0, 0, 0, 0)
        self.itemLayout.setSpacing(10)

        self.icon = QLabel()
        self.icon.setObjectName("imageFrame")
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setFixedSize(48, 48)

        self.labelLayout = QVBoxLayout()
        self.labelLayout.setSpacing(2)
        self.label = QLabel("Image")
        #self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.label.setMaximumWidth(160)
        self.sizeLabel = QLabel("0x0")
        self.sizeLabel.setStyleSheet("color: palette(light)")
        
        self.labelLayout.addStretch()
        self.labelLayout.addWidget(self.label)
        self.labelLayout.addWidget(self.sizeLabel)
        self.labelLayout.addStretch()

        self.deleteBtn = QToolButton()
        self.deleteBtn.setIcon(QIcon.fromTheme("application-close"))
        self.deleteBtn.setToolTip("Remove")
        self.deleteBtn.clicked.connect(self.removeImage)

        self.itemLayout.addWidget(self.icon)
        self.itemLayout.addLayout(self.labelLayout)
        self.itemLayout.addStretch()
        self.itemLayout.addWidget(self.deleteBtn)

        self.addWidget(self.placeholderWidget)
        self.addWidget(self.itemWidget)

        self.setCurrentWidget(self.placeholderWidget)

        self.setFixedHeight(self.itemLayout.sizeHint().height())
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def sendPropertyChangedSignal(self, property, value):
        self.propertyChanged.emit(property, value)

    def removeImage(self):
        self.setProperty("invalid", False)
        self.sendPropertyChangedSignal(self.src, "")
        self.updateStyle()

    def loadImage(self, name, pixmap):
        if name:
            self.setCurrentWidget(self.itemWidget)
            self.label.setText(name)
            self.label.setToolTip(name)
            self.icon.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            if pixmap.isNull():
                print("null!!! shoudl update!!!!")
                self.setProperty("invalid", True)
            else:
                self.setProperty("invalid", False)
            self.updateStyle()
            self.sizeLabel.setText(f"{pixmap.width()}x{pixmap.height()}")
        else:
            self.setCurrentWidget(self.placeholderWidget)

    def updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def updateIconStyle(self):
        self.icon.style().unpolish(self.icon)
        self.icon.style().polish(self.icon)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            self.setProperty("selected", True)
            self.updateStyle()
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            self.setProperty("selected", True)
            self.updateStyle()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setProperty("selected", False)
        self.updateStyle()

    def dropEvent(self, event):
        model = QStandardItemModel()
        model.dropMimeData(event.mimeData(), Qt.DropAction.CopyAction, 0, 0, QModelIndex())
        self.setProperty("selected", False)
        self.updateStyle()

        image = model.item(0, 0).data(100)

        self.sendPropertyChangedSignal(self.src, image)

        event.acceptProposedAction()

class PropertiesMultiFileItem(QFrame):
    dropped = pyqtSignal(object)
    removed = pyqtSignal()
    def __init__(self, label, editable=True, propertyName=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(65)
        self.setObjectName("imageEntry")
        self.setAcceptDrops(True)

        self.set = False
        self.pixmap = None
        self.editable = editable

        self.itemLayout = QVBoxLayout(self)
        self.itemLayout.setContentsMargins(4, 4, 4, 4)
        self.itemLayout.setSpacing(4)
        self.image = QLabel()
        self.image.setFixedSize(55, 55)
        self.image.setObjectName("imageFrame")
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.editable:
            self.label = QSpinBox()
            self.label.setStyleSheet("background: transparent; border: none; padding: 0px;")
            self.label.setRange(-2147483647, 2147483647) # max numbers
            self.label.setValue(int(label))
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.wheelEvent = lambda event: event.ignore()
        else:
            self.label = QLabel(str(label))
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.itemLayout.addWidget(self.image)
        self.itemLayout.addWidget(self.label)
        self.itemLayout.addStretch()

        self.setFixedHeight(self.sizeHint().height())

        self.removeButton = QToolButton(self)
        self.removeButton.setIcon(QIcon.fromTheme("application-close"))  # Replace with your desired icon
        self.removeButton.setAutoRaise(True)
        self.removeButton.resize(30, 30)
        self.removeButton.move(int(self.width() / 2 - self.removeButton.width() / 2), int(self.image.height() / 2 - self.removeButton.height() / 2 + 4))
        self.removeButton.clicked.connect(self.removeClicked)
        self.removeButton.hide()

    def removeClicked(self):
        self.removed.emit()
        self.set = False
        self.removeButton.hide()

    def loadImage(self, path):
        if path:
            self.unsetCursor()
            self.set = True
        else:
            self.pixmap = None
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.set = False
            self.image.setPixmap(QIcon().fromTheme("insert-image").pixmap(24, 24))
            self.setProperty("invalid", False)
            self.updateStyle()
            return

        pixmap = QPixmap(path).scaled(55, 55, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        if pixmap.isNull():
            print("null!!! shoudl update!!!!")
            self.setProperty("invalid", True)
        else:
            self.setProperty("invalid", False)

        self.updateStyle()
        self.pixmap = pixmap
        self.imagePath = path
        self.image.setPixmap(pixmap)

    def updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def makeTransparentPixmap(self, pixmap, opacity):
        transparent = QPixmap(pixmap.size())
        transparent.fill(Qt.GlobalColor.transparent)

        painter = QPainter(transparent)
        painter.setOpacity(opacity)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return transparent

    def enterEvent(self, event):
        if self.set:
            transparentPixmap = self.makeTransparentPixmap(self.pixmap, 0.15)
            self.image.setPixmap(transparentPixmap)
            self.removeButton.show()

    def leaveEvent(self, event):
        if self.set:
            self.image.setPixmap(self.pixmap)
        self.removeButton.hide()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            self.setProperty("selected", True)
            self.updateStyle()
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            self.setProperty("selected", True)
            self.updateStyle()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setProperty("selected", False)
        self.updateStyle()

    def dropEvent(self, event):
        model = QStandardItemModel()
        model.dropMimeData(event.mimeData(), Qt.DropAction.CopyAction, 0, 0, QModelIndex())
        self.setProperty("selected", False)
        self.updateStyle()

        image = model.item(0, 0).data(100)

        if self.editable:
            self.dropped.emit([self.label.text(), image])
        else:
            self.dropped.emit(image)

        event.acceptProposedAction()

class PropertiesMultiFileEntry(QFrame):
    propertyChanged = pyqtSignal(str, list)
    def __init__(self, src, editable, propertyName=None, parent=None):
        super().__init__(parent)
        self.itemLayout = FlowLayout(self)
        self.src = src
        self.data = None
        self.editable = editable
        self.fileItems = []
        
    def setItems(self, items):
        self.itemLayout.clear()
        self.fileItems.clear()
        for index, item in enumerate(items):
            fileItem = PropertiesMultiFileItem(item, self.editable)
            fileItem.dropped.connect(lambda image, index=index: self.setImage(index, image))
            fileItem.removed.connect(lambda index=index: self.removeImage(index))
            self.itemLayout.addWidget(fileItem)
            self.fileItems.append(fileItem)

    def loadImages(self, images, imageFolder, setData=True):
        if setData:
            self.data = images

        for index, widget in enumerate(self.fileItems):
            print(len(images), index)
            if len(images) <= index:   
                widget.loadImage(None)
            else:
                if images[index]:
                    path = os.path.join(imageFolder, images[index])
                    widget.loadImage(path)
                else:
                    widget.loadImage(None)

    def loadImageList(self, imageList, imageFolder):
        self.data = imageList
        indexes, images = zip(*imageList)

        indexes = list(indexes)
        images = list(images)

        self.setItems(indexes)
        self.loadImages(images, imageFolder, False)

    def setImage(self, index, item):
        if index < len(self.data):
            self.data[index] = item
        else:
            self.data.extend([""] * (index - len(self.data)))
            self.data.append(item)

        self.propertyChanged.emit(self.src, self.data)

    def removeImage(self, index):
        self.data[index] = ""
        self.propertyChanged.emit(self.src, self.data)

class PropertiesWidget(QStackedWidget):
    propertyChanged = pyqtSignal(object, object)
    def __init__(self, parent, properties, widgetProperties=False, imageUploadFunction=None, srcList=None, srcData=None):
        super().__init__(parent)

        metrics = QFontMetrics(self.font())
        height_px = metrics.height()

        self.entryHeight = height_px + 12
        self.entryWidth = 145
        self.clearOnRefresh = True
        self.ignorePropertyChange = False

        self.properties = {}

        self.imageUploadFunction = imageUploadFunction

        self.sourceList = srcList
        self.sourceData = srcData

        self.setupProperties(properties, widgetProperties)

    def loadLanguage(self, language):
        translation = gettext.translation('properties', localedir='locales', languages=[language])
        translation.install()
        global _
        _ = translation.gettext

    def sendPropertyChangedSignal(self, property, value):
        if not self.ignorePropertyChange:
            self.propertyChanged.emit(property, value)

    def createLineEdit(self, text, disabled, propertySignalDisabled, srcProperty=""):
        def onDeselect():
            lineEdit.clearFocus()
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, lineEdit.text())

        lineEdit = QLineEdit(self)
        lineEdit.setText(str(text))
        lineEdit.setDisabled(disabled)
        lineEdit.editingFinished.connect(onDeselect)
        lineEdit.setFixedHeight(self.entryHeight)
        lineEdit.setFixedWidth(self.entryWidth)

        return lineEdit
    
    def createSpinBox(self, text, min, max, disabled, propertySignalDisabled, srcProperty=""):
        def onChange():
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, spinBox.value())

        def onDeselect():
            spinBox.clearFocus()

        def wheelEvent(event):
            event.ignore() # disable wheel event completely

        spinBox = QSpinBox(self)
        spinBox.setDisabled(disabled)
        spinBox.wheelEvent = wheelEvent
        spinBox.valueChanged.connect(onChange)
        spinBox.editingFinished.connect(onDeselect)
        spinBox.setFixedHeight(self.entryHeight)
        spinBox.setFixedWidth(self.entryWidth)
              
        if min and min != "none":
            min = int(min)
        else:
            min = -2147483647

        if max and max != "none":
            max = int(max)
        else:
            max = 2147483647

        if not text:
            text = "0"

        spinBox.setRange(min, max)
        spinBox.setValue(int(text))

        return spinBox
    
    def createToggleSwitch(self, toggled, disabled, propertySignalDisabled, srcProperty=""):
        def onToggle():
            if not propertySignalDisabled:
                self.sendPropertyChangedSignal(srcProperty, str(int(toggleSwitch.isChecked())))

        toggleSwitch = SwitchControl(self)

        try:
            toggleSwitch.setChecked(bool(int(toggled)))
        except (ValueError, TypeError):
            toggleSwitch.setChecked(False)

        toggleSwitch.setDisabled(disabled)
        toggleSwitch.toggled.connect(onToggle)

        return toggleSwitch
    
    def createCombobox(self, text, list, editable, disabled, propertySignalDisabled, srcProperty=""):
        def onChange():
            combobox.clearFocus()
            self.sendPropertyChangedSignal(srcProperty, combobox.currentText())

        def wheelEvent(event):
            event.ignore() # disable wheel event completely

        combobox = QComboBox(self)
        combobox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        combobox.addItems(list)
        combobox.setEditable(editable)
        combobox.setDisabled(disabled)
        combobox.setFixedHeight(self.entryHeight)
        combobox.setFixedWidth(self.entryWidth)
        combobox.wheelEvent = wheelEvent
        combobox.activated.connect(onChange)

        if text:
            combobox.setCurrentText(text)
        else:
            combobox.setCurrentIndex(0)

        return combobox

    def createStrEdit(self, label, value, srcProperty, disabled):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyLabel = QLabel(label)
        propertyEdit = self.createLineEdit(value, disabled, False, srcProperty)

        layout.addWidget(propertyLabel)
        layout.addStretch()
        layout.addWidget(propertyEdit)

        return propertyEdit, widget
    
    def createIntEdit(self, label, value, min, max, src, disabled):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyLabel = QLabel(label)
        propertyEdit = self.createSpinBox(value, min, max, disabled, False, src)

        layout.addWidget(propertyLabel)
        layout.addStretch()
        layout.addWidget(propertyEdit)

        return propertyEdit, widget

    def createSlider(self, label, value, min, max, src, disabled):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyLabel = QLabel(label)
        
        propertyEdit = self.createSpinBox(value, min, max, disabled, False, src)
        propertyEdit.setFixedWidth(int(self.entryWidth * 3 / 8) - 3) # take up 3/8 of space

        def wheelEvent(event):
            event.ignore() # disable wheel event completely

        propertySlider = QSlider(Qt.Orientation.Horizontal)
        propertySlider.setRange(int(min), int(max))
        propertySlider.setTickInterval(int(max) - int(min))
        propertySlider.setValue(int(value))
        propertySlider.setFixedWidth(int(self.entryWidth * 5 / 8) - 3) # take up 5/8 of space
        propertySlider.wheelEvent = wheelEvent

        propertyEdit.valueChanged.connect(lambda value: propertySlider.setValue(int(value)))
        propertySlider.valueChanged.connect(lambda value: propertyEdit.setValue(int(value)))

        layout.addWidget(propertyLabel)
        layout.addStretch()
        layout.addWidget(propertySlider)
        layout.addWidget(propertyEdit)

        return propertyEdit, widget
    
    def createBoolEdit(self, label, value, srcProperty, disabled):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0,4,0,4)
        propertyLabel = QLabel(label)
        propertyEdit = self.createToggleSwitch(value, disabled, False, srcProperty)

        layout.addWidget(propertyLabel)
        layout.addStretch()
        layout.addWidget(propertyEdit)

        return propertyEdit, widget
    
    def createSrcEdit(self, label, value, src, disabled):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyLabel = QLabel(label)

        propertyEdit = self.createCombobox("Data Source", [], True, disabled, False, src)

        layout.addWidget(propertyLabel)
        layout.addStretch()
        layout.addWidget(propertyEdit)

        return propertyEdit, widget

    def loadSrcEdit(self, combobox, value, device):
        source_items = self.sourceData[str(device)]
        source_list = self.sourceList[str(device)]
        source_item = None

        if value != '':
            for x in source_items:
                match = False

                # handle hex src values
                if not value:
                    match = x["id_fprj"] == value
                elif isinstance(value, int) or value.isnumeric():
                    match = int(x["id_fprj"]) == int(value)
                else:
                    match = x["id_fprj"] == value

                if match:
                    source_item = x["string"]
                    break

        combobox.addItems(source_list)

        if source_item:
            combobox.setCurrentText(source_item)
        else:
            combobox.setCurrentIndex(0)

    def createListEdit(self, label, value, options, src, disabled):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyLabel = QLabel(label)
        propertyEdit = self.createCombobox(value, options, False, disabled, False, src)

        layout.addWidget(propertyLabel)
        layout.addStretch()
        layout.addWidget(propertyEdit)

        return propertyEdit, widget
    
    def createImgEdit(self, label, src, imageUploadFunction):
        def addImgResource():
            image = imageUploadFunction(ignoreCanvasReload=True, openInResourceFolder=True)
            if image:
                print(image)
                self.sendPropertyChangedSignal(src, image)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyEdit = PropertiesFileEntry(src, self.propertyChanged, addImgResource, label)

        layout.addWidget(propertyEdit)

        return propertyEdit, widget

    def createNumEdit(self, src, imageUploadFunction):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyEdit = PropertiesMultiFileEntry(src, False)
        propertyEdit.setItems([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "Minus"])
        propertyEdit.propertyChanged.connect(self.sendPropertyChangedSignal)

        layout.addWidget(propertyEdit)

        return propertyEdit, widget
    
    def createImgListEdit(self, src, imageUploadFunction):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        propertyEdit = PropertiesMultiFileEntry(src, True)
        propertyEdit.propertyChanged.connect(self.sendPropertyChangedSignal)

        layout.addWidget(propertyEdit)

        return propertyEdit, widget

    def createButton(self, text, disabled, property):
        def onClick():
            self.sendPropertyChangedSignal(property, "click")

        button = QPushButton(self)
        button.setText(text)
        button.setDisabled(disabled)
        button.clicked.connect(onClick)
        return button

    def createCheckBox(self, checked, disabled, srcProperty, propertySignalDisabled=False):
        def onChecked():
            self.sendPropertyChangedSignal(srcProperty, checkBox.isChecked())

        checkBox = QCheckBox()
        if checked == None or checked == "":
            checked = False
        checkBox.setChecked(checked)
        checkBox.setDisabled(disabled)
        if propertySignalDisabled == False:
            checkBox.stateChanged.connect(onChecked)
        return checkBox
    
    def createCategory(self, parent, name: str, seperator: bool) -> QVBoxLayout:
        layout = QVBoxLayout()

        if seperator:
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(line)

        category = QLabel(name.upper())
        category.setObjectName("propertyHeader")
        layout.addWidget(category)

        return layout

    def addProperty(self, layout: QVBoxLayout, propertyLayout):
        propertyItemLayout = QHBoxLayout()
        propertyText = QLabel(_(property))
        propertyItemLayout.addWidget(propertyText)
        propertyItemLayout.addLayout(propertyLayout)

        layout.addLayout(propertyItemLayout)
    
    def addProperties(self, propertiesList, parent, properties):
        for key, property in properties.items():
            if not property.get("string"): # category
                category = self.createCategory(parent, _(key), True)
                parent.addLayout(category)
                self.addProperties(propertiesList, category, property)
            else:
                propertyValue = property["value"]
                propertyDisabled = False

                if property.get("disabled") and property["disabled"] == "true":
                    propertyDisabled = True

                if property["type"] == "str":
                    propertyWidget, propertyLayout = self.createStrEdit(property["string"], propertyValue, key, propertyDisabled)
                elif property["type"] == "btn":
                    propertyWidget, propertyLayout = self.createButton(propertyValue, propertyDisabled, key)
                elif property["type"] == "img":
                    propertyWidget, propertyLayout = self.createImgEdit(property["string"], key, self.imageUploadFunction)
                elif property["type"] == "slider":
                    propertyWidget, propertyLayout = self.createSlider(property["string"], propertyValue, property["min"], property["max"], key, propertyDisabled)
                elif property["type"] == "list":
                    propertyWidget, propertyLayout = self.createListEdit(property["string"], propertyValue, property["options"], key, propertyDisabled)
                elif property["type"] == "imglist":
                    propertyWidget, propertyLayout = self.createImgListEdit(key, None)
                elif property["type"] == "numlist":
                    propertyWidget, propertyLayout = self.createNumEdit(key, None)
                elif property["type"] == "int":
                    propertyWidget, propertyLayout = self.createIntEdit(property["string"], propertyValue, property.get("min"), property.get("max"), key, propertyDisabled)
                elif property["type"] == "bool":
                    propertyWidget, propertyLayout = self.createBoolEdit(property["string"], propertyValue, key, propertyDisabled)
                elif property["type"] == "src":
                    propertyWidget, propertyLayout = self.createSrcEdit(property["string"], propertyValue, key, propertyDisabled)

                propertiesList[key] = {
                    "property_data": property, 
                    "type": property["type"], 
                    "layout": propertyLayout,
                    "widget": propertyWidget
                }

                parent.addWidget(propertyLayout)

    def setupProperties(self, properties: dict, usingWidgetProperties: bool):
        emptyPage = QWidget()
        self.properties["none"] = {
            "widget": emptyPage,
            "widgetContainer": emptyPage,
            "propertyWidgets": {}
        }
        self.addWidget(emptyPage)

        if usingWidgetProperties:
            for widget, widgetProperties in properties.items():
                scroll = QScrollArea()
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                scroll.setWidgetResizable(True)

                propertiesWidget = QWidget()
                propertiesLayout = QVBoxLayout()
                propertiesWidget.setLayout(propertiesLayout)

                # Prevent it from expanding beyond its parent
                propertiesWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
                scroll.setWidget(propertiesWidget)

                print()

                self.properties[widget] = {
                    "widget": scroll,
                    "widgetContainer": propertiesWidget,
                    "propertyWidgets": {}
                }

                self.addProperties(self.properties[widget]["propertyWidgets"], propertiesLayout, widgetProperties["properties"])
                propertiesLayout.addStretch()
                self.addWidget(scroll)

        else:
            propertiesWidget = QWidget()
            propertiesLayout = QVBoxLayout()
            propertiesWidget.setLayout(propertiesLayout)
            self.properties = {}
            self.addProperties(self.properties, propertiesLayout, properties)
            self.addWidget(propertiesWidget)

    def changePropertiesPage(self, category):
        self.setCurrentWidget(self.properties[category]["widget"])
        for key, property in self.properties.items():
            print(category)
            if key == category:
                property["widget"].setVisible(True)
            else:
                property["widget"].setVisible(False)

    def loadProperties(self, category, values=None, widget=None, project=None):
        if not category:
            self.changePropertiesPage("none")
            return

        self.ignorePropertyChange = True
        self.changePropertiesPage(category)
        for property, propertyWidget in self.properties[category]["propertyWidgets"].items():
            if widget != None:
                value = widget.getProperty(property)
            else:
                value = values.get(property)

            currentDevice = project.getDeviceType()

            # handle visibleOn property

            if propertyWidget["property_data"].get("visibleOn"):
                print(propertyWidget["property_data"].get("visibleOn"))
                if currentDevice not in propertyWidget["property_data"]["visibleOn"]:
                    print("nope!")
                    propertyWidget["layout"].setVisible(False)
                else:
                    propertyWidget["layout"].setVisible(True)

            # set value

            if propertyWidget["type"] == "str":
                propertyWidget["widget"].setText(value)

            elif propertyWidget["type"] == "bool":
                try:
                    propertyWidget["widget"].setChecked(bool(int(value)))
                except (ValueError, TypeError):
                    propertyWidget["widget"].setChecked(False)
                propertyWidget["widget"].update_circle_position(propertyWidget["widget"].isChecked())

            elif propertyWidget["type"] == "list":
                propertyWidget["widget"].setCurrentText(str(value))

            elif propertyWidget["type"] == "int":
                propertyWidget["widget"].setValue(int(value))

            elif propertyWidget["type"] == "src":
                self.loadSrcEdit(propertyWidget["widget"], value, currentDevice)
                
            elif propertyWidget["type"] == "img":
                propertyWidget["widget"].loadImage(value, QPixmap(os.path.join(project.getImageFolder(), value)))

            elif propertyWidget["type"] == "numlist":
                propertyWidget["widget"].loadImages(value, project.getImageFolder())

            elif propertyWidget["type"] == "imglist":
                propertyWidget["widget"].loadImageList(value, project.getImageFolder())


        self.ignorePropertyChange = False

    def clearProperties(self):
        self.changePropertiesPage("none")

    def resizeEvent(self, a0):
        for widget in self.properties.values():
            print(widget)
            widget["widgetContainer"].setMaximumWidth(self.width())
        print(self.width())
        return super().resizeEvent(a0)

class LegacyPropertiesWidget(QWidget):
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
        # self.searchWidget.setPlaceholderText(Translator.translate("MainWindow", "Search..."))

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

        if minVal != "none":
            spinBox.setMinimum(int(minVal))
        else:
            spinBox.setMinimum(-2147483647) # max int32 signed integer

        if maxVal != "none":
            spinBox.setMaximum(int(maxVal))
        else:
            spinBox.setMaximum(2147483647)

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
            if isinstance(selected, int) or selected.isnumeric():
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
            comboBox.setItemText(selected)
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
                                if image != None and len(image) > 1 and isinstance(image, list) and image[0] != "":
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
                    imageAmountInput = self.createSpinBox(len(propertyValue), False, True, key, 0, 9999)
                    imageAmountInput.textChanged.connect(lambda value=imageAmountInput.value(): updateImageAmount(value))
                    self.addProperty("", "Image Count", imageAmountInput, parent)

                    success, message = createImageCategories(propertyValue, len(propertyValue))

                    if not success:
                        QMessageBox.critical(None, "Properties", f"Error occured loading images: {message}")

                elif property["type"] == "numlist":
                    ignorePropertyCreation = True

                    decimalList = []

                    checked = False

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
                        QMessageBox.critical(None, "Properties", f"Int property for {property['string']} requires a min/max val or 'none'")
                    inputWidget = self.createSpinBox(propertyValue, False, False, key, property["min"], property["max"])
                elif property["type"] == "bool":
                    inputSinker, inputWidget = self.createCheckBox(propertyValue, key)
                elif property["type"] == "src":
                    for x in self.sourceData[str(device)]:
                        if propertyValue != '':
                            if isinstance(propertyValue, int) or propertyValue.isnumeric():
                                if int(x["id_fprj"]) == int(propertyValue):
                                    inputWidget = self.createComboBox(self.sourceList[str(device)], x["string"], key, True)
                                    break
                            else:
                                if x["id_fprj"] == propertyValue:
                                    inputWidget = self.createComboBox(self.sourceList[str(device)], x["string"], key, True)
                                    break
                        else:
                            inputWidget = self.createComboBox(self.sourceList[str(device)], False, key, True)
                            break   

                    else:
                        inputWidget = self.createComboBox(self.sourceList[str(device)], False, key, True)
                
                if not ignorePropertyCreation:
                    
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

                        if property.get("visibleOn") == None or device in property["visibleOn"]:
                            item = self.addProperty(key, property["string"], inputWidget, parent, inputSinker)

                            self.propertyItems[changeState[0]].stateChanged.connect(update)
                            update()
                    
                    else:
                        if property.get("visibleOn") == None or device in property["visibleOn"]:
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