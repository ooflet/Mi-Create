from PyQt6.QtWidgets import QApplication, QComboBox, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QPoint


class SearchableMenu(QFrame):
    MAX_HEIGHT = 450  # maximum height

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("dropdown")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)

        self.menuLayout = QVBoxLayout(self)
        self.menuLayout.setContentsMargins(0, 0, 0, 0)
        self.menuLayout.setSpacing(0)

        # Search box wrapper
        searchWrapper = QVBoxLayout()
        searchWrapper.setContentsMargins(6, 6, 6, 6)
        self.searchBox = QLineEdit(self, placeholderText="Search...")
        searchWrapper.addWidget(self.searchBox)

        self.searchBox.textChanged.connect(self.search)

        # List
        self.list = QListWidget()
        self.list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list.setFrameShape(QFrame.Shape.NoFrame)

        self.menuLayout.addLayout(searchWrapper)
        self.menuLayout.addWidget(self.list)

        self.searchBox.installEventFilter(self)
        self.list.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.searchBox and event.type() == event.Type.KeyPress:
            print(event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up), event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter))
            if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                # Send focus to list
                self.list.setFocus()
                QApplication.sendEvent(self.list, event)
                return True
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # Select current item if available
                current = self.list.currentItem()
                if current:
                    print("enter")
                    self.list.itemClicked.emit(current)
                return True
        elif obj is self.list and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # Select current item if available
                current = self.list.currentItem()
                if current:
                    print("enter")
                    self.list.itemClicked.emit(current)
                return True

        return super().eventFilter(obj, event)

    def search(self):
        filter_text = self.searchBox.text()
        visible_items = []
        for i in range(self.list.count()):
            item = self.list.item(i)
            if filter_text.lower() in item.data(100).lower():
                item.setHidden(False)
                visible_items.append(i)
            else:
                item.setHidden(True)
                
        if filter_text != "" and visible_items != []:
                self.list.setCurrentRow(visible_items[0])

        self.adjustHeight(len(visible_items))

    def addItems(self, items):
        for item in items:
            widget = QWidget()
            widgetLayout = QHBoxLayout()
            widgetLayout.setContentsMargins(6, 6, 6, 6)
            itemLabel = QLabel(item)
            itemWidget = QListWidgetItem(self.list)
            itemWidget.setData(100, item)
            widgetLayout.addWidget(itemLabel)
            widget.setLayout(widgetLayout)
            itemWidget.setSizeHint(widget.sizeHint())
            self.list.addItem(itemWidget)
            self.list.setItemWidget(itemWidget, widget)
        self.adjustHeight(len(items))
        self.search()

    def adjustHeight(self, visible_count):
        search_height = self.searchBox.sizeHint().height() + 14
        list_height = sum(
            self.list.item(i).sizeHint().height()
            for i in range(self.list.count())
            if not self.list.item(i).isHidden()
        )
        total_height = search_height + list_height
        final_height = min(total_height, self.MAX_HEIGHT)
        if final_height < 80:
            final_height = 80
        self.setFixedHeight(final_height)


class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        def currentItemChanged():
            self.setCurrentIndex(self.popup.list.currentRow())
            self.popup.hide()
            self.activated.emit(self.popup.list.currentRow())

        self.popup = SearchableMenu(self)
        self.popup.list.itemClicked.connect(currentItemChanged)

    def addItems(self, items):
        self.popup.list.clear()
        self.items = items
        self.popup.addItems(items)
        self.popup.list.setCurrentRow(0)
        super().addItems(items)
        self.setCurrentIndex(0)

    def setCurrentText(self, text):
        super().setCurrentText(text)
        self.selectByName(text)

    def showPopup(self):
        width = max(self.width(), 200)
        pos = self.mapToGlobal(QPoint(self.width() - width, 0))
        self.popup.move(pos)
        self.popup.setFixedWidth(width)
        self.popup.searchBox.setFocus()
        self.popup.show()

    def selectByName(self, name: str):
        index = self.findText(name, Qt.MatchFlag.MatchExactly)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            self.setCurrentIndex(0)

        for i in range(self.popup.list.count()):
            item = self.popup.list.item(i)
            if item.data(100) == name:
                self.popup.list.setCurrentRow(i)
                break
