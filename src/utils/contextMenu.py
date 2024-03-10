# Context Menus
# tostr 2024

import sys

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

sys.path.append("..")

from translate import QCoreApplication

# Context Menu System notes:
#
# The context menu system uses the same data structure as the properties system
#
# Something neat with the system is that you can inherit existing actions/menus from the
# main application. If, for example, you made an action in the window.ui file to copy an
# object, you do not have to create an entirely new action if you want to add a copy
# action to a context menu, simply add an action with the inherit property with the name
# of the action. Same also applies for submenus.

contextMenus = {
    "default" : {
        "Undo" : {
            "inherit" : "actionUndo"
        },
        "Redo" : {
            "inherit" : "actionRedo"
        },
        "sep1" : {},
        "Paste" : {
            "inherit" : "actionPaste"
        },
        "sep2" : {},
        "Zoom" : {
            "inheritSubmenu" : "menuZoom"
        }
    },
    "shape" : {
        "Undo" : {
            "inherit" : "actionUndo"
        },
        "Redo" : {
            "inherit" : "actionRedo"
        },
        "sep1" : {},
        "Cut" : {
            "inherit" : "actionCut"
        },
        "Copy" : {
            "inherit" : "actionCopy"
        },
        "Paste" : {
            "inherit" : "actionPaste"
        },
        "sep2" : {},
        "Layers" : {
            "inheritSubmenu" : "menuLayers"
        },
        "sep3" : {},
        "Delete" : {
            "inherit" : "actionDelete"
        }
    }
}

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
                elif "sep" in actionName:
                    menu.addSeparator()
                else:
                    action = menu.addAction(actionName)
                    if properties.get("icon"):
                        icon = QIcon()
                        icon.addFile(properties["icon"], QSize(), QIcon.Mode.Normal, QIcon.State.Off)
                        action.setIcon(icon)

        createContextMenu(self, contextMenus[type])