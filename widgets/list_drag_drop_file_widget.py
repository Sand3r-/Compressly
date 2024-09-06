from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal

class ListDragDropFileWidget(QWidget):
    dropped = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
        self.dropped.emit()