from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize

class Explorer(QTreeWidget):
    def __init__(self, parent, objectIcon):
        super().__init__(parent)
        self.items = {}
        self.objectIcon = objectIcon
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.clear()

    def updateExplorer(self, data):
        def createItem(x):
            objectIcon = QIcon()
            if not self.objectIcon.icon.get(x["@Shape"]):
                self.showDialogue("error", f"Widget {x['@Shape']} not implemented in self.objectIcon, please report as issue.")
                return
            objectIcon.addFile(self.objectIcon.icon[x["@Shape"]], QSize(), QIcon.Mode.Normal, QIcon.State.Off)
            object = QTreeWidgetItem(root)
            object.setText(0, x["@Name"])
            object.setIcon(0, objectIcon)
            object.setFlags(object.flags() | Qt.ItemFlag.ItemIsEditable)
            object.setData(0, 100, x["@Shape"])
            object.setData(0, 101, x["@Name"])
            self.items[x["@Name"]] = object
        
        icon = QIcon()
        icon.addFile(u":/Dark/watch.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        name = None
        if data["FaceProject"]["Screen"]["@Title"] == "":
            name = "Watchface"
        else:
            name = data["FaceProject"]["Screen"]["@Title"]
        root = QTreeWidgetItem(self)
        root.setText(0, name)
        root.setIcon(0, icon)
        root.setData(0, 100, "00")
        root.setFlags(root.flags() | Qt.ItemFlag.ItemIsEditable)
        if data["FaceProject"]["Screen"].get("Widget") != None:
            if type(data["FaceProject"]["Screen"].get("Widget")) == list:
                for x in data["FaceProject"]["Screen"]["Widget"]:
                    createItem(x)      
            else:
                createItem(data["FaceProject"]["Screen"].get("Widget"))  
            
        self.expandAll()