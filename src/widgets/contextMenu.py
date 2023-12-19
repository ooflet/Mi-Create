#
#
# Unused for the moment
#
#

# Context Menus
# Scripts interface with this module for context menus

from PySide6.QtWidgets import QMenu

contextMenus = {
    "default" : {
        "Undo" : {
            "icon" : ":/Dark/undo-2.png"
        },
        "Redo" : {
            "icon" : ":/Dark/redo-2.png"
        },
        "Separator" : {},
        "Paste" : {
            "icon" : ":/Dark/clipboard-paste.png"
        },
    },
    "shape" : {
        "Undo" : {
            "icon" : ":/Dark/undo-2.png"
        },
        "Redo" : {
            "icon" : ":/Dark/redo-2.png"
        },
        "Separator" : {},
        "Cut" : {
            "icon" : ":/Dark/scissors.png"
        },
        "Copy" : {
            "icon" : ":/Dark/copy(1).png"
        },
        "Paste" : {
            "icon" : ":/Dark/clipboard-paste.png"
        },
        "Separator" : {},
        "Delete" : {
            "icon" : ":/Dark/x_dim.png"
        }
    },
    "image" : {

    },
    "applet" : {

    }
}

#class ContextMenu:
    