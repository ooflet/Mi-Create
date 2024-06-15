# Context Menus
# ooflet <ooflet@proton.me>

import sys
import json

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

sys.path.append("..")

from translate import QCoreApplication

# Context Menu System notes:
#
# The context menu system uses the same data structure as the properties system
#
# Context menu items allow for "inheritance" from the main window, basically
# reusing already created menu items

with open("data/contextMenus.json") as file:
    contextMenus = json.load(file)

class ContextMenu(QMenu):
    def __init__(self, type, pos, ui):
        super().__init__()
        def createContextMenu(menu, actions):
            for actionName, properties in actions.items():
                if properties.get("submenu"):
                    subMenu = menu.addMenu(actionName)
                    createContextMenu(subMenu, properties["subMenu"])
                elif properties.get("inherit"):
                    menu.addAction(getattr(ui, properties["inherit"]))
                elif properties.get("inheritSubmenu"):
                    menu.addMenu(getattr(ui, properties["inheritSubmenu"]))
                elif properties.get("specialType"):
                    if properties.get("specialType") == "seperator":
                        menu.addSeparator()
                else:
                    action = menu.addAction(actionName)
                    if properties.get("icon"):
                        icon = QIcon()
                        icon.addFile(properties["icon"], QSize(), QIcon.Mode.Normal, QIcon.State.Off)
                        action.setIcon(icon)

        createContextMenu(self, contextMenus[type])