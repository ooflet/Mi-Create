import sys
import json
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen

class GridDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        rect = option.rect  # Get the rectangle area of the item
        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        # Create a custom pen with a thickness of 1 pixel
        pen = QPen(QColor(60,60,60))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw horizontal line at the bottom of the cell (except for the last row)
        if index.row() < index.model().rowCount() - 1:
            painter.drawLine(left, bottom, right, bottom)

        # Draw vertical line at the right edge of the cell
        painter.drawLine(right, top, right, bottom)

        # Call the base class paint method to paint the item
        super().paint(painter, option, index)

class PropertiesWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tree_widget = QTreeWidget(self)
        #self.tree_widget.setItemDelegate(VerticalLineDelegate())
        self.tree_widget.setFrameShape(QFrame.NoFrame)
        self.tree_widget.setRootIsDecorated(False)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.tree_widget.setUniformRowHeights(True)

        self.tree_widget.setHeaderLabels(["Property", "Value"])
        self.tree_widget.setItemDelegate(GridDelegate())

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        line_edit_widget = self.create_line_edit()  # Create QLineEdit widget
        spin_box_widget = self.create_spin_box()
        combo_box_widget = self.create_combo_box()
        check_box_widget = self.create_check_box()

        self.add_property("TextProperty", line_edit_widget)  # Use the QLineEdit widget
        self.add_property("DropdownProperty", combo_box_widget)
        self.add_property("NumericalProperty", spin_box_widget)
        self.add_property("BoolProperty", check_box_widget)

    def deselect_and_unfocus(self):
        line_edit_widget = self.sender()  # Get the sender of the signal
        line_edit_widget.clearFocus()
        self.deselect_item()

    def create_line_edit(self):
        line_edit = QLineEdit(self)
        line_edit.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        line_edit.editingFinished.connect(self.deselect_and_unfocus)
        return line_edit

    def deselect_item(self):
        self.tree_widget.setCurrentItem(None)

    def deselect_on_focus_out(self, event, line_edit):
        if not line_edit.underMouse():
            self.deselect_item()

    def add_property(self, name, value_widget):
        item = QTreeWidgetItem(self.tree_widget, [name, ""])
        self.tree_widget.setItemWidget(item, 1, value_widget)

    def create_spin_box(self):
        spin_box = QSpinBox(self)
        spin_box.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        spin_box.editingFinished.connect(self.deselect_and_unfocus)
        return spin_box
    
    def create_combo_box(self):
        combo_box = QComboBox(self)
        return combo_box
    
    def create_check_box(self):
        check_box = QCheckBox(self)
        return check_box
    
    def loadProperties(self, json):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Properties Widget Example")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        properties_widget = PropertiesWidget()
        layout.addWidget(properties_widget)
        

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())