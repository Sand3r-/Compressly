"""
    TODO("Implement conversion")
    TODO("Allow for deleting a selected file by pressing delete/backspace")
    TODO("Disable as much as possible in ffmpeg, remember to attach libav1 DLL")
    In other words, check which encoders can be removed, which filters and etc.
    
"""

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QListWidget, QFileDialog, QDialog
from PySide6.QtCore import Qt, Slot
import sys

class ListDragDropWidget(QWidget): ...

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Compressly")

        pageLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.dragDropWidget = ListDragDropWidget()

        pageLayout.addWidget(self.dragDropWidget)
        pageLayout.addLayout(buttonLayout)

        button = QPushButton("Add")
        button.pressed.connect(self.browseFiles)
        buttonLayout.addWidget(button)

        self.dialog = QFileDialog(self)
        self.dialog.setFileMode(QFileDialog.ExistingFiles)
        self.dialog.setWindowTitle('Select videos')
        self.dialog.setNameFilter("Video files *.mov *.mp4")
        self.dialog.finished.connect(self.filesSelected)

        button = QPushButton("Remove")
        button.pressed.connect(self.remove)
        buttonLayout.addWidget(button)

        button = QPushButton("Remove all")
        button.pressed.connect(self.removeAll)
        buttonLayout.addWidget(button)

        button = QPushButton("Convert")
        button.pressed.connect(self.convert)
        buttonLayout.addWidget(button)

        widget = QWidget()
        widget.setLayout(pageLayout)
        self.setCentralWidget(widget)

    def browseFiles(self):
        self.dialog.open()

    @Slot(QDialog.DialogCode)
    def filesSelected(self, result: QDialog.DialogCode) -> None:
        if result == QDialog.Accepted:
            self.dragDropWidget.listWidget.addItems(self.dialog.selectedFiles())

    def remove(self):
        widget = self.dragDropWidget.listWidget
        items = widget.selectedItems()
        for item in items:
            widget.takeItem(widget.row(item))

    def removeAll(self):
        self.dragDropWidget.listWidget.clear()

    def convert(self):
        pass


class ListDragDropWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.listWidget = QListWidget()
        self.dragAndDropLabel = QLabel("Drop file(s) here")
        self.dragAndDropLabel.setAlignment(Qt.AlignCenter)
        self.dragAndDropLabel.setStyleSheet("""
            color: limegreen;
            text-align: center;
            border: 2px solid limegreen;
            border-radius: 4px;
            font-size: 18px;
        """)

        self.layout.addWidget(self.listWidget)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.layout.replaceWidget(self.listWidget, self.dragAndDropLabel)
            self.listWidget.hide()
            self.dragAndDropLabel.show()
            
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.layout.replaceWidget(self.dragAndDropLabel, self.listWidget)
        self.dragAndDropLabel.hide()
        self.listWidget.show()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.listWidget.addItem(url.toLocalFile())
        self.layout.replaceWidget(self.dragAndDropLabel, self.listWidget)
        self.dragAndDropLabel.hide()
        self.listWidget.show()

app = QApplication(sys.argv)
app.setStyle('fusion')
window = MainWindow()
window.show()
app.exec()