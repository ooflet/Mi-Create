# Canvas for Mi Create
# tostr 2023

# Responsible for rendering parsed EasyFace XML projects via QGraphicsView library.
# Parse a fprj/xml file to a dictionary, create a Canvas object and call loadObjectsFromData

import os
import sys
import traceback
import logging
from tracemalloc import start

sys.path.append("..")
from utils.project import watchData

from PyQt6.QtCore import pyqtSignal, QPointF, QSize, QRect, QRectF, QLineF, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QPixmap, QIcon, QBrush
from PyQt6.QtWidgets import (QApplication, QGraphicsPathItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                            QToolButton, QGraphicsPixmapItem, QMessageBox, QRubberBand)

from utils.contextMenu import ContextMenu

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "27":"widget-analogdisplay",
            "30":"widget-image",
            "31":"widget-imagelist",
            "32":"widget-digitalnumber",
            "42":"widget-arcprogress"
        }

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
        self.setAcceptDrops(True) # just in case i implement image drag & drop

        self.zoomValue = 0

        self.deviceSize = watchData().modelSize[str(device)]

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
            self.widgets[item["Name"]].setSelected(True)

    def getSelectedObjects(self):
        return self.scene().selectedItems()

    def onObjectDeleted(self, name, widget):
        self.objectDeleted.emit(name)

    def createObject(self, index, i, imageFolder, interpolation):
        widget = None

        if interpolation == "Bilinear":
            interpolation = True
        else:
            interpolation = False

        try:
            if i["@Shape"] == "27":
                bgImg = QPixmap()
                bgImg.load(os.path.join(imageFolder, i["@Background_ImageName"]))

                secImg = QPixmap()
                secImg.load(os.path.join(imageFolder, i["@SecondHand_Image"]))

                minImg = QPixmap()
                minImg.load(os.path.join(imageFolder, i["@MinuteHand_Image"]))

                hrImg = QPixmap()
                hrImg.load(os.path.join(imageFolder, i["@HourHand_ImageName"]))

                # Create analogwidget
                widget = AnalogWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self.frame, self, QColor(255,255,255,0), i["@Name"])
                widget.setZValue(index)
                widget.setData(1, "27")
                widget.addBackground(bgImg, i["@BgImage_rotate_xc"], i["@BgImage_rotate_yc"], interpolation)
                widget.addHourHand(hrImg, i["@HourImage_rotate_xc"], i["@HourImage_rotate_yc"], interpolation)
                widget.addMinuteHand(minImg, i["@MinuteImage_rotate_xc"], i["@MinuteImage_rotate_yc"], interpolation)
                widget.addSecondHand(secImg, i["@SecondImage_rotate_xc"], i["@SecondImage_rotate_yc"], interpolation)

            elif i["@Shape"] == "29":
                #dialog = QMessageBox.warning(None, "Confirm", f"The object {i['@Name']} uses the legacy CircleProgress object, it will be automatically converted to the newer CircleProgressPlus object.")
                pass

            elif i["@Shape"] == "30":    
                # image
                widget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self.frame, self, QColor(255,255,255,0), i["@Name"], imageFolder)
                widget.setZValue(index)
                widget.setData(1, "30")

                if i["@Bitmap"] != "":
                    # Get QPixmap from file string
                    image = QPixmap()
                    image.load(os.path.join(imageFolder, i["@Bitmap"]))

                    # Create imagewidget    
                    widget.addImage(image, 0, 0, 0, interpolation)
                else:
                    self.scene().addItem(widget)
                    widget.representNoImage()
                
            elif i["@Shape"] == "31":
                # image list
                widget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self.frame, self, QColor(255,255,255,0), i["@Name"], imageFolder)
                widget.setZValue(index)
                widget.setData(1, "31")
                
                # Split image strings from the Bitmaplist
                imageList = i["@BitmapList"].split("|")
                firstImage = imageList[0].split(":")

                if i["@BitmapList"] != "":
                    # Get Image
                    if len(firstImage) >= 2:
                        image = QPixmap()
                        image.load(os.path.join(imageFolder, firstImage[1]))
                        widget.addImage(image, 0, 0, 0, interpolation)
                    else:
                        widget.representNoImage()
                else:
                    widget.addImage(QPixmap(), 0, 0, 0, interpolation)
                    widget.representNoImage()

            elif i["@Shape"] == "32":
                # digital number

                # Split images from the Bitmaplist
                imageList = i["@BitmapList"].split("|")
                widget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self.frame, self, QColor(255,255,255,100), i["@Name"], imageFolder)
                widget.setZValue(index)
                widget.setData(1, "32")

                if len(imageList) != 11:
                    widget.representNoImage()
                else:
                    widget.loadNumbers(i["@Digits"], i["@Spacing"], imageList, interpolation)

            elif i["@Shape"] == "42":
                # progress widget
                
                bgImage = QPixmap()
                bgImage.load(os.path.join(imageFolder, i["@Background_ImageName"]))
            
                fgImage = QPixmap()
                fgImage.load(os.path.join(imageFolder, i["@Foreground_ImageName"]))
                
                widget = ProgressWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self.frame, self, QColor(255,255,255,0), i["@Name"], i["@Rotate_xc"], i["@Rotate_yc"], i["@Radius"], i["@Line_Width"], i["@StartAngle"], i["@EndAngle"], bgImage, fgImage, interpolation)
                widget.setZValue(index)
                widget.setData(1, "42")

            else:
                return False, f"Widget {i['@Shape']} not implemented in canvas, please report as issue."
            
            self.widgets[i["@Name"]] = widget
            self.scene().addItem(widget)
            return True, "Success"
        except Exception as e:
            QMessageBox().critical(None, "Error", f"Unable to create object {i['@Name']}: {traceback.format_exc()}")
            return False, str(e)

    def loadObjects(self, data, imageFolder, interpolation):
        self.frame = DeviceFrame(self.deviceSize)
        if data["FaceProject"]["Screen"].get("Widget") != None:
            self.scene().clear()
            self.widgets.clear()
            self.scene().addItem(self.frame)

            widgets = data["FaceProject"]["Screen"]["Widget"]
            if type(widgets) == dict:
                for index, key in enumerate(widgets):     
                    result, reason = self.createObject(index, widgets[key], imageFolder, interpolation)
                    if not result:
                        return False, reason
                self.scene().updatePosMap()
                return True, "Success"
            
        else:
            self.scene().addItem(self.frame)
            return True, "Success"
        
    def reloadObject(self, objectName, objectData, imageFolder, interpolation):
        object = self.widgets[objectName]
        objectZValue = object.zValue()

        if object != None:
            object.delete()
            result, reason = self.createObject(objectZValue, objectData, imageFolder, interpolation)
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

    def __init__(self, posX, posY, sizeX, sizeY, parent, canvas, color, name, srcDir):
        super().__init__(posX, posY, sizeX, sizeY, parent, canvas, color, name)
        self.srcDir = srcDir
        self.imageItems = []
        self.setPos(posX, posY)

    def loadNumbers(self, digits, spacing, numList,  antialiasing):
        self.digits = digits
        self.numList = numList
        self.spacing = spacing
        self.antialiasing = antialiasing
        # Loop through digits
        for x in range(int(digits)):
            # Get QPixmap from file string
            if len(numList) == 11:
                image = QPixmap()
                image.load(os.path.join(self.srcDir, numList[x]))

                self.addImage(image, image.size().width()*x+(int(self.spacing)*x), 0, int(self.spacing), antialiasing)
            else:
                self.representNoImage()

    def addImage(self, qPixmap, posX, posY, spacing, isAntialiased):
        item = QGraphicsPixmapItem(qPixmap, self)
        item.setPos(posX, posY)
        self.imageItems.append(item)
        if isAntialiased:
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.color = QColor(0,0,0,0)
        self.setBrush(QBrush(self.color))
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