# Canvas for Mi Create
# tostr 2023

# Responsible for rendering EasyFace XML projects via QGraphicsView library.

import os
import sys
import base64
import json
from typing import Any

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "27":":Dark/analog.png",
            "30":":Dark/image.png",
            "31":":Dark/gallery-horizontal.png",
            "32":":Dark/numbers.png"
        }

class DeviceSize:
    def __init__(self):
        super().__init__()
        # Sizing goes [x, y, corner_radius]
        self.device = {
            "0":[454, 454, 400],
            "1":[454, 454, 400],
            "3":[466, 466, 450],
            "4":[480, 480, 450],
            "5":[360, 320, 300],
            "6":[280, 456, 150],
            "7":[390, 450, 100],
            "8":[194, 368, 200],
            "9":[192, 490, 95],
            "10":[240, 280, 60],
            "11":[336, 480, 100]
        }

class DeviceOutline(QGraphicsPathItem):
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
    onObjectDeleted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def selectionChanged(self):
        super().selectionChanged()
        self.itemSelectionChanged.emit()

    def objectDeleted(self, name):
        self.onObjectDeleted.emit(name)

class Canvas(QGraphicsView):
    objectAdded = Signal(QPointF, str)
    objectChanged = Signal(str, tuple)
    def __init__(self, device, antialiasingEnabled, deviceOutlineVisible, insertMenu, parent=None):
        super().__init__(parent)

        if antialiasingEnabled:
            self.setRenderHints(QPainter.Antialiasing)

        self.insertMenu = insertMenu
        self.deviceOutlineVisible = deviceOutlineVisible
        self.rubberBand = None
        self.origin = None
        self.setAcceptDrops(True)

        self.zoomValue = 0

        self.deviceSize = DeviceSize().device[str(device)]

        self.scene = Scene()
        self.scene.setSceneRect(0,0,self.deviceSize[0],self.deviceSize[1])

        self.drawDecorations(deviceOutlineVisible)

        self.setScene(self.scene)

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

    def handleObjectSelectionChange(self):
        selected_object = self.getSelectedObject()
        if selected_object:
            print(f"Object '{selected_object}' selected")

    def selectObject(self, name):
        for x in self.items():
            # data(0) is name
            if x.data(0) == name:
                print("set selected")
                x.setSelected(True)
            else:
                x.setSelected(False)

    def getSelectedObject(self):
        return self.scene.selectedItems()
    
    def setObjectProperty(self, name, property, value, data=""):
        for x in self.items():
            if x.data(0) == name:
                x.setProperty(property, value, data)

    def loadObjectsFromData(self, data, imageData, antialiasing, selectObject=""):
        # Data is the json dump of the "data" section of the file
        #print(data)
        if not data["FaceProject"]["Screen"].get("Widget") == None:
            self.scene.clear()
            self.drawDecorations(self.deviceOutlineVisible)

            for index, i in enumerate(data["FaceProject"]["Screen"]["Widget"]):
                match i["@Shape"]:
                    case "27":
                        # Seconds Image
                        secImgRaw = imageData[i["@SecondHand_Image"]]
                        secImgDecode = base64.b64decode(secImgRaw)
                        secImgArray = QByteArray(secImgDecode)
                        secImg = QPixmap()
                        secImg.loadFromData(secImgArray)

                        minImgRaw = imageData[i["@MinuteHand_Image"]]
                        minImgDecode = base64.b64decode(minImgRaw)
                        minImgArray = QByteArray(minImgDecode)
                        minImg = QPixmap()
                        minImg.loadFromData(minImgArray)

                        hrImgRaw = imageData[i["@HourHand_ImageName"]]
                        hrImgDecode = base64.b64decode(hrImgRaw)
                        hrImgArray = QByteArray(hrImgDecode)
                        hrImg = QPixmap()
                        hrImg.loadFromData(hrImgArray)

                        # Create analogwidget
                        imageWidget = AnalogWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0), i["@Name"], antialiasing, self.sceneRect().width(), self.sceneRect().height(), i["@Background_ImageName"], secImg, i["@SecondImage_rotate_xc"], i["@SecondImage_rotate_yc"], minImg, i["@MinuteImage_rotate_xc"], i["@MinuteImage_rotate_yc"], hrImg, i["@HourImage_rotate_xc"], i["@HourImage_rotate_yc"])
                        imageWidget.setZValue(index)
                        self.scene.addItem(imageWidget)

                    case "30":
                        path = i["@Bitmap"].split("/")
                        if path[0] == "resource":
                            if getattr(sys, 'frozen', False):
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                imgPath = os.path.join(script_dir, 'resource_packs')
                                imgFile = os.path.join(imgPath, f"{path[1]}.mres")
                                with open(imgFile, 'r') as file:
                                    imgData = json.loads(file.read())
                                    i["@Bitmap"] = path[2]
                                    imageData[path[2]] = imgData[path[2]]
                                    
                            else:
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                data_dir = os.path.join(script_dir, '..', 'data')
                                imgPath = os.path.join(data_dir, "resource_packs")
                                imgFile = os.path.join(imgPath, f"{path[1]}.mres")
                                with open(imgFile, 'r') as file:
                                    imgData = json.loads(file.read())
                                    i["@Bitmap"] = path[2]
                                    imageData[path[2]] = imgData[path[2]]
                                    
                        imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0), i["@Name"])
                        imageWidget.setZValue(index)

                        # Convert base64 image to QPixmap
                        if imageData.get(i["@Bitmap"]):
                            base64Data = imageData[i["@Bitmap"]]
                            decoded = base64.b64decode(base64Data)
                            qByteArray = QByteArray(decoded)
                            image = QPixmap()
                            image.loadFromData(qByteArray)

                            # Create imagewidget    
                            imageWidget.addImage(i["@Bitmap"], image, 0, 0, 1, antialiasing)  
                        else:
                            imageWidget.representNoImage()

                        self.scene.addItem(imageWidget)

                    case "31":
                        # Split image strings from the Bitmaplist
                        imageList = i["@BitmapList"].split("|")
                        firstImage = imageList[0].split(":")
                        
                        for x in firstImage:
                            index = firstImage.index(x)+1
                            if (index % 2) == 0:
                                path = x.split("/")
                                if path[0] == "resource":
                                    if getattr(sys, 'frozen', False):
                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        imgPath = os.path.join(script_dir, 'resource_packs')
                                        imgFile = os.path.join(imgPath, f"{path[1]}.mres")
                                        with open(imgFile, 'r') as file:
                                            imgData = json.loads(file.read())
                                            firstImage[firstImage.index(x)] = path[2]
                                            imageData[path[2]] = imgData[path[2]]
                                            
                                    else:
                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        data_dir = os.path.join(script_dir, '..', 'data')
                                        imgPath = os.path.join(data_dir, "resource_packs")
                                        imgFile = os.path.join(imgPath, f"{path[1]}.mres")
                                        with open(imgFile, 'r') as file:
                                            imgData = json.loads(file.read())
                                            firstImage[firstImage.index(x)] = path[2]
                                            imageData[path[2]] = imgData[path[2]]
                                            
                        # Convert base64 image to QPixmap
                        base64Data = imageData[firstImage[1]]
                        decoded = base64.b64decode(base64Data)
                        qByteArray = QByteArray(decoded)
                        image = QPixmap()
                        image.loadFromData(qByteArray)

                        # Create imagewidget
                        imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0), i["@Name"])
                        imageWidget.setZValue(index)
                        imageWidget.addImage(firstImage[1], image, 0, 0, 1, antialiasing)
                        self.scene.addItem(imageWidget)

                    case "32":
                        # Split images from the Bitmaplist
                        imageList = i["@BitmapList"].split("|")
                        if imageList[0] == "fontresource":
                            if getattr(sys, 'frozen', False):
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                fontPath = os.path.join(script_dir, 'custom_fonts')
                                fontFile = os.path.join(fontPath, f"{imageList[1]}.mfnt")
                                with open(fontFile, 'r') as file:
                                    fontData = json.loads(file.read())
                                    imageList = fontData["data"].split("|")
                                    for key, value in fontData["imgdata"].items():
                                        imageData[key] = value
                            else:
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                data_dir = os.path.join(script_dir, '..', 'data')
                                fontPath = os.path.join(data_dir, "custom_fonts")
                                fontFile = os.path.join(fontPath, f"{imageList[1]}.mfnt")
                                with open(fontFile, 'r') as file:
                                    fontData = json.loads(file.read())
                                    imageList = fontData["data"].split("|")
                                    for key, value in fontData["imgdata"].items():
                                        imageData[key] = value
                        
                        imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0), i["@Name"])
                        imageWidget.setZValue(index)

                        # Loop through digits
                        for x in range(int(i["@Digits"])):
                            # Convert base64 image to QPixmap
                            base64Data = imageData[imageList[x]]
                            decoded = base64.b64decode(base64Data)
                            qByteArray = QByteArray(decoded)
                            image = QPixmap()
                            image.loadFromData(qByteArray)

                            # Create imagewidget
                            imageWidget.addImage(imageList[x], image, image.size().width()*x, 0, int(i["@Digits"]), antialiasing)
                            
                        self.scene.addItem(imageWidget)
                    case _:
                        return False
            self.selectObject(selectObject)
            return True
        else:
            return True

class ResizeableObject(QGraphicsRectItem):
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

class BaseObject(QGraphicsRectItem):
    def __init__(self, posX, posY, sizeX, sizeY, color, name):
        # Initialize the shape.
        super().__init__(posX, posY, sizeX, sizeY)
        self.color = color
        self.setAcceptHoverEvents(True)
        self.setData(0, name)
        self.setData(0, name)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

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

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            # Force a repaint of the entire item when the selection state changes
            self.update()
        return super().itemChange(change, value)

    def boundingRect(self):
        # Ensure the bounding rectangle accounts for any changes that affect the item's appearance
        outline_width = 2.0  # Adjust this value as needed
        return self.rect().adjusted(-outline_width, -outline_width, outline_width, outline_width)

    def paint(self, painter, option, widget=None):
        # Paint the node in the graphic view.

        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setBrush(QBrush(self.color))

        if self.isSelected():
            outline_width = 2.0  # Adjust this value as needed
            painter.setPen(QPen(QColor(0, 205, 255), outline_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(QColor(0, 0, 0, 0), 0, Qt.SolidLine))

        painter.drawRect(self.rect())

class RectangleWidget(ResizeableObject):
    objectMovementStopped = Signal(int, int)
    def __init__(self, posX, posY, sizeX, sizeY, color, name):
        super().__init__(posX, posY, sizeX, sizeY, color, name)


class ImageWidget(BaseObject):
    objectMovementStopped = Signal(int, int)
    def __init__(self, posX, posY, sizeX, sizeY, color, name):
        super().__init__(posX, posY, sizeX, sizeY, color, name)
        self.imageItems = {}
        self.setPos(posX, posY)

    def mouseReleaseEvent(self, mouseEvent):
        super().mouseReleaseEvent(mouseEvent)
        self.objectMovementStopped.emi
        self.objectMovementStopped.emit(self.pos().x(), self.pos().y())

    def addImage(self, name, qPixmap, posX, posY, digits, isAntialiased):
        self.digits = digits
        self.imageItems[name] = QGraphicsPixmapItem(qPixmap, self)
        self.imageItems[name].setPos(posX, posY)
        if isAntialiased:
            self.imageItems[name].setTransformationMode(Qt.SmoothTransformation)
        self.setRect(0, 0, qPixmap.width()*digits, qPixmap.height())

    def representNoImage(self):
        self.setRect(0, 0, 100, 100)
        brush = QBrush()
        brush.setColor(QColor(42, 130, 218, 255))
        brush.setStyle(Qt.BDiagPattern)
        self.setBrush(brush)

    def setProperty(self, property, value, imageData):
        match property:
            case "@Bitmap":
                path = value.split("/")
                if path[0] == "resource":
                    if getattr(sys, 'frozen', False):
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        imgPath = os.path.join(script_dir, 'resource_packs')
                        imgFile = os.path.join(imgPath, f"{path[1]}.mres")
                        with open(imgFile, 'r') as file:
                            imgData = json.loads(file.read())
                            value = path[2]
                            imageData[path[2]] = imgData[path[2]]
                            
                    else:
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        data_dir = os.path.join(script_dir, '..', 'data')
                        imgPath = os.path.join(data_dir, "resource_packs")
                        imgFile = os.path.join(imgPath, f"{path[1]}.mres")
                        with open(imgFile, 'r') as file:
                            imgData = json.loads(file.read())
                            value = path[2]
                            imageData[path[2]] = imgData[path[2]]

                # Convert base64 image to QPixmap
                base64Data = imageData[value]
                decoded = base64.b64decode(base64Data)
                qByteArray = QByteArray(decoded)
                image = QPixmap()
                image.loadFromData(qByteArray)
                self.imageItem.setPixmap(image)
                self.imageItem.setPos(0, 0)
                self.setRect(0, 0, image.width(), image.height())
            
            case "@Digits":
                imageList = value.split("|")
                if imageList[0] == "fontresource":
                    if getattr(sys, 'frozen', False):
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        fontPath = os.path.join(script_dir, 'custom_fonts')
                        fontFile = os.path.join(fontPath, f"{imageList[1]}.mfnt")
                        with open(fontFile, 'r') as file:
                            fontData = json.loads(file.read())
                            imageList = fontData["data"].split("|")
                            for key, val in fontData["imgdata"].items():
                                imageData[key] = val
                    else:
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        data_dir = os.path.join(script_dir, '..', 'data')
                        fontPath = os.path.join(data_dir, "custom_fonts")
                        fontFile = os.path.join(fontPath, f"{imageList[1]}.mfnt")
                        with open(fontFile, 'r') as file:
                            fontData = json.loads(file.read())
                            imageList = fontData["data"].split("|")
                            for key, val in fontData["imgdata"].items():
                                imageData[key] = val
                
                imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0), i["@Name"])
                imageWidget.setZValue(index)

                # Loop through digits
                for x in range(int(i["@Digits"])):
                    # Convert base64 image to QPixmap
                    base64Data = imageData[imageList[x]]
                    decoded = base64.b64decode(base64Data)
                    qByteArray = QByteArray(decoded)
                    image = QPixmap()
                    image.loadFromData(qByteArray)

                    # Create imagewidget
                    imageWidget.addImage(image, image.size().width()*x, 0, int(i["@Digits"]))
            case "@X":
                self.setX(int(value))
            case "@Y":
                self.setY(int(value))
            case "@Alignment":
                pass
            case "@Alpha":
                self.imageItem.setOpacity(1-value/255)

class AnalogWidget(BaseObject):
    # hands pos X & Y are relative to anchor point 0,0 on the image
    # secHand, minHand & hrHand are QPixmaps, do not send raw data otherwise I will explode!!!!!!!
    def __init__(self, posX, posY, sizeX, sizeY, color, name, isAntialiased, screenSizeX, screenSizeY, background, secHand, secHandX, secHandY, minHand, minHandX, minHandY, hrHand, hrHandX, hrHandY):
        super().__init__(posX, posY, sizeX, sizeY, color, name)
        self.setPos(posX, posY)
        if not background == "":
            self.background = QGraphicsPixmapItem(background, self)
        self.hrHand = QGraphicsPixmapItem(hrHand, self)
        self.hrHand.setOffset(-int(hrHandX), -int(hrHandY))
        self.hrHand.setRotation(-60)
        self.hrHand.setPos(screenSizeX/2, screenSizeY/2)
        self.minHand = QGraphicsPixmapItem(minHand, self)
        self.minHand.setOffset(-int(minHandX), -int(minHandY))
        self.minHand.setRotation(60)
        self.minHand.setPos(screenSizeX/2, screenSizeY/2)
        self.secHand = QGraphicsPixmapItem(secHand, self)
        self.secHand.setOffset(-int(secHandX), -int(secHandY))
        self.secHand.setPos(screenSizeX/2, screenSizeY/2)
        if isAntialiased:
            self.hrHand.setTransformationMode(Qt.SmoothTransformation)
            self.minHand.setTransformationMode(Qt.SmoothTransformation)
            self.secHand.setTransformationMode(Qt.SmoothTransformation)
