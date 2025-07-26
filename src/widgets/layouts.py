from PyQt6.QtWidgets import QLayout, QSizePolicy
from PyQt6.QtCore import QSize, QRect, QPoint, Qt


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=5):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        return self.itemList[index] if 0 <= index < len(self.itemList) else None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        """Calculate height needed for given width (used by scroll area)."""
        x = 0
        y = 0
        lineHeight = 0
        spaceX = self.spacing()
        spaceY = self.spacing()
        left, top, right, bottom = self.getContentsMargins()
        effectiveWidth = width - left - right

        for item in self.itemList:
            size = item.sizeHint()
            if x + size.width() > effectiveWidth and x > 0:
                x = 0
                y += lineHeight + spaceY
                lineHeight = 0

            x += size.width() + spaceX
            lineHeight = max(lineHeight, size.height())

        y += lineHeight  # last line
        return y + top + bottom

    def minimumSize(self):
        """Return a minimum size that includes all children laid out."""
        return self.sizeHint()

    def sizeHint(self):
        width = self.parentWidget().width() if self.parentWidget() else 400
        return QSize(width, self.heightForWidth(width))

    def setGeometry(self, rect):
        super().setGeometry(rect)
        x, y = rect.x(), rect.y()
        lineHeight = 0
        spaceX = self.spacing()
        spaceY = self.spacing()

        for item in self.itemList:
            size = item.sizeHint()
            nextX = x + size.width()

            if nextX > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spaceY
                nextX = x + size.width()
                lineHeight = 0

            item.setGeometry(QRect(QPoint(x, y), size))
            x = nextX + spaceX
            lineHeight = max(lineHeight, size.height())

    def clear(self):
        while self.count():
            item = self.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                widget.setParent(None)

