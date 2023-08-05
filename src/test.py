from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

app = QApplication([])
loader = QUiLoader()
ui_file = QFile("C:\\Users\\Justin\\Documents\\metakey.txt")
data = ui_file.readAll()
content = bytes(data).decode('utf-8')
print("-----------------------------------------------------------------------------")
print(content)
print("-----------------------------------------------------------------------------")
ui_file.open(QFile.ReadOnly)
window = loader.load(ui_file)
ui_file.close()

if window is None:
    print("Failed to load UI file.")
else:
    window.show()
    app.exec()