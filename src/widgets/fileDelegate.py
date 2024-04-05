# from https://stackoverflow.com/questions/69474089/how-to-get-item-text-to-wrap-using-a-qlistview-set-to-iconmode-and-model-set-to/69489044#69489044

from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QApplication
from PyQt6.QtGui import QIcon, QFontMetrics, QPen
from PyQt6.QtCore import Qt, QRect, QSize

class ItemNameDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            print("return")
            return

        painter.save()

        # Selected
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # Icon
        icon = index.data(Qt.DecorationRole)
        
        mode = QIcon.Mode.Normal
        state = QIcon.State.On if option.state & QStyle.StateFlag.State_Open else QIcon.State.Off
        icon_rect = QRect(option.rect)
        icon_rect.setSize(QSize(option.rect.width(), 40))
        icon.paint(painter, icon_rect, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, mode=mode, state=state)

        # Text
        text = index.data(Qt.ItemDataRole.DisplayRole)
        font = QApplication.font()
        font_metrics = QFontMetrics(font)
        padding = 8
        rect = font_metrics.boundingRect(option.rect.left()+padding/2, option.rect.bottom()-icon_rect.height()+padding/2,
                                         option.rect.width()-padding, option.rect.height()-padding,
                                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWrapAnywhere,
                                         text)
        color = QApplication.palette().text().color()
        pen = QPen(color)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWrapAnywhere, text)

        painter.restore()
    
    def sizeHint(self, option, index):
        if not index.isValid():
            return super(ItemNameDelegate, self).sizeHint(option, index)
        else:
            text = index.data()
            font = QApplication.font()
            font_metrics = QFontMetrics(font)
            rect = font_metrics.boundingRect(0, 0, option.rect.width(), 0,
                                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWrapAnywhere,
                                         text)
            size = QSize(option.rect.width(), option.rect.height()+rect.height())
            return size
