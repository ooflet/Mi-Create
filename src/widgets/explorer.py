# Explorer Widget for Mi Create
# ooflet <ooflet@proton.me>

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame, QMessageBox
from PyQt6.QtGui import QContextMenuEvent, QIcon, QStandardItemModel
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QModelIndex, QPoint

from utils.contextMenu import ContextMenu

class Explorer(QTreeWidget):
    itemReordered = pyqtSignal(str, int)
    def __init__(self, parent, objectIcon, ui):
        super().__init__(parent)
        self.items = {}
        self.objectIcon = objectIcon
        self.mainWindowUI = ui
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setFrameShape(QFrame.Shape.NoFrame)
        #self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.clear()

        self.customContextMenuRequested.connect(self.contextMenuEvent)

    def dragMoveEvent(self, event):
        self.setDropIndicatorShown(True)
        super(QTreeWidget, self).dragMoveEvent(event)
        if self.dropIndicatorPosition() == self.DropIndicatorPosition.OnItem or self.dropIndicatorPosition() == self.DropIndicatorPosition.OnViewport:
            self.setDropIndicatorShown(False)
            event.ignore()

    def dropEvent(self, event):
        model = QStandardItemModel()
        model.dropMimeData(event.mimeData(), Qt.DropAction.CopyAction, 0, 0, QModelIndex())

        if model.item(0, 0).data(101) in self.items:
            print(model.item(0, 0).data(101))
            dropIndex = self.indexAt(event.position().toPoint())
            self.itemReordered.emit(model.item(0, 0).data(101), dropIndex)

    def contextMenuEvent(self, pos):
        if len(self.selectedItems()) > 0:
            pos = self.mapToGlobal(pos)
            menu = ContextMenu("shape", self.mainWindowUI)
            menu.exec(pos)

    def updateExplorer(self, project):
        self.clear()
        self.items = {}
        def createItem(item):
            if not self.objectIcon.icon.get(item.getProperty("widget_type")):
                #self.showDialogue("error", f"Widget {item['@Shape']} not implemented in self.objectIcon, please report as issue.")
                return
            object = QTreeWidgetItem(root)
            object.setText(0, item.getProperty("widget_name"))
            object.setSizeHint(0, QSize(18, 18))
            object.setIcon(0, QIcon.fromTheme(self.objectIcon.icon[item.getProperty("widget_type")]))
            object.setFlags(object.flags() | Qt.ItemFlag.ItemIsEditable)
            object.setData(0, 100, item.getProperty("widget_type"))
            object.setData(0, 101, item.getProperty("widget_name"))
            self.items[item.getProperty("widget_name")] = object
        
        icon = QIcon().fromTheme("device-watch")
        name = None
        if project.getTitle() == "":
            name = "Watchface"
        else:
            name = project.getTitle()
        root = QTreeWidgetItem(self)
        root.setText(0, name)
        root.setIcon(0, icon)
        root.setData(0, 100, "00")
        root.setFlags(root.flags() | Qt.ItemFlag.ItemIsEditable)
        if project.getAllWidgets() != None:
            for x in project.getAllWidgets():
                createItem(x) 
            
        self.expandAll()