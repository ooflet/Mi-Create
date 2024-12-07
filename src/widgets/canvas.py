# Canvas for Mi Create
# ooflet <ooflet@proton.me>

# Responsible for rendering projects via QGraphicsView library.
# Pass a Project-derived class 

import os
import sys
import traceback
import logging
from pprint import pprint
from datetime import datetime
from math import cos, sin, radians

sys.path.append("..")

from utils.data import WatchData
from utils.project import FprjWidget, GMFWidget

from PyQt6.QtCore import pyqtSignal, QPoint, QPointF, QSize, QRect, QTimer, Qt, QModelIndex
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QPixmap, QIcon, QBrush, QImage, QStandardItemModel
from PyQt6.QtWidgets import (QApplication, QGraphicsPathItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                            QToolButton, QGraphicsPixmapItem, QGraphicsEllipseItem, QMessageBox, QRubberBand, QGraphicsDropShadowEffect, QHBoxLayout, QVBoxLayout)

from utils.menu import ContextMenu

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "widget_analog" : "widget-analogdisplay",
            "widget_pointer" : "widget-pointer",
            "widget" : "widget-image",
            "widget_container" : "widget-container",
            "widget_imagelist" : "widget-imagelist",
            "widget_num" : "widget-digitalnumber",
            "widget_arc" : "widget-arcprogress"
        }

class DeviceRepresentation(QGraphicsPixmapItem):
    def __init__(self, id, interpolation):
        super().__init__()
        self.deviceData = {
            "9": [":/Images/mb8.png", -325, -180]
        }
        self.setPixmap(QPixmap(self.deviceData[id][0]))
        self.setPos(self.deviceData[id][1], self.deviceData[id][2])
        if interpolation:
            self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

class DeviceOutline(QGraphicsPathItem):
    # Creates the grey outline showing how rounded the screen is
    def __init__(self, size):
        super().__init__()
        thickness = 5
        outline = QPainterPath()
        outline.addRoundedRect(thickness/2, thickness/2, (size[0]-thickness), (size[1]-thickness), size[2], size[2])
        self.setPath(outline)
        self.setPen(QPen(QColor(255, 255, 255, 100), thickness, Qt.PenStyle.SolidLine))
        self.setBrush(QColor(0,0,0,0))
        self.setZValue(9999)

class DeviceFrame(QGraphicsPathItem):
    # Shape that crops the screen to the border radius
    def __init__(self, size, clip):
        super().__init__()
        outline = QPainterPath()
        if clip:
            outline.addRoundedRect(0, 0, size[0], size[1], size[2], size[2])
        else:
            outline.addRoundedRect(0, 0, size[0], size[1], 0, 0)
        self.setPath(outline)
        self.setBrush(QColor(0,0,0,255))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, clip)
        self.setZValue(0)

class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # hack incoming!!!!
        # qt breaks down and segfaults when removing items in some cases
        # something something BSP index doesn't properly get updated
        
        # i haven't seen major performance hits without BSP
        # there may be, so good luck future maintainers in fixing my shitty patch :)

        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        self.originPositions = {}
        self.positionMap = {
            "X": [],
            "Y": []
        }
        self.posLines = []

    def updatePosMap(self):
        self.positionMap = {"X": [], "Y": []}
        for item in self.items():
            # if isinstance(item, NumberWidget) and hasattr(item, "angle") and item.angle != 0:
            #     # calculate points when widget is rotated
            #     angle_rad = radians(item.angle)
            #     origin = item.pos() + item.transformOriginPoint()
            #     rotated_points = []

            #     # translate
            #     x1 = item.pos().x() + origin.x()
            #     y1 = item.pos().y() + origin.y()

            #     x2 = item.rect().bottomRight().x() + origin.x()
            #     y2 = item.rect().bottomRight().y() + origin.y()

            #     rotated_x1 = cos(angle_rad) * x1 - sin(angle_rad) * y1
            #     rotated_y1 = sin(angle_rad) * x1 + cos(angle_rad) * y1

            #     rotated_x2 = cos(angle_rad) * x2 - sin(angle_rad) * y2
            #     rotated_y2 = sin(angle_rad) * x2 + cos(angle_rad) * y2

            #     self.positionMap["X"].append(rotated_x1)
            #     self.positionMap["X"].append(rotated_x2)
            #     self.positionMap["Y"].append(rotated_y1)
            #     self.positionMap["Y"].append(rotated_y2)

            if isinstance(item, BaseWidget):
                # get points
                self.positionMap["X"].append(item.pos().x())
                self.positionMap["X"].append(item.pos().x() + item.rect().width())
                self.positionMap["Y"].append(item.pos().y())
                self.positionMap["Y"].append(item.pos().y() + item.rect().height())

    def getAdjacentPos(self, object: QGraphicsRectItem):
        catchRange = 3 # pixel offset before the object gets snapped
        adjacentPosList = []
        pos = [None, None, None, None] # x1, y1, x2, y2

        """
        x1, y1  •───────────┐
                │           │
                │           │
                │           │
                │           │
                └───────────• x2, y2
        """

        # filter function
        def posFilter(x, objPos):
            if x - catchRange <= objPos <= x + catchRange:
                return True
            else:
                return False
    
        # filter both X & Y pos and place in a list
        adjacentPosList1 = [list(filter(lambda x, objPos=object.pos().x(): posFilter(x, objPos), self.positionMap["X"])), list(filter(lambda x, objPos=object.pos().y(): posFilter(x, objPos), self.positionMap["Y"]))]
        adjacentPosList2 = [list(filter(lambda x, objPos=object.pos().x()+object.rect().width(): posFilter(x, objPos), self.positionMap["X"])), list(filter(lambda x, objPos=object.pos().y()+object.rect().height(): posFilter(x, objPos), self.positionMap["Y"]))]

        if adjacentPosList1[0] != []:
            pos[0] = (min(adjacentPosList1[0], key=lambda x:abs(x-object.pos().x())))

        if adjacentPosList1[1] != []:
            pos[1] = (min(adjacentPosList1[1], key=lambda x:abs(x-object.pos().y())))

        if adjacentPosList2[0] != []:
            pos[2] = (min(adjacentPosList2[0], key=lambda x:abs(x-object.pos().x()+object.rect().width())))

        if adjacentPosList2[1] != []:
            pos[3] = (min(adjacentPosList2[1], key=lambda x:abs(x-object.pos().y()+object.rect().height())))

        # prioritize snap positions

        if pos[0] != None and pos[2] != None:
            if pos[2] - pos[0] != object.rect().width():
                if pos[0] - object.pos().x() > pos[2] - (object.pos().x() + object.rect().width()):
                    pos[0] = None
                else:
                    pos[2] = None

        if pos[1] != None and pos[3] != None:
            if pos[1] - pos[3] != object.rect().width():
                if pos[1] - object.pos().y() > pos[3] - (object.pos().y() + object.rect().height()):
                    pos[1] = None
                else:
                    pos[3] = None

        return pos
    
    def getPreviewNumber(self, source):
        now = datetime.now()
        if source == "Hour":
            return now.strftime("%I")
        elif source == "Hour High":
            return now.strftime("%I")[0]
        elif source == "Hour Low":
            return now.strftime("%I")[1]
        elif source == "Minute":
            return now.strftime("%M")
        elif source == "Minute High":
            return now.strftime("%M")[0]
        elif source == "Minute Low":
            return now.strftime("%M")[1]
        elif source == "Second":
            return now.strftime("%S")
        elif source == "Second High":
            return now.strftime("%S")[0]
        elif source == "Second Low":
            return now.strftime("%S")[1]
        elif source == "Day":
            return now.strftime("%d")
        elif source == "Month":
            return now.strftime("%m")
        elif source == "Week":
            return now.strftime("%w")
        elif source == "AM/PM":
            am_pm = now.strftime("%p")
            print(am_pm)
            if am_pm == "AM" or am_pm == "am":
                return "0"
            elif am_pm == "PM" or am_pm == "pm":
                return "1"

    def drawSnapLines(self, pos):
        for line in self.posLines:
            self.removeItem(line)

        self.posLines.clear()

        if pos[0] != None:
            self.posLines.append(self.addRect(pos[0], 0, 1, self.sceneRect().height(), QPen(Qt.PenStyle.NoPen), self.palette().highlight()))

        if pos[1] != None:
            self.posLines.append(self.addRect(0, pos[1], self.sceneRect().width(), 1, QPen(Qt.PenStyle.NoPen), self.palette().highlight()))
        
        if pos[2] != None:
            self.posLines.append(self.addRect(pos[2], 0, 1, self.sceneRect().height(), QPen(Qt.PenStyle.NoPen), self.palette().highlight()))

        if pos[3] != None:
            self.posLines.append(self.addRect(0, pos[3], self.sceneRect().width(), 1, QPen(Qt.PenStyle.NoPen), self.palette().highlight()))

    def clearSnapLines(self):
        for line in self.posLines:
            self.removeItem(line)

        self.posLines.clear()

class Canvas(QGraphicsView):
    onObjectAdded = pyqtSignal(str, int, int)
    onObjectChange = pyqtSignal(str, str, object) # hate hacky workarounds, just support any type already Qt
    onObjectPosChange = pyqtSignal()

    def __init__(self, device, antialiasingEnabled: bool, deviceOutlineVisible: bool, ui: object, parent=None):
        super().__init__(parent)

        if antialiasingEnabled:
            self.setRenderHints(QPainter.RenderHint.Antialiasing)

        self.mainWindowUI = ui # used for ContextMenu, it needs window UI to access QActions
        self.widgets = {}

        self.itemDragPreview = None

        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse) # positions scene to zoom under mouse

        self.deviceOutlineVisible = deviceOutlineVisible
        self.origin = None
        self.setAcceptDrops(True) # just in case item implement image drag & drop

        self.zoomValue = 0

        self.deviceSize = WatchData().modelSize[str(device)]

        self.graphicsScene = Scene()
        self.graphicsScene.setSceneRect(0,0,self.deviceSize[0],self.deviceSize[1])

        self.isPreviewPlaying = False

        self.setScene(self.graphicsScene)

    def fireObjectPositionChanged(self):
        self.scene().updatePosMap()
        self.onObjectPosChange.emit()

    def mousePressEvent(self, event):
        if not any(isinstance(item, BaseWidget) for item in self.items(event.pos())):
            if event.button() == Qt.MouseButton.LeftButton:
                self.rubberBandOrigin = event.pos()
                self.rubberBand.setGeometry(QRect(self.rubberBandOrigin, QSize()))
                self.rubberBand.show()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.rubberBand.isHidden():
            self.rubberBand.setGeometry(QRect(self.rubberBandOrigin, event.pos()).normalized())
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        for item in self.items(self.rubberBand.geometry()):
            if isinstance(item, BaseWidget):
                item.setSelected(True)
        self.rubberBand.setGeometry(QRect(0,0,0,0))
        return super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()

            model = QStandardItemModel()
            model.dropMimeData(event.mimeData(), Qt.DropAction.CopyAction, 0, 0, QModelIndex())

            self.itemDragPreview = QGraphicsPixmapItem()
            self.scene().addItem(self.itemDragPreview)
            self.itemDragPreview.setOpacity(0.5)
            self.itemDragPreview.setPixmap(QPixmap(os.path.join(self.imageFolder, model.item(0, 0).data(0))))

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()

            if self.itemDragPreview != None:
                self.itemDragPreview.setPos(self.mapToScene(int(event.position().x()), int(event.position().y())))

    def dragLeaveEvent(self, event):
        if self.itemDragPreview != None:
            self.scene().removeItem(self.itemDragPreview)
            self.itemDragPreview = None

    def dropEvent(self, event):
        event.acceptProposedAction()

        model = QStandardItemModel()
        model.dropMimeData(event.mimeData(), Qt.DropAction.CopyAction, 0, 0, QModelIndex())

        if self.itemDragPreview != None:
            self.scene().removeItem(self.itemDragPreview)
            self.itemDragPreview = None

        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            position = self.mapToScene(int(event.position().x()), int(event.position().y()))
            self.onObjectAdded.emit(model.item(0, 0).data(0), int(position.x()), int(position.y()))


    def contextMenuEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        view = self.scene().views()[0]  # Get the first view
        viewPos = view.mapToGlobal(view.mapFromScene(scenePos))

        topLevelItem = None
        items = self.items(event.pos())
        for item in items:
            if isinstance(item, BaseWidget):
                if topLevelItem == None:
                    topLevelItem = item
                elif topLevelItem.zValue() < item.zValue():
                    topLevelItem = item

        if topLevelItem != None:
            if not topLevelItem.isSelected():
                self.scene().clearSelection()
                topLevelItem.setSelected(True)
            menu = ContextMenu("shape", self.mainWindowUI)
        else:
            menu = ContextMenu("default", self.mainWindowUI)

        menu.exec(viewPos)

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            zoom_factor = 1.25 if delta > 0 else 1 / 1.25
            self.scale(zoom_factor, zoom_factor)
        elif modifiers == Qt.KeyboardModifier.AltModifier:
            scroll_delta = event.angleDelta().x()
            scroll_value = self.horizontalScrollBar().value() - scroll_delta
            self.horizontalScrollBar().setValue(scroll_value)
        else:
            scroll_delta = event.angleDelta().y()
            scroll_value = self.verticalScrollBar().value() - scroll_delta
            self.verticalScrollBar().setValue(scroll_value)

    def handleObjectSelectionChange(self):
        selected_object = self.getSelectedObject()
        if selected_object:
            print(f"Object '{selected_object}' selected")

    def getObject(self, name):
        return self.widgets.get(name)

    def clearSelected(self):
        self.scene().clearSelection()

    def selectObject(self, name, clearSelection=True):
        if name == None:
            return
        if clearSelection:
            self.scene().clearSelection()
        self.widgets[name].setSelected(True)

    def selectObjectsFromPropertyList(self, items: list):
        for item in items:
            self.widgets[item["Name"]].setSelected(True)

    def getSelectedObjects(self):
        return self.scene().selectedItems()

    def onObjectDeleted(self, name, widget):
        self.objectDeleted.emit(name)

    def createPreview(self):
        large_preview_path = os.path.join(self.imageFolder, "preview_large.png")
        area = self.scene().sceneRect()

        if os.path.exists(large_preview_path):
            if QMessageBox.question(None, "previewGenerator", f"{large_preview_path} already exists. Overwrite?") == QMessageBox.StandardButton.Yes:
                os.remove(large_preview_path)
            else:
                return
            
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)

        self.scene().render(painter, image.rect(), area)
        painter.end()

        # Save the image to a file.
        image.save()

    def createAnalogDisplay(self, transparency, name, pos, zValue, backgroundImage, hourHandImage, minuteHandImage, secondHandImage, itemAnchors, smoothHr, smoothMin, snap, interpolationStyle):
        suffix = name.split("_")
        smoothSec = "0" # false
        updateInterval = 30 # update interval in miliseconds
        if len(suffix) >= 2:
            interval = suffix[-1].split("[")
            
            if interval[0] == "smooth":
                smoothSec = "1" # true

            if len(interval) == 2 and interval[1].strip("[]") != "":
                updateInterval = int(interval[1].strip("[]"))

        # Create widget
        widget = AnalogWidget(int(pos.x()), int(pos.y()), int(pos.width()), int(pos.height()), self.frame, self, QColor(255,255,255,0), transparency, name, smoothHr, smoothMin, smoothSec, updateInterval)
        widget.setZValue(zValue)
        widget.setData(1, "widget_analog") # Item ID
        widget.snap = snap

        # Add images

        bgImg = QPixmap()
        if backgroundImage is not None:        # check if there is a background image exist
          bgImg.load(os.path.join(self.imageFolder, backgroundImage))

        hrImg = QPixmap()
        if hourHandImage is not None:
          hrImg.load(os.path.join(self.imageFolder, hourHandImage))

        minImg = QPixmap()
        if minuteHandImage is not None:
          minImg.load(os.path.join(self.imageFolder, minuteHandImage))
        
        secImg = QPixmap()
        if secondHandImage is not None:        # check if there is a second hand image exist some AOD does not have this
          secImg.load(os.path.join(self.imageFolder, secondHandImage))

        widget.addBackground(bgImg, itemAnchors["background"]["x"], itemAnchors["background"]["y"], interpolationStyle)
        widget.addHourHand(hrImg, itemAnchors["hour"]["x"], itemAnchors["hour"]["y"], interpolationStyle)
        widget.addMinuteHand(minImg, itemAnchors["minute"]["x"], itemAnchors["minute"]["y"], interpolationStyle)
        widget.addSecondHand(secImg, itemAnchors["second"]["x"], itemAnchors["second"]["y"], interpolationStyle)
        
        if bgImg.isNull() and hrImg.isNull() and minImg.isNull() and secImg.isNull():
            widget.color = QColor(255, 0, 0, 100)

        return widget
    
    def createPointer(self, transparency, name, rect, zValue, pointer, pointerAnchorX, pointerAnchorY, snap, interpolationStyle):
        # Create widget
        widget = PointerWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), transparency, name)
        widget.setZValue(zValue)
        widget.setData(1, "widget") # Item ID
        widget.snap = snap

        # Add image
        pixmap = QPixmap()
        pixmap.load(os.path.join(self.imageFolder, pointer))

        widget.addPointer(pixmap, pointerAnchorX, pointerAnchorY, interpolationStyle)

        return widget

    def createImage(self, transparency, name, rect, zValue, image, snap, interpolationStyle):
        # Create widget
        widget = ImageWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), transparency, name)
        widget.setZValue(zValue)
        widget.setData(1, "widget") # Item ID
        widget.snap = snap

        # Add image
        pixmap = QPixmap()
        pixmap.load(os.path.join(self.imageFolder, image))

        widget.setImage(pixmap, interpolationStyle)
        
        return widget

    def createImageList(self, transparency, name, rect, zValue, defaultValue, source, bitmapList, snap, interpolationStyle, previewIndex=None):
        # Create widget
        widget = ImagelistWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), transparency, name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_imagelist") # Item ID 
        widget.snap = snap

        # check if animation

        animationName = name.split("_")

        if animationName[0] == "anim":
            animImageList = [QPixmap(os.path.join(self.imageFolder, image[1])) for image in bitmapList]
            widget.addAnimatedImagelist(animImageList, interpolationStyle)
        else:
            imageList = {}
            for image in bitmapList:
                if len(image) >= 2:
                    imageList[int(image[0])] = QPixmap(os.path.join(self.imageFolder, image[1]))
                else:
                    widget.representNoImage()
                    break

            widget.addImagelist(imageList, source, previewIndex, defaultValue, interpolationStyle)

        return widget
    
    def createContainer(self, transparency, name, rect, zValue):
        # no use for it so far, just bare bones implementation
        widget = BaseWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), transparency, name)
        widget.setZValue(zValue)
        return widget

    def createDigitalNumber(self, transparency, name, rect, zValue, source, numList, digits, spacing, alignment, hideZeros, snap, interpolationStyle, posRelativeToAlign, previewNumber=None):
        split = name.split("_")
        angle = 0

        if len(split) >= 2:
            nameAngle = split[-1].split("[")
            if len(nameAngle) >= 2:
                angleString = nameAngle[1].strip("[]")
                if nameAngle[0] == "angle" and angleString != "":
                    angle = int(angleString) / 10
        
        widget = NumberWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), transparency, name, angle, posRelativeToAlign)
        widget.setZValue(zValue)
        widget.setData(1, "widget_imagelist") # Item ID
        widget.snap = snap

        numList = [QPixmap(os.path.join(self.imageFolder, image)) for image in numList]

        # Get QPixmap from file string
        if len(numList) >= 10:
            widget.addNumbers(previewNumber, source, numList, digits, spacing, alignment, hideZeros, interpolationStyle)
        else:
            widget.representNoImage()
                
        return widget

    def createProgressArc(self, transparency, name, rect, zValue, backgroundImage, arcImage, arcX, arcY, radius, lineWidth, startAngle, endAngle, isFlat, snap, interpolationStyle):
        bgImage = QPixmap()
        if backgroundImage is not None:
          bgImage.load(os.path.join(self.imageFolder, backgroundImage))
    
        fgImage = QPixmap()
        fgImage.load(os.path.join(self.imageFolder, arcImage))

        # the amount of arguments is horrific, might fix
        widget = ProgressWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), 
                                transparency, name, arcX, arcY, radius, lineWidth, startAngle, endAngle, isFlat, bgImage, fgImage, 
                                interpolationStyle)
        
        widget.setZValue(zValue)
        widget.setData(1, "widget_arc")
        widget.snap = snap

        return widget

    def createWidgetFromData(self, index, item, snap, interpolation):
        widget = None

        # qt calls this "smooth transformation"
        if interpolation == "Bilinear":
            interpolation = True
        else:
            interpolation = False

        if item.getProperty("widget_type") == None:
            # invalid widget type (most likely not supported)
            # none type is returned when widget attempts to convert widget_type value into generic ID
            return False, f" Widget '{item.getProperty('widget_name')}' has unsupported widget type", ""

        try:
            if item.getProperty("widget_type") == "widget_analog":
                widget = self.createAnalogDisplay(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("widget_background_bitmap"),
                    item.getProperty("analog_hour_image"),
                    item.getProperty("analog_minute_image"),
                    item.getProperty("analog_second_image"),
                    # construct table for hand's anchor points
                    {
                        "background": {
                            "x": item.getProperty("analog_bg_anchor_x"),
                            "y": item.getProperty("analog_bg_anchor_y"),
                        },
                        "hour": {
                            "x": item.getProperty("analog_hour_anchor_x"),
                            "y": item.getProperty("analog_hour_anchor_y"),
                        },
                        "minute": {
                            "x": item.getProperty("analog_minute_anchor_x"),
                            "y": item.getProperty("analog_minute_anchor_y"),
                        },
                        "second": {
                            "x": item.getProperty("analog_second_anchor_x"),
                            "y": item.getProperty("analog_second_anchor_y"),
                        },
                    },
                    item.getProperty("analog_hour_smooth_motion"),
                    item.getProperty("analog_minute_smooth_motion"),
                    snap,
                    interpolation
                )
            
            elif item.getProperty("widget_type") == "widget_pointer":
                widget = self.createPointer(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmap"),
                    item.getProperty("pointer_anchor_x"),
                    item.getProperty("pointer_anchor_y"),
                    snap,
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_arc":
                widget = self.createProgressArc(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("widget_background_bitmap"),
                    item.getProperty("arc_image"),
                    item.getProperty("arc_pos_x"),
                    item.getProperty("arc_pos_y"),
                    item.getProperty("arc_radius"),
                    item.getProperty("arc_thickness"),
                    item.getProperty("arc_start_angle"),
                    item.getProperty("arc_end_angle"),
                    item.getProperty("arc_flat_caps"),
                    snap,
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget":
                if isinstance(item, GMFWidget):
                    unitImageFromWidget = False
                elif isinstance(item, FprjWidget):
                    unitImageFromWidget = True
                else:
                    posRelativeToAlign = False

                widget = self.createImage(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmap"),
                    snap,
                    interpolation
                )

                split = item.getProperty("widget_name").split("[")
                if len(split) >= 2:
                    nameRef = split[0].split("_")
                    if len(nameRef) >= 2 and nameRef[-1] == "ref":
                        if self.unitImages.get(item.getProperty("widget_name")):
                            self.unitImages.pop(item.getProperty("widget_name"))
                        self.unitImages[item.getProperty("widget_name")] = [item, widget, unitImageFromWidget]

            elif item.getProperty("widget_type") == "widget_imagelist":
                widget = self.createImageList(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    int(item.getProperty("imagelist_default_index")),
                    item.getSourceName(),
                    item.getProperty("widget_bitmaplist"),
                    snap,
                    interpolation,
                    item.getPreviewNumber(),
                )

            elif item.getProperty("widget_type") == "widget_container":
                widget = self.createContainer(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index
                )

            elif item.getProperty("widget_type") == "widget_num":
                if isinstance(item, GMFWidget):
                    posRelativeToAlign = True
                    unitImageFromWidget = False
                elif isinstance(item, FprjWidget):
                    posRelativeToAlign = False
                    unitImageFromWidget = True
                else:
                    posRelativeToAlign = False

                widget = self.createDigitalNumber(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getSourceName(),
                    item.getProperty("widget_bitmaplist"),
                    item.getProperty("num_digits"),
                    item.getProperty("num_spacing"),
                    item.getProperty("num_alignment"),
                    bool(int(item.getProperty("num_toggle_zeros"))),
                    snap,
                    interpolation,
                    posRelativeToAlign,
                    item.getPreviewNumber()
                )

            elif item.getProperty("widget_type") == "widget_arc":
                widget = self.createProgressArc(
                    item.getProperty("widget_alpha"),
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("analog_background"),
                    item.getProperty("arc_image"),
                    item.getProperty("arc_pos_x"),
                    item.getProperty("arc_pos_y"),
                    item.getProperty("arc_radius"),
                    item.getProperty("arc_thickness"),
                    item.getProperty("arc_start_angle"),
                    item.getProperty("arc_end_angle"),
                    snap,
                    interpolation
                )

            else:
                # this only happens in the rare off chance when the item ID is added, but not implemented in the canvas
                return False, f"Widget {item.getProperty('widget_type')} not implemented in canvas. Please report this as an issue.", ""

            # add widget into widget list
            self.widgets[item.getProperty("widget_name")] = widget
            return True, "Success", ""
        except Exception:
            # status, user facing message, debug info
            return False, f"Widget '{item.getProperty('widget_name')}' has malformed data or is corrupt", f"Canvas failed to create object {item.getProperty('widget_name')}:\n {traceback.format_exc()}"

    def loadObjects(self, project, snap=None, interpolation=None, clip=True, outline=False):
        self.frame = DeviceFrame(self.deviceSize, clip)
        
        if interpolation == None:
            interpolation = self.interpolation
        else:
            self.interpolation = interpolation

        if snap == None:
            snap = self.snap
        else:
            self.snap = snap

        # device representation shows the device as an image behind the watchface
        # why? no reason
        #self.deviceRep = DeviceRepresentation(project.getDeviceType(), interpolation)

        self.unitImages = {}
        self.scene().clear()
        self.widgets.clear()
        #self.scene().addItem(self.deviceRep)
        self.scene().addItem(self.frame)

        if outline:
            self.deviceOutline = DeviceOutline(self.deviceSize)
            self.scene().addItem(self.deviceOutline)
            
        if project.getAllWidgets() == []:
            return True, "Success", ""

        self.imageFolder = project.getImageFolder()

        self.scene().originPositons = {}

        widgets = project.getAllWidgets()

        for index, widget in enumerate(widgets):    
            result, userFacingReason, debugReason = self.createWidgetFromData(index, widget, snap, interpolation)
            self.scene().originPositions[widget.getProperty("widget_name")] = [int(widget.getProperty("widget_pos_x")), int(widget.getProperty("widget_pos_y"))]
            if not result:
                print(debugReason)
                return False, userFacingReason, debugReason
        
        for unitWidget in self.unitImages.values():
            split = unitWidget[0].getProperty("widget_name").split("[")
            if len(split) >= 2:
                nameRef = split[0].split("_")
                if len(nameRef) >= 2 and nameRef[-1] == "ref":
                    numWidget = self.getObject(split[-1].strip("[]"))
                    if numWidget and isinstance(numWidget, NumberWidget):
                        numWidget.addUnitImage(
                            True,
                            unitWidget[1],
                            interpolation,
                            numWidget.alignment
                        )
                    else:
                        QMessageBox.warning(None, "Canvas", "Invalid widget for _ref!")

        self.scene().updatePosMap()
        return True, "Success", ""
        
    def reloadObject(self, objectName, widget):
        # loads a single object without reloading every object in the canvas
        # if using on a mass set of objects, its usually easier to call the loadobjects function
        object = self.widgets[objectName]
        objectZValue = object.zValue()

        if object != None:

            result, userFacingReason, debugReason = self.createWidgetFromData(objectZValue, widget, self.snap, self.interpolation)
            if not result:
                return False, userFacingReason, debugReason
            else:
                self.scene().originPositions[objectName] = [int(widget.getProperty("widget_pos_x")), int(widget.getProperty("widget_pos_y"))]
                self.scene().updatePosMap()
                object.selectionPath.prepareGeometryChange()
                object.delete()
                for unitWidget in self.unitImages.values():
                    split = unitWidget[0].getProperty("widget_name").split("[")
                    numWidget = self.widgets[split[-1].strip("[]")]
                    if numWidget and isinstance(numWidget, NumberWidget):
                        numWidget.addUnitImage(
                            True,
                            unitWidget[1],
                            self.interpolation,
                            numWidget.alignment
                        )
                    else:
                        QMessageBox.warning(None, "Canvas", "Invalid widget for _ref!")
                
                return True, "Success", ""

class BaseWidget(QGraphicsRectItem):
    # Basic widget with draggable and selectable controls
    # Allows for snap to guides
    # Adding child QGraphicsItems to this widget extends functionality 

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name):
        # Initialize the shape.
        super().__init__(posX, posY, sizeX, sizeY, parent)
        self.setRect(0, 0, sizeX, sizeY)
        self.setPos(posX, posY)
        self.setPen(QPen(QColor(0,0,0,0)))
        self.origPos = None
        self.size = QPointF(sizeX, sizeY)
        self.boundingPosOverride = False
        self.boundingPos = QPointF(0, 0)
        self.color = color
        self.canvas = canvas
        self.selectionPos = None
        self.selectionPath = QGraphicsPathItem()
        self.selectionPainterPath = QPainterPath()
        self.highlightThickness = 2
        self.highlightRadius = 3
        self.snap = True
        self.scene().addItem(self.selectionPath)
        self.setAcceptHoverEvents(True)
        self.setOpacity(int(transparency) / 255)
        self.setData(0, name)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        #self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)

    def boundingRect(self):
        # Create outline
        if self.selectionPos == None or self.pos().x() != self.selectionPos.x() or self.pos().y() != self.selectionPos.y():
            self.selectionPos = self.pos()

            if self.boundingPosOverride:
                self.selectionPath.setPos(self.boundingPos)
            else:
                self.selectionPath.setPos(self.pos())
                
            self.selectionPainterPath.clear()
            self.selectionPainterPath.addRoundedRect(0, 0, self.rect().width(), self.rect().height(), self.highlightRadius, self.highlightRadius)
            self.selectionPath.setPath(self.selectionPainterPath)
            pen = QPen(self.scene().palette().highlight(), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            self.selectionPath.setPen(pen)

        # hack to get rid of bounding box ghosting
        outline_width = 4
        return self.rect().adjusted(-outline_width, -outline_width, outline_width, outline_width)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(event)

        # handle snap
        if self.snap:
            snapPos = self.scene().getAdjacentPos(self)

            if snapPos == [None, None]:
                return
            
            self.scene().drawSnapLines(snapPos)

            if snapPos[0] != None:
                self.setX(snapPos[0])
                
            if snapPos[1] != None:
                self.setY(snapPos[1])

            if snapPos[2] != None:
                self.setX(snapPos[2] - self.rect().width())
                
            if snapPos[3] != None:
                self.setY(snapPos[3] - self.rect().height())

        self.setPos(round(self.x()), round(self.y()))

        if len(self.scene().selectedItems()) > 1:
            for item in self.scene().selectedItems():
                x = self.scene().originPositions[item.data(0)][0] + (self.pos().x() - self.origPos.x())
                y = self.scene().originPositions[item.data(0)][1] + (self.pos().y() - self.origPos.y())
                item.setPos(x, y)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.origPos = self.pos()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.scene().clearSnapLines()
        if event.button() != Qt.MouseButton.RightButton:
            self.canvas.fireObjectPositionChanged()
    
    def delete(self):
        self.scene().removeItem(self.selectionPath)
        self.scene().removeItem(self)

    def paint(self, painter, option, widget=None):
        # Paint the node in the graphic view.

        painter.setBrush(QBrush(self.color))
        painter.setPen(self.pen())

        if self.isSelected():
            self.selectionPath.show()
        else:
            self.selectionPath.hide()

        painter.drawRect(self.rect())

class ImageWidget(BaseWidget):
    # Widget for basic images

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name)
        self.pixmapItem = QGraphicsPixmapItem(self)
        self.setPos(posX, posY)

    def setImage(self, qPixmap, isAntialiased):
        if qPixmap.isNull():
            self.representNoImage()
            return
        
        self.pixmapItem.setPixmap(qPixmap)
        self.setRect(0, 0, qPixmap.width(), qPixmap.height())

        if isAntialiased:
            self.pixmapItem.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def representNoImage(self):
        self.color = QColor(255, 0, 0, 100)

class ImagelistWidget(ImageWidget):
    # Widget for imagelists and animated images

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name)
        self.previewIndex = None
        self.defaultValue = None
        self.imagelist = None
        self.isAnimation = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateImage)
        self.source = None

    def getLastValidListIndex(self, index):
        if self.imagelist.get(index):
            return index

        for i in range(index, -1, -1):
            if self.imagelist.get(int(i)) != None:
                return i

        return None

    def addImagelist(self, imagelist, source, previewIndex, defaultValue, isAntialiased):
        if imagelist == []:
            self.representNoImage()
            return

        if previewIndex != None:
            previewIndex = int(previewIndex)
        
        self.previewIndex = previewIndex
        self.defaultValue = defaultValue
        self.antialiased = isAntialiased

        self.source = source
        self.imagelist = imagelist

        if previewIndex != None:
            previewImage = imagelist[self.getLastValidListIndex(previewIndex)]
        elif previewIndex == None and defaultValue != None:
            previewImage = imagelist[self.getLastValidListIndex(defaultValue)]
        else:
            previewImage = imagelist[next(iter(imagelist))] # get first item

        self.pixmapItem.setPixmap(previewImage)
        self.setRect(0, 0, previewImage.width(), previewImage.height())
        
        if isAntialiased:
            self.pixmapItem.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addAnimatedImagelist(self, imagelist, isAntialiased):
        self.isAnimation = True
        self.imagelist = imagelist
        initialFrame = imagelist[0]

        self.animatedImageList = imagelist
        self.pixmapItem.setPixmap(initialFrame)
        self.setRect(0, 0, initialFrame.width(), initialFrame.height())
        
        if isAntialiased:
            self.pixmapItem.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def updateImage(self):
        if self.isAnimation:
            self.currentFrame = (self.currentFrame + 1) % len(self.animatedImageList)
            self.pixmapItem.setPixmap(self.animatedImageList[self.currentFrame])

            if self.totalRepeats != 0:
                print(self.currentFrame + 1, len(self.animatedImageList) - 1, self.animRepeats, self.totalRepeats)
                if self.currentFrame + 1 > len(self.animatedImageList) - 1:
                    self.animRepeats += 1

                if self.animRepeats >= self.totalRepeats:
                    self.stopPreview(False)
        else:
            livePreviewIndex = None
            
            if self.scene().getPreviewNumber(self.source) != None:
                livePreviewIndex = int(self.scene().getPreviewNumber(self.source))
            
            if livePreviewIndex != None:
                self.pixmapItem.setPixmap(self.imagelist[self.getLastValidListIndex(livePreviewIndex)])
            elif self.previewIndex != None:
                self.pixmapItem.setPixmap(self.imagelist[self.getLastValidListIndex(self.previewIndex)])
            elif self.previewIndex == None and self.defaultValue != None:
                self.pixmapItem.setPixmap(self.imagelist[self.getLastValidListIndex(self.defaultValue)])
            else:
                self.pixmapItem.setPixmap(self.imagelist[next(iter(self.imagelist))])
            

    def startPreview(self, framesec=None, repeatAmounts=None):
        if self.imagelist == None:
            return
        
        if self.isAnimation:    
            self.animRepeats = 0
            self.totalRepeats = int(repeatAmounts)
            self.currentFrame = 0
            interval = int(framesec)
        else:
            interval = 100
            
        self.updateImage()
        self.timer.start(interval)

    def stopPreview(self, endPreview=True):
        if self.imagelist == None:
            return
        
        self.timer.stop()

        if self.isAnimation:
            if endPreview:
                self.pixmapItem.setPixmap(self.imagelist[0])    
        else:
            if self.previewIndex != None:
                self.pixmapItem.setPixmap(self.imagelist[self.getLastValidListIndex(self.previewIndex)])
            elif self.previewIndex == None and self.defaultValue != None:
                self.pixmapItem.setPixmap(self.imagelist[self.getLastValidListIndex(self.defaultValue)])
            else:
                self.pixmapItem.setPixmap(self.imagelist[next(iter(self.imagelist))])
            

class NumberWidget(BaseWidget):
    # Displays numbers

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name, angle, isPosRelativeToAlignment=False):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name)
        self.imageItems = []
        self.numList = []
        self.source = None
        self.angle = angle
        self.relativeToAlign = isPosRelativeToAlignment
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.updatePreviewNumber)
        self.posX = posX
        self.setPos(posX, posY)

    def addBlankImage(self):
        self.imageItems.append("") # append blank to imageitems

    def updateAngle(self):
        # calculate pivot point of the widget
        rect = self.rect()
        print(self.alignment)
        if self.alignment != None:
            if self.alignment == "Left":
                pivot = rect.topLeft()
            elif self.alignment == "Center":
                pivot = rect.center() - QPointF(0, rect.height() / 2)
            elif self.alignment == "Right":
                pivot = rect.topRight()
        
        # set angle to widget
        self.setTransformOriginPoint(pivot)
        self.setRotation(self.angle)

        # set angle to selection box
        self.selectionPath.setTransformOriginPoint(pivot)
        self.selectionPath.setRotation(self.angle)

    def addImage(self, qPixmap, posX, posY, spacing, isAntialiased):
        if qPixmap.isNull():
            self.representNoImage()
            return
        
        item = QGraphicsPixmapItem(qPixmap, self)
        item.setPos(posX, posY)
        self.imageItems.append(item)
        if isAntialiased:
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        
    def addNumbers(self, previewNumber, source, numList, digits, spacing, alignment, hideZeros, interpolationStyle, previewFromSource=False):
        # store arguments for later
        if not previewFromSource:
            self.previewNumber = previewNumber
        self.initialImage = numList[0]
        self.source = source
        self.numList = numList
        self.digits = digits
        self.spacing = spacing
        self.alignment = alignment
        self.hideZeros = hideZeros
        self.interpolationStyle = interpolationStyle
        
        self.clearImages()

        for x in range(int(digits)):
            # Get QPixmap from file string
            if len(numList) >= 10:
                if previewNumber != None:
                    previewNumber = str(previewNumber)
                    cropped = previewNumber[-int(digits):] # crop number
                    previewNumber = cropped.zfill(int(digits)) # pad number with zeroes
                    image = numList[int(previewNumber[x])]
                else:
                    image = numList[x % len(numList)]

                if hideZeros and previewNumber != None and int(previewNumber[x]) == 0:
                    self.addBlankImage()
                else:
                    if hideZeros:
                        hideZeros = False
                    
                    if alignment == "Left":
                        num = len([item for item in self.imageItems if item != ""])
                        self.addImage(image, (image.size().width() * num) + (int(spacing) * num), 0, int(spacing), interpolationStyle)
                    elif alignment == "Center":
                        # check if this is the first item by checking if there are no other items
                        items = [item for item in self.imageItems if item != ""]
                        # get pos x by multiplying all empty items by width and dividing by 2
                        initialItemPosX = (len([item for item in self.imageItems if item == ""]) * image.size().width()) / 2
                        if items == []:
                            self.addImage(image, initialItemPosX, 0, int(spacing), interpolationStyle)
                        else:
                            self.addImage(image, (image.size().width() + int(spacing)) * len(items) + initialItemPosX , 0, int(spacing), interpolationStyle)
                    elif alignment == "Right":
                        self.addImage(image, (image.size().width() * x) + (int(spacing) * x), 0, int(spacing), interpolationStyle)
            else:
                self.representNoImage()

            if not previewFromSource:
                width = ( self.initialImage.width() * len(self.imageItems) ) + ( int(spacing) * len(self.imageItems) )
                self.setRect(0, 0, width, self.initialImage.height())

            if self.relativeToAlign:
                if alignment == "Center":
                    self.setX(self.posX - (self.rect().width() / 2))
                elif alignment == "Right":
                    self.setX(self.posX - self.rect().width())

            self.updateAngle()

    def addUnitImage(self, unitImageFromWidget, unitWidget, interpolationStyle, alignment=None, unitImage=None):
        
        if alignment != None:
            if alignment == "Left":
                num = len([item for item in self.imageItems if item != ""])
                unitImagePosX = (self.initialImage.size().width() * num) + (int(self.spacing) * num) 
            elif alignment == "Center":
                # check if this is the first item by checking if there are no other items
                items = [item for item in self.imageItems if item != ""]
                # get pos x by multiplying all empty items by width and dividing by 2
                initialItemPosX = (len([item for item in self.imageItems if item == ""]) * self.initialImage.size().width()) / 2
                if items == []:
                    unitImagePosX = initialItemPosX
                else:
                    unitImagePosX = (self.initialImage.size().width() + int(self.spacing)) * len(items) + initialItemPosX
            elif alignment == "Right":
                unitImagePosX = (self.initialImage.size().width() * len(self.imageItems)) + (int(self.spacing) * len(self.imageItems))

        else:
            unitImagePosX = self.rect().width()

        if unitImageFromWidget:
            unitWidget.setPos(unitImagePosX, 0)
            unitWidget.setParentItem(self)
            unitWidget.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            unitWidget.snap = False
            unitWidget.boundingPosOverride = True
            unitWidget.boundingPos = QPointF(self.pos().x() + unitImagePosX, self.pos().y())
            self.setRect(0, 0, self.rect().width() + unitWidget.rect().width(), self.initialImage.height())
        else:
            unitImageWidget = QGraphicsPixmapItem(self)
            unitImageWidget.setPixmap(unitImage)
            unitImageWidget.setX(unitImagePosX)
            self.setRect(0, 0, self.rect().width() + unitImage.width(), self.initialImage.height())

            if interpolationStyle:
                unitImageWidget.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        
    def updatePreviewNumber(self):
        previewNumber = self.scene().getPreviewNumber(self.source)
        
        if previewNumber is not None:
            self.addNumbers(previewNumber, self.source, self.numList, self.digits, self.spacing, self.alignment, self.hideZeros, self.interpolationStyle, previewFromSource=True)

    def startPreview(self):
        if self.source != None:
            self.updatePreviewNumber()
            self.timer.start()

    def stopPreview(self):
        if self.source != None:
            self.timer.stop()
            self.addNumbers(self.previewNumber, self.source, self.numList, self.digits, self.spacing, self.alignment, self.hideZeros, self.interpolationStyle, True)

    def clearImages(self):
        for x in self.imageItems:
            if isinstance(x, str) is not True:
                self.scene().removeItem(x)
        self.imageItems.clear()

    def representNoImage(self):
        self.color = QColor(255, 0, 0, 100)

class AnalogWidget(BaseWidget):
    # Widget for handling AnalogDisplays
    
    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name, smoothHr, smoothMin, smoothSec, updateInterval):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name)
        print(smoothHr, smoothMin)
        self.smoothHr = smoothHr 
        self.smoothMin = smoothMin 
        self.smoothSec = smoothSec
        self.timer = QTimer()
        self.timer.setInterval(updateInterval)
        self.timer.timeout.connect(self.updatePreviewHands)
        self.setPos(posX, posY)

    def addBackground(self, backgroundImage, bgX, bgY, antialiasing):
        self.bgImage = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage.setPos(int(bgX), int(bgY))
        if antialiasing:
            self.bgImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addSecondHand(self, secHandImage, secHandX, secHandY, antialiasing):
        self.secHand = QGraphicsPixmapItem(secHandImage, self)
        self.secHand.setOffset(-int(secHandX), -int(secHandY))
        self.secHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.secHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addMinuteHand(self, minHandImage, minHandX, minHandY, antialiasing):
        self.minHand = QGraphicsPixmapItem(minHandImage, self)
        self.minHand.setOffset(-int(minHandX), -int(minHandY))
        self.minHand.setRotation(48)
        self.minHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.minHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addHourHand(self, hourHandImage, hrHandX, hrHandY, antialiasing):
        self.hrHand = QGraphicsPixmapItem(hourHandImage, self)
        self.hrHand.setOffset(-int(hrHandX), -int(hrHandY))
        self.hrHand.setRotation(300)
        self.hrHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.hrHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def updatePreviewHands(self):
        now = datetime.now()
        if self.hrHand != None:
            if self.smoothHr == "1":
                min = int(now.strftime("%M")) / 60
                angle = (int(now.strftime("%I")) + min) / 12 * 360
            else:
                angle = int(now.strftime("%I")) / 12 * 360
            self.hrHand.setRotation(angle)

        if self.minHand != None:
            if self.smoothMin == "1":
                sec = int(now.strftime("%S")) / 60
                angle = (int(now.strftime("%M")) + sec) / 60 * 360
            else:
                angle = int(now.strftime("%M")) / 60 * 360

            self.minHand.setRotation(angle)

        if self.secHand != None:
            if self.smoothSec == "1":
                msec = int(now.strftime("%f")) / 1000000
                angle = (int(now.strftime("%S")) + msec)  / 60 * 360
            else:
                angle = int(now.strftime("%S")) / 60 * 360
            self.secHand.setRotation(angle)

    def startPreview(self):
        self.timer.start()
        self.updatePreviewHands()

    def stopPreview(self):
        self.timer.stop()
        if self.hrHand != None:
            self.hrHand.setRotation(300)
        if self.minHand != None:
            self.minHand.setRotation(48)
        if self.secHand != None:
            self.secHand.setRotation(0)

class PointerWidget(BaseWidget):
    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name)
        self.setPos(posX, posY)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, False)

    def addPointer(self, image, anchorX, anchorY, antialiasing):
        self.pointer = QGraphicsPixmapItem(image, self)
        self.pointer.setOffset(-int(anchorX), -int(anchorY))
        self.pointer.setPos(image.width()/2, image.height()/2)
        self.setRect(0, 0, image.width(), image.height())
        if antialiasing:
            self.pointer.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

class ProgressArc(QGraphicsEllipseItem):
    def __init__(self, posX, posY, width, height, parent, thickness, startAngle, endAngle, isFlat, pathImage):
        super().__init__(posX, posY, width, height, parent)
        pen = QPen()
        pen.setWidth(thickness)
        if pathImage.isNull():
            pen.setColor(QColor(255, 0, 0, 100))    
        else:
            pen.setBrush(QBrush(pathImage))
        
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)

        if isFlat == "1":
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        else:
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.setStartAngle(((endAngle * -1) + 90) * 16)
        self.setSpanAngle(((startAngle * -1) - (endAngle * -1)) * 16)
        self.setPen(pen)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())

class ProgressWidget(BaseWidget):
    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name, offsetX, offsetY, radius, thickness, startAngle, endAngle, isFlat, bgImage, pathImage, isAntialiased):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, transparency, name)
        self.setPos(posX, posY)
        
        radius = int(radius)
        thickness = int(thickness)
        startAngle = int(startAngle)
        endAngle = int(endAngle)
        
        self.setRect(0, 0, sizeX, sizeY)

        self.backgroundImage = QGraphicsPixmapItem(QPixmap(bgImage), self)
        
        radius = radius - thickness / 2

        self.arc = ProgressArc(
            int(offsetX) - radius - (thickness / 2), 
            int(offsetY) - radius - (thickness / 2), 
            (radius * 2) + thickness,
            (radius * 2) + thickness, 
            self, 
            int(thickness),
            startAngle,
            endAngle,
            isFlat,
            pathImage)

        if isAntialiased:
            self.backgroundImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            #self.arc.setTransformationMode(Qt.TransformationMode.SmoothTransformation)