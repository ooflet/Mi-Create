# Canvas
# tostr 2023

# Responsible for rendering parsed EasyFace XML projects via QGraphicsView library.
# Parse a fprj/xml file to a dictionary, create a Canvas object and call loadObjectsFromData

import os
import sys
import traceback
import logging
from tracemalloc import start

sys.path.append("..")
from utils.project import WatchData

from PyQt6.QtCore import pyqtSignal, QPointF, QSize, QRect, QRectF, QLineF, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QPixmap, QIcon, QBrush
from PyQt6.QtWidgets import (QApplication, QGraphicsPathItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                            QToolButton, QGraphicsPixmapItem, QMessageBox, QRubberBand, QGraphicsBlurEffect, QGraphicsOpacityEffect)

from utils.contextMenu import ContextMenu
from utils.project import FprjProject

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "widget_analog":"widget-analogdisplay",
            "widget":"widget-image",
            "widget_imagelist":"widget-imagelist",
            "widget_num":"widget-digitalnumber",
            "widget_arc":"widget-arcprogress"
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
        self.setPen(QPen(QColor(200, 200, 200, 100), thickness, Qt.PenStyle.SolidLine))
        self.setBrush(QColor(0,0,0,0))
        self.setZValue(9999)

class DeviceFrame(QGraphicsPathItem):
    # Shape that crops the screen to the border radius
    def __init__(self, size):
        super().__init__()
        outline = QPainterPath()
        outline.addRoundedRect(0, 0, size[0], size[1], size[2], size[2])
        self.setPath(outline)
        self.setBrush(QColor(0,0,0,255))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)
        self.setZValue(0)

class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.positionMap = {
            "X": [],
            "Y": []
        }
        self.posLines = []

    def updatePosMap(self):
        self.positionMap = {"X":[], "Y":[]}
        for item in self.items():
            if isinstance(item, BaseWidget):
                self.positionMap["X"].append(item.pos().x())
                self.positionMap["X"].append(item.pos().x() + item.rect().width())
                self.positionMap["Y"].append(item.pos().y())
                self.positionMap["Y"].append(item.pos().y() + item.rect().height())

    def getAdjacentPos(self, object: QGraphicsItem):
        catchRange = 10 # pixel offset before the object gets snapped
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

        print(pos)
        return pos
    
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
    onObjectAdded = pyqtSignal(QPointF, str)
    onObjectChange = pyqtSignal(str, str, object) # hate hacky workarounds, just support any type already Qt
    onObjectPosChange = pyqtSignal()

    def __init__(self, device: int, antialiasingEnabled: bool, deviceOutlineVisible: bool, ui: object, parent=None):
        super().__init__(parent)

        if antialiasingEnabled:
            self.setRenderHints(QPainter.RenderHint.Antialiasing)

        self.mainWindowUI = ui # used for ContextMenu, it needs window UI to access QActions
        self.widgets = {}

        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse) # positions scene to zoom under mouse

        self.deviceOutlineVisible = deviceOutlineVisible
        self.origin = None
        self.setAcceptDrops(True) # just in case item implement image drag & drop

        self.zoomValue = 0

        self.deviceSize = WatchData().modelSize[str(device)]

        self.graphicsScene = Scene()
        self.graphicsScene.setSceneRect(0,0,self.deviceSize[0],self.deviceSize[1])

        self.deviceOutline = DeviceOutline(self.deviceSize)
        
        self.drawDecorations()

        self.setScene(self.graphicsScene)

    def fireObjectPositionChanged(self):
        self.scene().updatePosMap()
        self.onObjectPosChange.emit()

    def drawDecorations(self):
        insertButton = QToolButton(self)
        insertButton.setObjectName("canvasDecoration-button")
        insertButton.setGeometry(20, 20, 40, 25)
        insertButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        insertButton.setMenu(self.mainWindowUI.menuInsert)
        insertButton.setIcon(QIcon(":Dark/plus.png"))
        insertButton.setIconSize(QSize(18, 18))
        insertButton.setToolTip("Create Widget")
        insertButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    def mousePressEvent(self, event):
        if not any(isinstance(item, BaseWidget) for item in self.items(event.pos())):
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
        
        #print(topLevelItem, topLevelItem.zValue())

        if topLevelItem != None:
            if not topLevelItem.isSelected():
                self.scene().clearSelection()
                topLevelItem.setSelected(True)
            menu = ContextMenu("shape", viewPos, self.mainWindowUI)
        else:
            menu = ContextMenu("default", viewPos, self.mainWindowUI)

        action = menu.exec(viewPos)

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

    def selectObject(self, name):
        if name == None:
            return
        self.scene().clearSelection()
        self.widgets[name].setSelected(True)

    def selectObjectsFromPropertyList(self, items: list):
        for item in items:
            self.widgets[item.getProperty("Name")].setSelected(True)

    def getSelectedObjects(self):
        return self.scene().selectedItems()

    def onObjectDeleted(self, name, widget):
        self.objectDeleted.emit(name)

    def createAnalogDisplay(self, name, pos, zValue, backgroundImage, hourHandImage, minuteHandImage, secondHandImage, itemAnchors, interpolationStyle):
        # Create widget
        widget = AnalogWidget(int(pos.x()), int(pos.y()), int(pos.width()), int(pos.height()), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_analog") # Item ID

        # Add images

        bgImg = QPixmap()
        bgImg.load(os.path.join(self.imageFolder, backgroundImage))

        hrImg = QPixmap()
        hrImg.load(os.path.join(self.imageFolder, hourHandImage))

        minImg = QPixmap()
        minImg.load(os.path.join(self.imageFolder, minuteHandImage))
        
        secImg = QPixmap()
        secImg.load(os.path.join(self.imageFolder, secondHandImage))

        widget.addBackground(bgImg, itemAnchors["background"]["x"], itemAnchors["background"]["y"], interpolationStyle)
        widget.addHourHand(hrImg, itemAnchors["hour"]["x"], itemAnchors["hour"]["y"], interpolationStyle)
        widget.addMinuteHand(minImg, itemAnchors["minute"]["x"], itemAnchors["minute"]["y"], interpolationStyle)
        widget.addSecondHand(secImg, itemAnchors["second"]["x"], itemAnchors["second"]["y"], interpolationStyle)
        
        return widget

    def createImage(self, name, rect, zValue, image, interpolationStyle):
        # Create widget
        widget = ImageWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget") # Item ID

        # Add image
        pixmap = QPixmap()
        pixmap.load(os.path.join(self.imageFolder, image))

        widget.addImage(pixmap, 0, 0, 0, interpolationStyle)
        
        return widget

    def createImageList(self, name, rect, zValue, bitmapList, interpolationStyle):
        # Create widget
        widget = ImageWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_imagelist") # Item ID 

        # Split image strings from the Bitmaplist
        
        print(bitmapList)
        firstImage = bitmapList[0]

        if bitmapList != []:
            # Get Image
            if len(firstImage) >= 2:
                image = QPixmap()
                image.load(os.path.join(self.imageFolder, firstImage[1]))
                widget.addImage(image, 0, 0, 0, interpolationStyle)
            else:
                widget.representNoImage()
        else:
            widget.addImage(QPixmap(), 0, 0, 0, interpolationStyle)
            
        return widget

    def createDigitalNumber(self, name, rect, zValue, numList, digits, spacing, interpolationStyle):
        widget = ImageWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_imagelist") # Item ID

        for x in range(int(digits)):
            # Get QPixmap from file string
            if len(numList) == 11:
                image = QPixmap()
                image.load(os.path.join(self.imageFolder, numList[x]))

                widget.addImage(image, (image.size().width() * x) + (int(spacing) * x), 0, int(spacing), interpolationStyle)
            else:
                self.representNoImage()
                
        return widget

    def createProgressArc(self, name, rect, zValue, backgroundImage, arcImage, arcX, arcY, radius, lineWidth, startAngle, endAngle, interpolationStyle):
        bgImage = QPixmap()
        bgImage.load(os.path.join(self.imageFolder, backgroundImage))
    
        fgImage = QPixmap()
        fgImage.load(os.path.join(self.imageFolder, arcImage))
        
        # the amount of arguments is horrific, but im too lazy to fix it
        widget = ProgressWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), name, arcX, arcY, radius, lineWidth, startAngle, endAngle, bgImage, fgImage, interpolationStyle)
        widget.setZValue(zValue)
        widget.setData(1, "widget_arc")

        return widget

    def createWidgetFromData(self, index, item, interpolation):
        widget = None

        if interpolation == "Bilinear":
            interpolation = True
        else:
            interpolation = False

        try:
            if item.getProperty("widget_type") == "widget_analog":
                widget = self.createAnalogDisplay(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_height"))
                    ),
                    index,
                    item.getProperty("analog_background"),
                    item.getProperty("analog_hour_image"),
                    item.getProperty("analog_minute_image"),
                    item.getProperty("analog_second_image"),
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
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_arc":
                widget = self.createProgressArc(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_height"))
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
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget":
                widget = self.createImage(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmap"),
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_imagelist":
                widget = self.createImageList(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmaplist"),
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_num":
                widget = self.createDigitalNumber(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmaplist"),
                    item.getProperty("num_digits"),
                    item.getProperty("num_spacing"),
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_arc":
                widget = self.createProgressArc(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_height"))
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
                    interpolation
                )

            else:
                return False, f"Widget {item.getProperty('widget_type')} not implemented in canvas, please report as issue."

            self.widgets[item.getProperty("widget_name")] = widget
            self.scene().addItem(widget)
            return True, "Success"
        except Exception as e:
            QMessageBox().critical(None, "Error", f"Unable to create object {item.getProperty('widget_name')}: {traceback.format_exc()}")
            return False, str(e)

    def loadObjects(self, project, interpolation):
        self.frame = DeviceFrame(self.deviceSize)
        #self.deviceRep = DeviceRepresentation(project.getDeviceType(), interpolation)
        if project.widgets != None:
            self.scene().clear()
            self.widgets.clear()
            #self.scene().addItem(self.deviceRep)
            print("frame")
            self.scene().addItem(self.frame)
 
            self.imageFolder = project.imageFolder

            widgets = project.getAllWidgets()
            if type(widgets) == list:
                for index, widget in enumerate(widgets):    
                    result, reason = self.createWidgetFromData(index, widget, interpolation)
                    if not result:
                        return False, reason
                self.scene().updatePosMap()
                return True, "Success"
            else:
                return False, "Widgets not in list!"
            
        else:
            print("frame")
            self.scene().addItem(self.frame)
            return True, "Success"
        
    def reloadObject(self, objectName, objectData, interpolation):
        object = self.widgets[objectName]
        objectZValue = object.zValue()

        if object != None:
            object.delete()
            result, reason = self.createObject(objectZValue, objectData, interpolation)
            if not result:
                return False, reason 
            else:
                self.scene().updatePosMap()
                return True, "Success"
        
class BaseWidget(QGraphicsRectItem):
    # Basic widget with draggable and selectable controls
    # Allows for snap to guides
    # Adding child QGraphicsItems to this widget extends functionality 

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, name):
        # Initialize the shape.
        super().__init__(posX, posY, sizeX, sizeY, parent)
        self.setRect(0, 0, sizeX, sizeY)
        self.setPen(QPen(QColor(0,0,0,0)))
        self.size = QPointF(sizeX, sizeY)
        self.color = color
        self.canvas = canvas
        self.selectionPos = None
        self.selectionPath = QGraphicsPathItem()
        self.selectionPainterPath = QPainterPath()
        self.highlightThickness = 2
        self.highlightRadius = 3
        self.scene().addItem(self.selectionPath)
        self.setAcceptHoverEvents(True)
        self.setData(0, name)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)

    def boundingRect(self):
        # Creates outline and patches bounding box ghosting
        if self.selectionPos == None or self.pos().x() != self.selectionPos.x() or self.pos().y() != self.selectionPos.y():
            self.selectionPos = self.pos()
            self.selectionPainterPath.clear()
            self.selectionPainterPath.addRoundedRect(self.pos().x(), self.pos().y(), self.rect().width(), self.rect().height(), self.highlightRadius, self.highlightRadius)
            self.selectionPath.setPath(self.selectionPainterPath)
            self.selectionPath.setPen(QPen(self.scene().palette().highlight(), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        outline_width = 2  # Adjust this value as needed
        return self.rect().adjusted(-outline_width, -outline_width, outline_width, outline_width)
    
    def getRect(self):
        return self.rect()
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(event)

        # handle snap
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

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(self.pen())

        if self.isSelected():
            self.selectionPath.show()
        else:
            self.selectionPath.hide()

        painter.drawRect(self.rect())

class ImageWidget(BaseWidget):
    # Widget for basic images and handling for DigitalNumber
    # All ImageList related things are handled in the addImage function
    # Live previews of animations are planned with this widget

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, name):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, name)
        self.imageItems = []
        self.setPos(posX, posY)

    def addImage(self, qPixmap, posX, posY, spacing, isAntialiased):
        if qPixmap.isNull():
            self.representNoImage()
            return
        item = QGraphicsPixmapItem(qPixmap, self)
        item.setPos(posX, posY)
        self.imageItems.append(item)
        if isAntialiased:
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setRect(0, 0, qPixmap.width()*len(self.imageItems)+spacing*len(self.imageItems)-spacing, qPixmap.height())

    def clearImages(self):
        for x in self.imageItems:
            self.scene().removeItem(x)
        self.imageItems.clear()

    def representNoImage(self):
        self.color = QColor(255, 0, 0, 100)
        self.setRect(0,0,48,48)

class AnalogWidget(BaseWidget):
    # Widget for handling AnalogDisplays
    
    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, name):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, name)
        self.setPos(posX, posY)

    def addBackground(self, backgroundImage, bgX, bgY, antialiasing):
        if backgroundImage != "":
            self.background = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage.setPos(int(bgX), int(bgY))
        if antialiasing:
            self.bgImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addSecondHand(self, secHandImage, secHandX, secHandY, antialiasing):
        self.secHand = QGraphicsPixmapItem(secHandImage, self)
        self.secHand.setOffset(-int(secHandX), -int(secHandY))
        if secHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
        self.secHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.secHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addMinuteHand(self, minHandImage, minHandX, minHandY, antialiasing):
        if minHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
        self.minHand = QGraphicsPixmapItem(minHandImage, self)
        self.minHand.setOffset(-int(minHandX), -int(minHandY))
        self.minHand.setRotation(60)
        self.minHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.minHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addHourHand(self, hourHandImage, hrHandX, hrHandY, antialiasing):
        if hourHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
        self.hrHand = QGraphicsPixmapItem(hourHandImage, self)
        self.hrHand.setOffset(-int(hrHandX), -int(hrHandY))
        self.hrHand.setRotation(-60)
        self.hrHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.hrHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)


class CircularArcItem(QGraphicsPathItem):
    # hate this so much!!!!!!!!
    def __init__(self, rect, start_angle, end_angle, width, thickness, parent=None):
        super().__init__(parent)
        self.rect = QRectF(rect)
        self.start_angle = -end_angle + 90
        self.span_angle = abs(start_angle) + abs(end_angle)
        print(self.start_angle, self.span_angle)
        self.thickness = thickness
        self.width = width/2

        self.setPath(self.createArcPath())

    def createArcPath(self):
        path = QPainterPath()

        # draw external arc
        path.arcMoveTo(self.rect, self.start_angle)
        path.arcTo(self.rect, self.start_angle, self.span_angle)

        # draw internal arc
        small_radius = min(self.rect.width(), self.rect.height()) * self.thickness / self.rect.width()
        path.arcTo(self.rect.adjusted(small_radius, small_radius, -small_radius, -small_radius),
                   self.start_angle + self.span_angle, -self.span_angle)
        path.closeSubpath()

        return path
    
class CirclularArcImage(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent, posX, posY, radius, thickness, start_angle, span_angle, antialiased):
        super().__init__(pixmap, parent)
        self.posX = int(posX)
        self.posY = int(posY)
        self.radius = radius
        self.thickness = thickness
        self.startAngle = start_angle
        self.endAngle = span_angle
        self.antialiased = antialiased

    def boundingRect(self):
        return QRectF(0, 0, self.pixmap().width(), self.pixmap().height())

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, self.antialiased)
        if self.pixmap().isNull():
            brush = QBrush(QColor(255, 0, 0, 100))
        else:
            brush = QBrush(self.pixmap())
        pen = QPen(QColor(255,255,255,255))
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setBrush(brush)
        painter.setPen(pen)

        diameter = 2 * self.radius
        arc_rect = QRectF(self.posX - self.radius - (self.thickness / 2), self.posY - self.radius - (self.thickness / 2), diameter + self.thickness, diameter + self.thickness)
        
        # Draw using image brush. Its very bad to use, will implement soon
        painter.drawPath(CircularArcItem(arc_rect, self.startAngle, self.endAngle, self.pixmap().width(), self.thickness).createArcPath())

class ProgressWidget(BaseWidget):
    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, name, offsetX, offsetY, radius, thickness, startAngle, endAngle, bgImage, pathImage, isAntialiased):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, name)
        self.setPos(posX, posY)
        self.setRect(0, 0, sizeX, sizeY)

        radius = int(radius)
        thickness = int(thickness)
        startAngle = int(startAngle)
        endAngle = int(endAngle)

        # self.arcRect = QRectF(int(offsetX) - radius - (thickness / 2), int(offsetY) - radius - (thickness / 2), radius * 2 + thickness, radius * 2 + thickness)
        # print(self.arcRect)

        # self.arcPath = QPainterPath()
        # self.arcPath.moveTo(radius, radius)
        # self.arcPath.arcTo(self.arcRect, startAngle, endAngle)

        # self.arcImage = QBrush(bgImage)

        # self.arcPen = QPen()
        # self.arcPen.setBrush(self.arcImage)
        # self.arcPen.setWidth(thickness)
        # self.arcPen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.backgroundImage = QGraphicsPixmapItem(bgImage, self)

        self.pathImage = CirclularArcImage(pathImage, self, offsetX, offsetY, radius, thickness, startAngle, endAngle, isAntialiased)

        if isAntialiased:
            self.backgroundImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self.pathImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)