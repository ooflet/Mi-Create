# Explorer Widget using QListWidget for Mi Create
# ooflet <ooflet@proton.me>

from PyQt6.QtWidgets import (QListWidget, QListWidgetItem, QWidget, QFrame, QHBoxLayout,
                             QLabel)
from PyQt6.QtGui import QContextMenuEvent, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from utils.translate import Translator
from utils.menu import ContextMenu
from widgets.items import ExplorerItem

class Explorer(QListWidget):
    itemReordered = pyqtSignal(int)
    itemHiddenToggled = pyqtSignal(str)
    itemLockedToggled = pyqtSignal(str)
    
    def __init__(self, parent, objectIcon, ui):
        super().__init__(parent)
        self.items = {}
        self.objectIcon = objectIcon
        self.mainWindowUI = ui

        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QListWidget.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setUniformItemSizes(True)

        self.customContextMenuRequested.connect(self.contextMenuEvent)

    def dropEvent(self, event):
        dropIndex = self.indexAt(event.position().toPoint()).row()
        self.itemReordered.emit(dropIndex)
        super().dropEvent(event)

    def contextMenuEvent(self, pos):
        if len(self.selectedItems()) > 0:
            globalPos = self.mapToGlobal(pos)
            menu = ContextMenu("shape", self.mainWindowUI)
            menu.exec(globalPos)

    def updateExplorer(self, project, canvas):
        self.clear()
        self.items = {}

        def createItem(item):
            widget_type = item.getProperty("widget_type")
            widget_name = item.getProperty("widget_name")
            if not self.objectIcon.icon.get(widget_type):
                return
            
            listItem = QListWidgetItem()

            listItem.setSizeHint(QSize(26, 26))
            listItem.setData(100, widget_type)
            listItem.setData(101, widget_name)

            icon = QIcon.fromTheme(self.objectIcon.icon[widget_type]).pixmap(18, 18)
            hidden = canvas.widgetSettings[item.project.currentTheme][widget_name]["hidden"]
            locked = canvas.widgetSettings[item.project.currentTheme][widget_name]["locked"]

            listItemWidget = ExplorerItem(widget_name, icon, hidden, locked)

            def visibleToggle(name):
                self.itemHiddenToggled.emit(name)
                if canvas.widgetSettings[item.project.currentTheme][widget_name]["hidden"]:
                    listItemWidget.visibleIcon.setIcon(QIcon.fromTheme("edit-hide"))
                    listItemWidget.hidden = True
                else:
                    listItemWidget.visibleIcon.setIcon(QIcon.fromTheme("edit-show"))
                    listItemWidget.hidden = False

            def lockedToggle(name):
                self.itemLockedToggled.emit(name)
                if canvas.widgetSettings[item.project.currentTheme][widget_name]["locked"]:
                    listItemWidget.lockIcon.setIcon(QIcon.fromTheme("edit-lock"))
                    listItemWidget.locked = True
                else:
                    listItemWidget.lockIcon.setIcon(QIcon.fromTheme("edit-unlock"))                
                    listItemWidget.locked = False

            listItemWidget.visibleIcon.clicked.connect(lambda args, name=widget_name: visibleToggle(name))
            listItemWidget.lockIcon.clicked.connect(lambda args, name=widget_name: lockedToggle(name))

            listItem.setSizeHint(listItemWidget.sizeHint())

            self.items[widget_name] = listItem
            self.addItem(listItem)
            self.setItemWidget(listItem, listItemWidget)

        widgets = project.getAllWidgets()
        if widgets:
            for x in widgets:
                createItem(x)
