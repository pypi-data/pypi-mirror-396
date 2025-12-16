from PyQt6.QtCore import QLibraryInfo
from PyQt6.QtWidgets import QApplication, QLabel
import os

plugin_root = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
print("Plugin root:", plugin_root)
print("Platforms dir:", os.path.join(plugin_root, "platforms"))

app = QApplication([])
label = QLabel("PyQt6 OK?")
label.resize(300, 100)
label.show()
app.exec()
