from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QProgressBar, QWidget
from widgets.folder_selection_widget import FolderSelectionWidget
from widgets.list_drag_drop_file_widget import ListDragDropFileWidget


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Compressly")

        # Create layouts
        self.pageLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()

        # Create Drag and Drop Widget
        self.dragDropWidget = ListDragDropFileWidget()
        self.pageLayout.addWidget(self.dragDropWidget)

        # Create a progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar { text-align: center; }
            QProgressBar::chunk { background-color: limegreen; }
        """)
        self.pageLayout.addWidget(self.progress)

        # Add button layout before folder selection
        self.pageLayout.addLayout(self.buttonLayout)

        # Create folder selection widget
        self.folderSelectionWidget = FolderSelectionWidget()
        self.pageLayout.addWidget(self.folderSelectionWidget)

        # Create buttons
        self.addButton = QPushButton("Add")
        self.buttonLayout.addWidget(self.addButton)

        self.removeButton = QPushButton("Remove")
        self.buttonLayout.addWidget(self.removeButton)

        self.compressButton = QPushButton("Compress")
        self.buttonLayout.addWidget(self.compressButton)

        widget = QWidget()
        widget.setLayout(self.pageLayout)
        MainWindow.setCentralWidget(widget)
