from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QWidget,
    QFileDialog,
    QRadioButton,
    QButtonGroup,
    QLineEdit,
)

class FolderSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create the layout
        self.layout = QVBoxLayout(self)

        # Create stylesheet for radio buttons
        radioButtonStyle = """
        QRadioButton::indicator::unchecked {
            background-color: green;
        }
        QRadioButton::indicator::checked {
            background-color: limegreen;
        }
        """

        # Create the radio buttons
        self.radioOriginal = QRadioButton("Use the original folder")
        self.radioOriginal.setStyleSheet(radioButtonStyle)
        self.radioSaveTo = QRadioButton("Save to folder")
        self.radioSaveTo.setStyleSheet(radioButtonStyle)
        self.radioOriginal.setChecked(True)

        # Group the radio buttons
        self.radioGroup = QButtonGroup(self)
        self.radioGroup.addButton(self.radioOriginal)
        self.radioGroup.addButton(self.radioSaveTo)

        # Create the text input for folder path
        self.outputFolder = QLineEdit(self)
        self.outputFolder.setPlaceholderText("Select a folder...")
        self.outputFolder.setEnabled(False)  # Initially disabled

        # Create a button to open the file dialog
        self.browseButton = QPushButton("Browse...", self)
        self.browseButton.setEnabled(False)  # Initially disabled
        self.browseButton.clicked.connect(self.openFolderDialog)

        # Add the widgets to the layout
        self.layout.addWidget(self.radioOriginal)
        self.layout.addWidget(self.radioSaveTo)
        self.layout.addWidget(self.outputFolder)
        self.layout.addWidget(self.browseButton)

        # Connect the radio buttons to the method that controls input state
        self.radioOriginal.toggled.connect(self.toggleFolderInput)

    def toggleFolderInput(self):
        # Enable or disable the folder input and button based on the selected radio button
        if self.radioSaveTo.isChecked():
            self.outputFolder.setEnabled(True)
            self.browseButton.setEnabled(True)
        else:
            self.outputFolder.setEnabled(False)
            self.browseButton.setEnabled(False)

    def openFolderDialog(self):
        # Open a file dialog to select a folder
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.outputFolder.setText(folder)