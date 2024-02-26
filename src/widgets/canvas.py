# Canvas for Mi Create
# tostr 2023

# Responsible for rendering parsed EasyFace XML projects via QGraphicsView library.
# Parse an xml file to a dictionary, create a Canvas object and call loadObjectsFromData

import os
import sys
import traceback
import logging
from tracemalloc import start

sys.path.append("..")
from utils.project import watchData

from PyQt6.QtCore import pyqtSignal, QPointF, QModelIndex, QSize, QRectF, QRect, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QStandardItemModel, QPixmap, QIcon, QBrush, QImage
from PyQt6.QtWidgets import (QApplication, QGraphicsPathItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, 
                               QGraphicsEllipseItem, QMenu, QGraphicsPixmapItem, QMessageBox, QRubberBand)

class ObjectIcon:
    def __init__(self):
        super().__init__()
        self.icon = {
            "27":":Dark/analog.png",
            "30":":Dark/image.png",
            "31":":Dark/image-list.png",
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
        self.setPen(QPen(QColor(200, 200, 200, 100), thickness, Qt.PenStyle.SolidLine))
        self.setBrush(QColor(0,0,0,0))
        self.setZValue(9999)

class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

class Canvas(QGraphicsView):
    objectAdded = pyqtSignal(QPointF, str)
    objectChanged = pyqtSignal(str, str, object) # hate hacky workarounds, just support any type already Qt
    objectPosChanged = pyqtSignal()
    objectLayerChange = pyqtSignal(str, str)
    objectDeleted = pyqtSignal(str)

    def __init__(self, device, antialiasingEnabled, deviceOutlineVisible, insertMenu, parent=None):
        super().__init__(parent)

        if antialiasingEnabled:
            self.setRenderHints(QPainter.RenderHint.Antialiasing)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

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

    def fireObjectPositionChanged(self):
        self.objectPosChanged.emit()

    def drawDecorations(self, deviceOutlineVisible):
        background = QGraphicsRectItem(0, 0, self.deviceSize[0], self.deviceSize[1])
        background.setPen(QPen(Qt.PenStyle.NoPen))
        background.setBrush(QColor(0, 0, 0, 255))
        
        self.scene.addItem(background)

        if deviceOutlineVisible:
            self.scene.addItem(DeviceOutline(self.deviceSize))

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

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                zoom_factor = 1.25
                self.scale(zoom_factor, zoom_factor)
            elif event.key() == Qt.Key.Key_Minus:
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

    def selectObjects(self, objects):
        for name in objects:
            for x in self.items():
                # data(0) is name
                # text(0) is treewidgetitem text
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
                analogWidget.setData(1, "27")
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
                imageWidget.setData(1, "30")

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
                imageWidget.setData(1, "31")
                
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
                imageWidget.setData(1, "32")

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
                imageWidget.setData(1, "42")
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
                
        
class BaseWidget(QGraphicsRectItem):
    # Basic widget with draggable and selectable controls
    # Adding child QGraphicsItems to this widget extends functionality 

    def __init__(self, posX, posY, sizeX, sizeY, canvas, color, name):
        # Initialize the shape.
        super().__init__(posX, posY, sizeX, sizeY)
        self.setRect(0, 0, sizeX, sizeY)
        self.color = color
        self.canvas = canvas
        self.setAcceptHoverEvents(True)
        self.setData(0, name)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape, True)

    def contextMenuEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        view = self.scene().views()[0]  # Get the first view
        viewPos = view.mapToGlobal(view.mapFromScene(scenePos))

        menu = QMenu()
        raiseIcon = QIcon()
        raiseIcon.addFile(u":/Dark/bring-to-front.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        raiseToTopAction = menu.addAction("Bring to Front")
        raiseToTopAction.setIcon(raiseIcon)
        raiseAction = menu.addAction("Bring Forwards")
        lowerIcon = QIcon()
        lowerIcon.addFile(u":/Dark/send-to-back.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        lowerToBottomAction = menu.addAction("Send to Back")
        lowerToBottomAction.setIcon(lowerIcon)
        lowerAction = menu.addAction("Send Backwards")
        menu.addSeparator()
        deleteIcon = QIcon()
        deleteIcon.addFile(u":/Dark/x_dim.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        action1 = menu.addAction("Delete")
        action1.setIcon(deleteIcon)

        if not self.isSelected():
            self.setSelected(True)

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
        self.canvas.fireObjectPositionChanged()

    def paint(self, painter, option, widget=None):
        # Paint the node in the graphic view.

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))

        if self.isSelected():
            outline_width = 2.0  # Adjust this value as needed
            painter.setPen(QPen(QColor(0, 205, 255), outline_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        else:
            painter.setPen(QPen(QColor(0, 0, 0, 0), 0, Qt.PenStyle.SolidLine))

        painter.drawRect(self.rect())

class ImageWidget(BaseWidget):
    # Widget for basic images and handling for DigitalNumber
    # All ImageList related things are handled in the addImage function
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
    
    def __init__(self, posX, posY, sizeX, sizeY, canvas, color, name):
        super().__init__(posX, posY, sizeX, sizeY, canvas, color, name)
        self.setPos(posX, posY)

    def addBackground(self, backgroundImage, bgX, bgY, antialiasing):
        if backgroundImage != "":
            self.background = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage = QGraphicsPixmapItem(backgroundImage, self)
        self.bgImage.setPos(int(bgX), int(bgY))
        if antialiasing:
            self.bgImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addSecondHand(self, secHandImage, secHandX, secHandY, antialiasing):
        if secHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
            self.setRect(0,0,100,100)
        self.secHand = QGraphicsPixmapItem(secHandImage, self)
        self.secHand.setOffset(-int(secHandX), -int(secHandY))
        self.secHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.secHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addMinuteHand(self, minHandImage, minHandX, minHandY, antialiasing):
        if minHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
            self.setRect(0,0,100,100)
        self.minHand = QGraphicsPixmapItem(minHandImage, self)
        self.minHand.setOffset(-int(minHandX), -int(minHandY))
        self.minHand.setRotation(60)
        self.minHand.setPos(self.rect().width()/2, self.rect().height()/2)
        if antialiasing:
            self.minHand.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def addHourHand(self, hourHandImage, hrHandX, hrHandY, antialiasing):
        if hourHandImage.isNull():
            self.color = QColor(255, 0, 0, 100)
            self.setRect(0,0,100,100)
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
            self.backgroundImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self.pathImage.setTransformationMode(Qt.TransformationMode.SmoothTransformation)