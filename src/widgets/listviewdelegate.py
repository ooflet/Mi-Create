# List Widget Delegates

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import Qt, QIcon, QFontMetrics, QPen
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QApplication

class ImageDelegate(QStyledItemDelegate):
    # Delegate to wrap filenames.

    def paint(self, painter, option, index):
        if not index.isValid():
            return

        painter.save()

        # Selected
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # Icon
        icon = index.data(Qt.DecorationRole)
        
        mode = QIcon.Normal
        state = QIcon.On if option.state & QStyle.State_Open else QIcon.Off
        icon_rect = QRect(option.rect)
        icon_rect.setSize(QSize(option.rect.width(), 48))
        icon.paint(painter, icon_rect, alignment=Qt.AlignCenter | Qt.AlignVCenter, mode=mode, state=state)

        # Text
        text = index.data(Qt.DisplayRole)
        font = QApplication.font()
        font_metrics = QFontMetrics(font)
        padding = 8
        rect = font_metrics.boundingRect(option.rect.left()+padding/2, option.rect.bottom()-icon_rect.height()+padding/2,
                                         option.rect.width()-padding, option.rect.height()-padding,
                                         Qt.AlignHCenter | Qt.AlignTop | Qt.TextWrapAnywhere,
                                         text)
        color = QApplication.palette().text().color()
        pen = QPen(color)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWrapAnywhere, text)

        painter.restore()
    
    def sizeHint(self, option, index):
        if not index.isValid():
            return super(ImageDelegate, self).sizeHint(option, index)
        else:
            text = index.data()
            font = QApplication.font()
            font_metrics = QFontMetrics(font)
            rect = font_metrics.boundingRect(0, 0, option.rect.width(), 0,
                                         Qt.AlignLeft | Qt.AlignTop | Qt.TextWrapAnywhere,
                                         text)
            size = QSize(option.rect.width(), option.rect.height()+rect.height())
            return size