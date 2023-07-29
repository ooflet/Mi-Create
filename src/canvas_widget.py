from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class BaseItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.SizeAllCursor)
        self.resizeHandles = []

    def createResizeHandles(self):
        handles_size = 6
        handles = [
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1)
        ]

        for handle in handles:
            x = self.rect().width() * handle[0] - handles_size / 2
            y = self.rect().height() * handle[1] - handles_size / 2

            resize_handle = self.scene().addEllipse(x, y, handles_size, handles_size, QPen(), QBrush(Qt.black))
            resize_handle.setFlag(QGraphicsRectItem.ItemIsMovable, False)
            resize_handle.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
            resize_handle.setCursor(Qt.SizeFDiagCursor)
            self.resizeHandles.append(resize_handle)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange:
            for handle in self.resizeHandles:
                handle.setPos(handle.pos() + value - self.pos())
        return super().itemChange(change, value)
    
class Canvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            data = event.mimeData()
            model_data = data.data('application/x-qabstractitemmodeldatalist')
            ba = QByteArray(model_data)
            stream = QDataStream(ba)
            scene = self.scene()
            while not stream.atEnd():
                row = stream.readInt32()
                col = stream.readInt32()
                item_data = stream.readInt32()  # Assuming item_data is an integer representing the position
                rect = BaseItem(0,0,50,50)
                scene.addItem(rect)  # Add the item to the QGraphicsScene
            event.acceptProposedAction()

