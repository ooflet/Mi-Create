# Canvas for Mi Create
# tostr 2023

# Responsible for rendering parsed EasyFace XML projects via QGraphicsView library.
# Parse an xml file to a dictionary, create a Canvas object and call loadObjectsFromData

import os
import sys
import traceback
import logging
from tracemalloc import start
from typing import Any

sys.path.append("..")
from project.projectManager import watchData

from PySide6.QtCore import Signal, QPointF, QModelIndex, QSize, QRectF, QRect
from PySide6.QtGui import Qt, QPainter, QPainterPath, QPen, QColor, QStandardItemModel, QPixmap, QIcon, QBrush, QImage
from PySide6.QtWidgets import (QApplication, QGraphicsPathItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                               QGraphicsEllipseItem, QMenu, QGraphicsPixmapItem, QMessageBox, QRubberBand)

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "27":":Dark/analog.png",
            "30":":Dark/image.png",
            "31":":Dark/gallery-horizontal.png",
            "32":":Dark/numbers.png",
            "42":":Dark/progress.png"
        }

class DeviceOutline(QGraphicsPathItem):
    # Creates the grey outline showing how rounded the screen is
    def __init__(self, size):
        super().__init__()
        thickness = 5
        outline = QPainterPath()
        outline.addRoundedRect(thickness/2, thickness/2, (size[0]-thickness), (size[1]-thickness), size[2], size[2])
        self.setPath(outline)
        self.setPen(QPen(QColor(200, 200, 200, 100), thickness, Qt.SolidLine))
        self.setBrush(QColor(0,0,0,0))
        self.setZValue(9999)

class Scene(QGraphicsScene):
    itemSelectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def selectionChanged(self):
        super().selectionChanged()
        self.itemSelectionChanged.emit()

class Canvas(QGraphicsView):
    objectAdded = Signal(QPointF, str)
    objectChanged = Signal(str, str, Any)
    objectLayerChange = Signal(str, str)
    objectDeleted = Signal(str)

    def __init__(self, device, antialiasingEnabled, deviceOutlineVisible, insertMenu, parent=None):
        super().__init__(parent)

        if antialiasingEnabled:
            self.setRenderHints(QPainter.Antialiasing)

        #self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.insertMenu = insertMenu
        self.deviceOutlineVisible = deviceOutlineVisible
        self.origin = None
        self.setAcceptDrops(True)

        self.zoomValue = 0

        self.deviceSize = watchData().modelSize[str(device)]

        self.scene = Scene()
        self.scene.setSceneRect(0,0,self.deviceSize[0],self.deviceSize[1])

        self.drawDecorations(deviceOutlineVisible)

        self.setScene(self.scene)

    def fireObjectPositionChanged(self, name, x, y):
        self.objectChanged.emit(name, "@X", x)
        self.objectChanged.emit(name, "@Y", y)

    def drawDecorations(self, deviceOutlineVisible):
        background = QGraphicsRectItem(0, 0, self.deviceSize[0], self.deviceSize[1])
        background.setPen(QPen(Qt.NoPen))
        background.setBrush(QColor(0, 0, 0, 255))
        
        self.scene.addItem(background)

        if deviceOutlineVisible:
            self.scene.addItem(DeviceOutline(self.deviceSize))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        scenePos = self.mapToScene(event.pos())  # Convert to scene coordinates

        # Calculate the offset between the view's top-left corner and the rectangle's top-left corner
        viewRect = self.viewport().rect()
        sceneRect = self.sceneRect()
        offset = QPointF(sceneRect.x() - viewRect.x(), sceneRect.y() - viewRect.y())

        # Subtract the offset from the drop position to get the position relative to the rectangle
        relativePos = scenePos - offset

        model = QStandardItemModel()
        model.dropMimeData(event.mimeData(), Qt.CopyAction, 0, 0, QModelIndex())
        self.objectAdded.emit(relativePos, model.item(0, 0).data(99))

        event.acceptProposedAction()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            zoom_factor = 1.25 if delta > 0 else 1 / 1.25
            self.scale(zoom_factor, zoom_factor)

        elif modifiers == Qt.AltModifier:
            scroll_delta = event.angleDelta().x()
            scroll_value = self.horizontalScrollBar().value() - scroll_delta
            self.horizontalScrollBar().setValue(scroll_value)
        else:
            scroll_delta = event.angleDelta().y()
            scroll_value = self.verticalScrollBar().value() - scroll_delta
            self.verticalScrollBar().setValue(scroll_value)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                zoom_factor = 1.25
                self.scale(zoom_factor, zoom_factor)
            elif event.key() == Qt.Key_Minus:
                zoom_factor = 1 / 1.25
                self.scale(zoom_factor, zoom_factor)
            event.accept()
        else:
            super().keyPressEvent(event)

    def handleObjectSelectionChange(self):
        selected_object = self.getSelectedObject()
        if selected_object:
            print(f"Object '{selected_object}' selected")

    def selectObject(self, name):
        for x in self.items():
            # data(0) is name
            if x.data(0) == name:
                x.setSelected(True)
            else:
                x.setSelected(False)

    def getSelectedObject(self):
        return self.scene.selectedItems()

    def onObjectDeleted(self, name, widget):
        self.objectDeleted.emit(name)

    def createObject(self, index, i, imageFolder, antialiasing):
        # so many hacks
        # dear god
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
                analogWidget = AnalogWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self, QColor(255,255,255,0), i["@Name"])
                analogWidget.setZValue(index)
                analogWidget.addBackground(bgImg, i["@BgImage_rotate_xc"], i["@BgImage_rotate_yc"], antialiasing)
                analogWidget.addHourHand(hrImg, i["@HourImage_rotate_xc"], i["@HourImage_rotate_yc"], antialiasing)
                analogWidget.addMinuteHand(minImg, i["@MinuteImage_rotate_xc"], i["@MinuteImage_rotate_yc"], antialiasing)
                analogWidget.addSecondHand(secImg, i["@SecondImage_rotate_xc"], i["@SecondImage_rotate_yc"], antialiasing)
                self.scene.addItem(analogWidget)
                analogWidget.objectDeleted = lambda name, self=self: self.onObjectDeleted(name, analogWidget)
                analogWidget.objectLayerAction = lambda name, action: self.objectLayerChange.emit(name, action)

            elif i["@Shape"] == "29":
                dialog = QMessageBox.warning(None, "Confirm", f"The object {i['@Name']} uses the legacy CircleProgress object, it will be automatically converted to the newer CircleProgressPlus object.")

            elif i["@Shape"] == "30":    
                imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self, QColor(255,255,255,0), i["@Name"], imageFolder)
                imageWidget.setZValue(index)

                if i["@Bitmap"] != "":
                    # Get QPixmap from file string
                    image = QPixmap()
                    image.load(os.path.join(imageFolder, i["@Bitmap"]))

                    # Create imagewidget    
                    imageWidget.addImage(image, 0, 0, 0, antialiasing)
                    self.scene.addItem(imageWidget)
                else:
                    self.scene.addItem(imageWidget)
                    imageWidget.addImage(QPixmap(), 0, 0, 0, antialiasing)
                    imageWidget.representNoImage()
                
                imageWidget.objectDeleted = lambda name, self=self: self.onObjectDeleted(name, imageWidget)
                imageWidget.objectLayerAction = lambda name, action: self.objectLayerChange.emit(name, action)
                
            elif i["@Shape"] == "31":
                imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self, QColor(255,255,255,0), i["@Name"], imageFolder)
                imageWidget.setZValue(index)
                
                # Split image strings from the Bitmaplist
                imageList = i["@BitmapList"].split("|")
                firstImage = imageList[0].split(":")

                if i["@BitmapList"] != "":
                    # Get Image
                    if len(firstImage) >= 2:
                        image = QPixmap()
                        image.load(os.path.join(imageFolder, firstImage[1]))
                        imageWidget.addImage(image, 0, 0, 0, antialiasing)
                    else:
                        imageWidget.representNoImage()
                    name = i["@Name"]
                    self.scene.addItem(imageWidget)
                else:
                    self.scene.addItem(imageWidget)
                    imageWidget.addImage(QPixmap(), 0, 0, 0, antialiasing)
                    imageWidget.representNoImage()
                    
                imageWidget.objectDeleted = lambda name, self=self: self.onObjectDeleted(name, imageWidget)
                imageWidget.objectLayerAction = lambda name, action: self.objectLayerChange.emit(name, action)

            elif i["@Shape"] == "32":
                # Split images from the Bitmaplist
                imageList = i["@BitmapList"].split("|")
                imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self, QColor(255,255,255,100), i["@Name"], imageFolder)
                imageWidget.setZValue(index)

                if len(imageList) != 11:
                    imageWidget.representNoImage()
                else:
                    imageWidget.loadNumbers(i["@Digits"], i["@Spacing"], imageList, antialiasing)
                    
                name = i["@Name"]
                self.scene.addItem(imageWidget)
                imageWidget.objectDeleted = lambda name, self=self: self.onObjectDeleted(name, imageWidget)
                imageWidget.objectLayerAction = lambda name, action: self.objectLayerChange.emit(name, action)

            elif i["@Shape"] == "42":
                bgImage = QPixmap()
                bgImage.load(os.path.join(imageFolder, i["@Background_ImageName"]))
            
                fgImage = QPixmap()
                fgImage.load(os.path.join(imageFolder, i["@Foreground_ImageName"]))
                
                progressWidget = ProgressWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), self, QColor(255,255,255,0), i["@Name"], i["@Rotate_xc"], i["@Rotate_yc"], i["@Radius"], i["@Line_Width"], i["@StartAngle"], i["@EndAngle"], bgImage, fgImage, antialiasing)
                progressWidget.setZValue(index)
                name = i["@Name"]
                self.scene.addItem(progressWidget)
                progressWidget.objectDeleted = lambda name, self=self: self.onObjectDeleted(name, progressWidget)
                progressWidget.objectLayerAction = lambda name, action: self.objectLayerChange.emit(name, action)

            else:
                return False, f"Widget {i['@Shape']} not implemented in canvas, please report as issue."
            
            return True, "Success"
        except Exception as e:
            QMessageBox().critical(None, "Error", f"Unable to create object {i['@Name']}: {traceback.format_exc()}")
            return False, str(e)

    def loadObjects(self, data, imageFolder, antialiasing):
        if data["FaceProject"]["Screen"].get("Widget") != None:
            self.scene.clear()
            self.drawDecorations(self.deviceOutlineVisible)

            widgets = data["FaceProject"]["Screen"]["Widget"]
            if type(widgets) == list:
                for index, i in enumerate(widgets):     
                    result, reason = self.createObject(index, i, imageFolder, antialiasing)
                    if not result:
                        return False, reason 
                return True, "Success"
            else:
                result, reason = self.createObject(0, widgets, imageFolder, antialiasing)
                if not result:
                    return False, reason 
                else:
                    return True, "Success"
        else:
            return True, "Success"
        
    def reloadObject(self, objectName, objectData, imageFolder, antialiasing):
        object = None
        objectZValue = None

        for x in self.items():
            # data(0) is name
            if x.data(0) == objectName:
                object = x
                objectZValue = object.zValue()
                break

        if object != None:
            object.scene().removeItem(object)
            result, reason = self.createObject(objectZValue, objectData, imageFolder, antialiasing)
            if not result:
                return False, reason 
            else:
                return True, "Success"
                
        
class Widget(QGraphicsRectItem):
    # Basic widget with only bounding box and movement
    # All other widgets inherit this widget except ResizeableWidget

    def __init__(self, posX, posY, sizeX, sizeY, canvas, color, name):
        # Initialize the shape.
        super().__init__(posX, posY, sizeX, sizeY)
        self.setRect(0, 0, sizeX, sizeY)
        self.color = color
        self.canvas = canvas
        self.setAcceptHoverEvents(True)
        self.setData(0, name)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)

    def contextMenuEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        view = self.scene().views()[0]  # Get the first view
        viewPos = view.mapToGlobal(view.mapFromScene(scenePos))

        menu = QMenu()
        raiseIcon = QIcon()
        raiseIcon.addFile(u":/Dark/bring-to-front.png", QSize(), QIcon.Normal, QIcon.Off)
        raiseToTopAction = menu.addAction("Bring to Front")
        raiseToTopAction.setIcon(raiseIcon)
        raiseAction = menu.addAction("Bring Forwards")
        lowerIcon = QIcon()
        lowerIcon.addFile(u":/Dark/send-to-back.png", QSize(), QIcon.Normal, QIcon.Off)
        lowerToBottomAction = menu.addAction("Send to Back")
        lowerToBottomAction.setIcon(lowerIcon)
        lowerAction = menu.addAction("Send Backwards")
        menu.addSeparator()
        deleteIcon = QIcon()
        deleteIcon.addFile(u":/Dark/x_dim.png", QSize(), QIcon.Normal, QIcon.Off)
        action1 = menu.addAction("Delete")
        action1.setIcon(deleteIcon)

        action = menu.exec(viewPos)

        if action == action1:
            self.objectDeleted(self.data(0))
        elif action == raiseToTopAction:
            self.objectLayerAction(self.data(0), "top")
        elif action == raiseAction:
            self.objectLayerAction(self.data(0), "raise")
        elif action == lowerToBottomAction:
            self.objectLayerAction(self.data(0), "bottom")
        elif action == lowerAction:
            self.objectLayerAction(self.data(0), "lower")
        

    def objectDeleted(self, name):
        pass

    def objectLayerAction(self, name, action):
        pass

    def boundingRect(self):
        # Ensure the bounding rectangle accounts for any changes that affect the item's appearance
        outline_width = 2.0  # Adjust this value as needed
        return self.rect().adjusted(-outline_width, -outline_width, outline_width, outline_width)
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.canvas.fireObjectPositionChanged(self.data(0), self.pos().x(), self.pos().y())

    def paint(self, painter, option, widget=None):
        # Paint the node in the graphic view.

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))

        if self.isSelected():
            outline_width = 2.0  # Adjust this value as needed
            painter.setPen(QPen(QColor(0, 205, 255), outline_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(QColor(0, 0, 0, 0), 0, Qt.SolidLine))

        painter.drawRect(self.rect())

class ResizeableWidget(QGraphicsRectItem):
    # Widget with resizing properties

    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, posX, posY, sizeX, sizeY, color, name):
        """
        Initialize the shape.
        """
        super().__init__(posX, posY, sizeX, sizeY)
        self.color = color
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setData(0, name)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()
        self.setZValue(9999)

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handleAt(moveEvent.pos())
            cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect()
        
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def contextMenuEvent(self, event):

        scenePos = self.mapToScene(event.pos())
        view = self.scene().views()[0]  # Get the first view
        viewPos = view.mapToGlobal(view.mapFromScene(scenePos))
        
        menu = QMenu()
        deleteIcon = QIcon()
        deleteIcon.addFile(u":/Dark/x_dim.png", QSize(), QIcon.Normal, QIcon.Off)
        action1 = menu.addAction("Delete")
        action1.setIcon(deleteIcon)
        
        action = menu.exec(viewPos)
        
        if action == action1:
            self.scene().removeItem(self)

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

        for handle, rect in self.handles.items():
            rect_item = QGraphicsRectItem(rect)
            rect_item.setZValue(1000)  

    def interactiveResize(self, mousePos):
        # Perform shape interactive resize.

        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            if rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:

            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            #print("MR")
            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:

            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            if rect.width() > 0 and rect.height() > 0:
                self.setRect(rect)
                
        self.updateHandlesPos()

    def objectDeleted(self, name):
        pass

    def shape(self):
        # Returns the shape of this item as a QPainterPath in local coordinates.

        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        # Paint the node in the graphic view.

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor(0, 205, 255), 0, Qt.SolidLine))

        if self.isSelected():
            painter.setPen(QPen(QColor(0, 205, 255), 2.0, Qt.SolidLine))

        if not self.isSelected():
            painter.setPen(QPen(QColor(0, 0, 0, 0), 0, Qt.SolidLine))

        painter.drawRect(self.rect())

        if self.isSelected():
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            for handle, rect in self.handles.items():
                if self.handleSelected is None or handle == self.handleSelected:
                    painter.drawRect(rect)


class RectangleWidget(ResizeableWidget):
    def __init__(self, posX, posY, sizeX, sizeY, color, name):
        super().__init__(posX, posY, sizeX, sizeY, color, name)


class ImageWidget(Widget):
    # Widget for basic images and handling for DigitalNumber
    # All ImageList related things are handled in the createObject function
    # Live previews of animations are planned with this widget

    def __init__(self, posX, posY, sizeX, sizeY, canvas, color, name, srcDir):
        super().__init__(posX, posY, sizeX, sizeY, canvas, color, name)
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
            item.setTransformationMode(Qt.SmoothTransformation)
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

class AnalogWidget(Widget):
    # Widget for handling AnalogDisplays
    
    def __init__(self, posX, posY, sizeX, sizeY, canvas, color, name):
        super().__init__(posX, posY, sizeX, sizeY, canvas, color, name)
        self.setPos(posX, posY)

    def addBackground(self, backgroundImage, bgX, bgY, antialiasing):
        if backgroundImage != "":
            self.background = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage.setPos(int(bgX), int(bgY))
        if antialiasing:
            self.bgImage.setTransformationMode(Qt.SmoothTransformation)

    def addSecondHand(self, secHandImage, secHandX, secHandY, antialiasing):
        if secHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
            self.setRect(0,0,100,100)
        self.secHand = QGraphicsPixmapItem(secHandImage, self)
        self.secHand.setOffset(-int(secHandX), -int(secHandY))
        self.secHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.secHand.setTransformationMode(Qt.SmoothTransformation)

    def addMinuteHand(self, minHandImage, minHandX, minHandY, antialiasing):
        if minHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
            self.setRect(0,0,100,100)
        self.minHand = QGraphicsPixmapItem(minHandImage, self)
        self.minHand.setOffset(-int(minHandX), -int(minHandY))
        self.minHand.setRotation(60)
        self.minHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.minHand.setTransformationMode(Qt.SmoothTransformation)

    def addHourHand(self, hourHandImage, hrHandX, hrHandY, antialiasing):
        if hourHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
            self.setRect(0,0,100,100)
        self.hrHand = QGraphicsPixmapItem(hourHandImage, self)
        self.hrHand.setOffset(-int(hrHandX), -int(hrHandY))
        self.hrHand.setRotation(-60)
        self.hrHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.hrHand.setTransformationMode(Qt.SmoothTransformation)


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
        painter.setRenderHint(QPainter.Antialiasing, self.antialiased)
        brush = QBrush(self.pixmap())
        pen = QPen(QColor(255,255,255,255))
        pen.setStyle(Qt.DashLine)
        painter.setBrush(brush)
        painter.setPen(pen)

        diameter = 2 * self.radius
        arc_rect = QRectF(self.posX - self.radius - (self.thickness / 2), self.posY - self.radius - (self.thickness / 2), diameter + self.thickness, diameter + self.thickness)
        
        # Draw using image brush. Its very bad to use, will implement soon
        painter.drawPath(CircularArcItem(arc_rect, self.startAngle, self.endAngle, self.pixmap().width(), self.thickness).createArcPath())

class ProgressWidget(Widget):
    def __init__(self, posX, posY, sizeX, sizeY, canvas, color, name, offsetX, offsetY, radius, thickness, startAngle, endAngle, bgImage, pathImage, isAntialiased):
        super().__init__(posX, posY, sizeX, sizeY, canvas, color, name)
        self.setPos(posX, posY)
        self.setRect(0, 0, bgImage.width(), bgImage.height())

        radius = int(radius)
        thickness = int(thickness)
        startAngle = int(startAngle)
        endAngle = int(endAngle)

        self.backgroundImage = QGraphicsPixmapItem(bgImage, self)

        self.pathImage = CirclularArcImage(pathImage, self, offsetX, offsetY, radius, thickness, startAngle, endAngle, isAntialiased)

        if isAntialiased:
            self.backgroundImage.setTransformationMode(Qt.SmoothTransformation)
            self.pathImage.setTransformationMode(Qt.SmoothTransformation)