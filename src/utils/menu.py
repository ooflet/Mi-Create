# Context Menus
# ooflet <ooflet@proton.me>

import sys
import json

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

sys.path.append("..")

from utils.translate import Translator

# Context Menu System notes:
#
# Context menu items allow for "inheritance" from the main window, basically
# reusing already created menu items

with open("data/context_menus.json") as file:
    contextMenus = json.load(file)

class ContextMenu(QMenu):
    def __init__(self, type, ui):
        self.ids = {}
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
                        icon = QIcon().fromTheme(properties["icon"])
                        action.setIcon(icon)
                
                if properties.get("id"):
                    print(properties["id"])
                    self.ids[action] = properties["id"]

        createContextMenu(self, contextMenus[type])