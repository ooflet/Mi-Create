# Canvas for Mi Create
# ooflet <ooflet@proton.me>

# Responsible for rendering projects via QGraphicsView library.
# Pass a Project-derived class 

import os
import sys
import traceback
import logging
from pprint import pprint

sys.path.append("..")
from utils.project import WatchData

from PyQt6.QtCore import pyqtSignal, QPointF, QSize, QRect, QRectF, QLineF, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QPixmap, QIcon, QBrush
from PyQt6.QtWidgets import (QApplication, QGraphicsPathItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                            QToolButton, QGraphicsPixmapItem, QGraphicsEllipseItem, QMessageBox, QRubberBand, QGraphicsOpacityEffect)

from utils.contextMenu import ContextMenu

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "widget_analog" : "widget-analogdisplay",
            "widget" : "widget-image",
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
        self.positionMap = {"X":[], "Y":[]}
        for item in self.items():
            if isinstance(item, BaseWidget):
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

    def __init__(self, device, antialiasingEnabled: bool, deviceOutlineVisible: bool, ui: object, parent=None):
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
        insertButton.setIcon(QIcon().fromTheme("insert-object"))
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

    def createAnalogDisplay(self, name, pos, zValue, backgroundImage, hourHandImage, minuteHandImage, secondHandImage, itemAnchors, snap, interpolationStyle):
        # Create widget
        widget = AnalogWidget(int(pos.x()), int(pos.y()), int(pos.width()), int(pos.height()), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_analog") # Item ID
        widget.snap = snap

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
        
        if bgImg.isNull() and hrImg.isNull() and minImg.isNull() and secImg.isNull():
            widget.color = QColor(255, 0, 0, 100)

        return widget

    def createImage(self, name, rect, zValue, image, snap, interpolationStyle):
        # Create widget
        widget = ImageWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget") # Item ID
        widget.snap = snap

        # Add image
        pixmap = QPixmap()
        pixmap.load(os.path.join(self.imageFolder, image))

        widget.addImage(pixmap, 0, 0, 0, interpolationStyle)
        
        return widget

    def createImageList(self, name, rect, zValue, bitmapList, snap, interpolationStyle):
        # Create widget
        widget = ImageWidget(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_imagelist") # Item ID 
        widget.snap = snap

        # Split image strings from the Bitmaplist
        
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

    def createDigitalNumber(self, name, rect, zValue, numList, digits, spacing, snap, interpolationStyle):
        widget = ImageWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), name)
        widget.setZValue(zValue)
        widget.setData(1, "widget_imagelist") # Item ID
        widget.snap = snap

        for x in range(int(digits)):
            # Get QPixmap from file string
            if len(numList) >= 11:
                image = QPixmap()
                image.load(os.path.join(self.imageFolder, numList[x]))

                widget.addImage(image, (image.size().width() * x) + (int(spacing) * x), 0, int(spacing), interpolationStyle)
            else:
                widget.representNoImage()
                
        return widget

    def createProgressArc(self, name, rect, zValue, backgroundImage, arcImage, arcX, arcY, radius, lineWidth, startAngle, endAngle, isFlat, snap, interpolationStyle):
        bgImage = QPixmap()
        bgImage.load(os.path.join(self.imageFolder, backgroundImage))
    
        fgImage = QPixmap()
        fgImage.load(os.path.join(self.imageFolder, arcImage))
        
        # the amount of arguments is horrific, but im too lazy to fix it
        widget = ProgressWidget(rect.x(), rect.y(), rect.width(), rect.height(), self.frame, self, QColor(255,255,255,0), name, arcX, arcY, radius, lineWidth, startAngle, endAngle, isFlat, bgImage, fgImage, interpolationStyle)
        widget.setZValue(zValue)
        widget.setData(1, "widget_arc")
        widget.snap = snap

        return widget

    def createWidgetFromData(self, index, item, snap, interpolation):
        widget = None

        # qt calls this "smooth transformation" (????)
        if interpolation == "Bilinear":
            interpolation = True
        else:
            interpolation = False

        if item.getProperty("widget_type") == None:
            # invalid widget type (most likely not supported)
            # none type is returned when widget attempts to convert widget_type value into generic ID
            return False, f" Widget '{item.getProperty('widget_name')}' has unsupported widget type"

        try:
            if item.getProperty("widget_type") == "widget_analog":
                widget = self.createAnalogDisplay(
                    item.getProperty("widget_name"),
                    # use a QRect when defining position values
                    # i am quite retarded and used individual x,y,w,h values instead of using qrect
                    # oh well i'll fix later
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
                    snap,
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_arc":
                widget = self.createProgressArc(
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
                widget = self.createImage(
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

            elif item.getProperty("widget_type") == "widget_imagelist":
                widget = self.createImageList(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmaplist"),
                    snap,
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_num":
                widget = self.createDigitalNumber(
                    item.getProperty("widget_name"),
                    QRect(
                        int(item.getProperty("widget_pos_x")),
                        int(item.getProperty("widget_pos_y")),
                        int(item.getProperty("widget_size_width")),
                        int(item.getProperty("widget_size_height"))
                    ),
                    index,
                    item.getProperty("widget_bitmaplist"),
                    item.getProperty("num_digits"),
                    item.getProperty("num_spacing"),
                    snap,
                    interpolation
                )

            elif item.getProperty("widget_type") == "widget_arc":
                widget = self.createProgressArc(
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
                # this only happens in the rare off chance when the item is implemented in generic widget IDs
                return False, f"Widget {item.getProperty('widget_type')} not implemented in canvas, please report as issue."

            # add widget into widget list
            print(item.getProperty("widget_name"))
            pprint(self.widgets)
            self.widgets[item.getProperty("widget_name")] = widget
            return True, "Success"
        except Exception:
            return False, str(f" Unable to create object {item.getProperty('widget_name')}:\n {traceback.format_exc()}")

    def loadObjects(self, project, snap=None, interpolation=None, clip=True, outline=False):
        print(clip, outline)
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
        if project.widgets != None:
            self.scene().clear()
            self.widgets.clear()
            #self.scene().addItem(self.deviceRep)
            self.scene().addItem(self.frame)

            if outline:
                self.deviceOutline = DeviceOutline(self.deviceSize)
                self.scene().addItem(self.deviceOutline)
 
            self.imageFolder = project.imageFolder

            self.scene().originPositons = {}

            widgets = project.getAllWidgets()
            if type(widgets) == list:
                for index, widget in enumerate(widgets):    
                    result, reason = self.createWidgetFromData(index, widget, snap, interpolation)
                    self.scene().originPositions[widget.getProperty("widget_name")] = [int(widget.getProperty("widget_pos_x")), int(widget.getProperty("widget_pos_y"))]
                    if not result:
                        return False, reason
                self.scene().updatePosMap()
                return True, "Success"
            else:
                return False, "Widgets not in list!"
            
        else:
            self.scene().addItem(self.frame)
            return True, "Success"
        
    def reloadObject(self, objectName, widget):
        # loads a single object without reloading every object in the canvas
        # if using on a mass set of objects, its usually easier to call the loadobjects function
        object = self.widgets[objectName]
        objectZValue = object.zValue()

        if object != None:

            result, reason = self.createWidgetFromData(objectZValue, widget, self.snap, self.interpolation)
            if not result:
                return False, reason 
            else:
                self.scene().originPositions[objectName] = [int(widget.getProperty("widget_pos_x")), int(widget.getProperty("widget_pos_y"))]
                self.scene().updatePosMap()
                object.selectionPath.prepareGeometryChange()
                object.delete()
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
        self.origPos = None
        self.size = QPointF(sizeX, sizeY)
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
            self.selectionPainterPath.clear()
            self.selectionPainterPath.addRoundedRect(self.pos().x(), self.pos().y(), self.rect().width(), self.rect().height(), self.highlightRadius, self.highlightRadius)
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

        width = ( qPixmap.width() * len(self.imageItems) ) + ( spacing * len(self.imageItems) )
        self.setRect(0, 0, width, qPixmap.height())

    def clearImages(self):
        for x in self.imageItems:
            self.scene().removeItem(x)
        self.imageItems.clear()

    def representNoImage(self):
        self.color = QColor(255, 0, 0, 100)

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
        self.secHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.secHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addMinuteHand(self, minHandImage, minHandX, minHandY, antialiasing):
        self.minHand = QGraphicsPixmapItem(minHandImage, self)
        self.minHand.setOffset(-int(minHandX), -int(minHandY))
        self.minHand.setRotation(60)
        self.minHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.minHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addHourHand(self, hourHandImage, hrHandX, hrHandY, antialiasing):
        self.hrHand = QGraphicsPixmapItem(hourHandImage, self)
        self.hrHand.setOffset(-int(hrHandX), -int(hrHandY))
        self.hrHand.setRotation(-60)
        self.hrHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.hrHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

class ProgressArc(QGraphicsEllipseItem):
    def __init__(self, posX, posY, width, height, parent, thickness, startAngle, endAngle, isFlat, pathImage):
        super().__init__(posX, posY, width, height, parent)
        pen = QPen()
        pen.setWidth(thickness)
        QPixmap.isNull
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
        print(pen)
        self.setPen(pen)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())

class ProgressWidget(BaseWidget):
    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, name, offsetX, offsetY, radius, thickness, startAngle, endAngle, isFlat, bgImage, pathImage, isAntialiased):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, name)
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