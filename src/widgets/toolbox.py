from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QTreeView, QStyledItemDelegate

class BranchDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = option
        if index.column() == 0:
            opt.rect.adjust(opt.rect.height(), 0, 0, 0)
        super().paint(painter, opt, index)
        if index.column() == 0 and not index.parent().isValid():  # Only for top-level items
            branch_rect = QRect(0, opt.rect.y(), opt.rect.height(), opt.rect.height())
            self.drawBranchIndicator(painter, branch_rect, self.parent().isExpanded(index))

    def drawBranchIndicator(self, painter, rect, expanded):
        if expanded:
            # Use a custom QPixmap for expanded items (customize this pixmap)
            pixmap = QPixmap("path_to_expanded_icon.png")
        else:
            # Use a custom QPixmap for collapsed items (customize this pixmap)
            pixmap = QPixmap("path_to_collapsed_icon.png")

        painter.drawPixmap(rect, pixmap)

class TreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        delegate = BranchDelegate(self)
        self.setItemDelegate(delegate)
        self.setIndentation(0)
        self.setHeaderHidden(True)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        last_state = self.isExpanded(index)
        super().mousePressEvent(event)
        if index.isValid() and last_state == self.isExpanded(index):
            self.setExpanded(index, not last_state)
