import sys

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame
from PyQt6.QtGui import QContextMenuEvent, QIcon
from PyQt6.QtCore import Qt, QSize

class Explorer(QTreeWidget):
    def __init__(self, parent, objectIcon, ui):
        super().__init__(parent)
        self.items = {}
        self.objectIcon = objectIcon
        self.mainWindowUI = ui
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.clear()

    def updateExplorer(self, project):
        self.clear()
        self.items = {}
        def createItem(item):
            if not self.objectIcon.icon.get(item["@Shape"]):
                #self.showDialogue("error", f"Widget {item['@Shape']} not implemented in self.objectIcon, please report as issue.")
                return
            object = QTreeWidgetItem(root)
            object.setText(0, item["@Name"])
            object.setIcon(0, QIcon.fromTheme(self.objectIcon.icon[item["@Shape"]]))
            object.setFlags(object.flags() | Qt.ItemFlag.ItemIsEditable)
            object.setData(0, 100, item["@Shape"])
            object.setData(0, 101, item["@Name"])
            self.items[item["@Name"]] = object
        
        icon = QIcon()
        icon.addFile(u":/Dark/watch.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
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