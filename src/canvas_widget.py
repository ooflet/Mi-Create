from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class Canvas(QGraphicsView):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setScene(None)
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
                while not stream.atEnd():
                    row = stream.readInt32()
                    col = stream.readInt32()
                    item_data = stream.readQVariant()
                    item = QTreeWidgetItem()
                    item.setData(0, Qt.DisplayRole, item_data)
                    self.addTopLevelItem(item)
                event.acceptProposedAction()