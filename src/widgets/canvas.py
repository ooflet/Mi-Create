# Watchface Renderer for Mi Face Studio
# tostr 2023

# Responsible for rendering EasyFace XML projects via QGraphicsView library.

import sys
import base64

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
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
            "7":[450, 390, 250],
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
        self.setZValue(999)

class Scene(QGraphicsScene):
    itemSelectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def selectionChanged(self):
        super().selectionChanged()
        self.itemSelectionChanged.emit()

class Canvas(QGraphicsView):
    def __init__(self, device, antialiasingEnabled, deviceOutlineVisible, parent=None):
        super().__init__(parent)
        if antialiasingEnabled:
            self.setRenderHint(QPainter.Antialiasing)

        self.rubberBand = None
        self.origin = None
        self.setAcceptDrops(True)

        self.zoomValue = 0

        deviceSize = DeviceSize().device[str(device)]

        self.scene = Scene()
        self.scene.setSceneRect(0,0,deviceSize[0],deviceSize[1])

        self.setScene(self.scene)

        background = QGraphicsRectItem(0, 0, deviceSize[0], deviceSize[1])
        background.setPen(QPen(Qt.NoPen))
        background.setBrush(QColor(0, 0, 0, 255))
        
        self.scene.addItem(background)

        if deviceOutlineVisible:
            self.scene.addItem(DeviceOutline(deviceSize))

    def dragEnterEvent(self, event):
        print("enter")
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            print("accept")
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        print("move")
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            print("accept")
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("drop")
        print(event.mimeData().formats())
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            print("accept")
            data = event.mimeData()
            item_data = data.data('application/x-qgraphicsitemdata')
            print(item_data)

            # Use the item_data to retrieve the name or other relevant information
            item_name = item_data.decode('utf-8')  
            print("Dropped item name:", item_name)

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

    def selectObject(self, obj):
        if obj and isinstance(obj, BaseObject):
            obj.setSelected(True)

    def getSelectedObject(self):
        selected_items = self.scene.selectedItems()
        if selected_items:
            return selected_items[0]  # Return the first selected item if any
        else:
            return None

    def loadObjectsFromData(self, data, imageData, antialiasing):
        #print(data)
        if data["FaceProject"]["Screen"].get("Widget") != None:
            for i in data["FaceProject"]["Screen"]["Widget"]:
                match i["@Shape"]:
                    case "30":
                        # Convert base64 image to QPixmap
                        base64Data = imageData[i["@Bitmap"]]
                        decoded = base64.b64decode(base64Data)
                        qByteArray = QByteArray(decoded)
                        image = QPixmap()
                        image.loadFromData(qByteArray)

                        # Create imagewidget
                        item = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0))
                        item.addImage(image, 0, 0, 1, antialiasing)
                        self.scene.addItem(item)

                    case "31":
                        # Split image strings from the Bitmaplist
                        imageList = i["@BitmapList"].split("|")
                        firstImage = imageList[0].split(":")

                        # Convert base64 image to QPixmap
                        base64Data = imageData[firstImage[1]]
                        decoded = base64.b64decode(base64Data)
                        qByteArray = QByteArray(decoded)
                        image = QPixmap()
                        image.loadFromData(qByteArray)

                        # Create imagewidget
                        imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0))
                        imageWidget.addImage(image, 0, 0, 1, antialiasing)
                        self.scene.addItem(imageWidget)

                    case "32":
                        # Split images from the Bitmaplist
                        imageList = i["@BitmapList"].split("|")
                        imageWidget = ImageWidget(int(i["@X"]), int(i["@Y"]), int(i["@Width"]), int(i["@Height"]), QColor(255,255,255,0))

                        # Loop through digits
                        for x in range(int(i["@Digits"])):
                            # Convert base64 image to QPixmap
                            base64Data = imageData[imageList[x]]
                            decoded = base64.b64decode(base64Data)
                            qByteArray = QByteArray(decoded)
                            image = QPixmap()
                            image.loadFromData(qByteArray)

                            # Create imagewidget
                            imageWidget.addImage(image, image.size().width()*x, 0, int(i["@Digits"]), antialiasing)
                            
                        self.scene.addItem(imageWidget)
                        
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

    def __init__(self, posX, posY, sizeX, sizeY, color):
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
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()

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

    def __init__(self, posX, posY, sizeX, sizeY, color):
        # Initialize the shape.

        super().__init__(posX, posY, sizeX, sizeY)
        self.color = color
        self.setAcceptHoverEvents(True)
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

class RectangleWidget(ResizeableObject):
    def __init__(self, posX, posY, sizeX, sizeY, color):
        super().__init__(posX, posY, sizeX, sizeY, color)


class ImageWidget(BaseObject):
    def __init__(self, posX, posY, sizeX, sizeY, color):
        super().__init__(posX, posY, sizeX, sizeY, color)
        self.setPos(posX, posY)

    def addImage(self, qPixmap, posX, posY, digits, isAntialiased):
        self.imageItem = QGraphicsPixmapItem(qPixmap, self)
        self.imageItem.setPos(posX, posY)

        if isAntialiased:
            self.imageItem.setTransformationMode(Qt.SmoothTransformation)

        self.setRect(0, 0, qPixmap.width()*digits, qPixmap.height())
        

def main():

    app = QApplication(sys.argv)

    grview = Canvas()
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)

    scene.addPixmap(QPixmap('01.png'))
    grview.setScene(scene)

    item = ImageWidget(0, 0, 300, 150, QColor(255, 255, 255, 255))
    scene.addItem(item)

    grview.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    grview.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()