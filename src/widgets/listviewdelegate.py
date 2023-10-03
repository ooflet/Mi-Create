# List Widget Delegates
# Makes it so that text is below images

from PySide6.QtCore import *
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import *

class ListStyledItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignTop
        option.decorationPosition = QStyleOptionViewItem.Top