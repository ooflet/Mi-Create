from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

class ResourcesDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def initStyleOption(self, option, index):
        option.decorationPosition = QStyleOptionViewItem.Position.Top
        option.decorationAlignment = Qt.AlignmentFlag.AlignCenter
        return super().initStyleOption(option, index)