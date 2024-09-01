"""

    MIT License

    Copyright (c) 2024 Michał Gallus

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""
"""
    This project is currently a work in progress, although even in its current
    state its quite usable.
    --- To-do log ---
    TODO: Extract ffmpeg-related code to ffmpeg.py and handle things there
    TODO: Clean-up the code, ensure consistent style
    TODO: Add type-annotations
    TODO: Learn how to use linter and lint the code
    TODO: Show file progress 3/5 below progress bar
    TODO: Disable buttons on conversion
    TODO: Add cancel button
    TODO: Add icons to buttons
    TODO: Add Application icon
    TODO: Launch conversion instantly upon drag-drop
    TODO: Allow for customization of the conversion settings
    TODO: Allow for output suffix customization
    TODO: Make convert button bigger or coloured so that its easier to find
    TODO: Consider rearchitecting to MVC using QAbstractListModel etc.
    TODO: Make a git hook for linting
    TODO: Figure out how to do stylesheets properly
    TODO: Learn how to and create Unit and Integration tests
    TODO: Create a CI for running tests and making sure linting was done
    TODO: Automate packaging on CI
    TODO: Implement QML instead of traditional Qt

    pyinstaller --name "Compressly" --noconsole main.py --add-binary "external/ffmpeg/ffmpeg.exe;external/ffmpeg/" --add-binary "external/ffmpeg/SvtAv1Enc.dll;external/ffmpeg/" --noconfirm
"""

import logging as log
import argparse, re, logger, os, sys
from pathlib import Path
from typing import List, Tuple
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QListWidget,
    QFileDialog,
    QDialog,
    QRadioButton,
    QButtonGroup,
    QLineEdit,
    QProgressBar,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Slot, QProcess
from PySide6.QtGui import QKeySequence

class ListDragDropWidget(QWidget): ...

log_ffmpeg = False

# Source: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/44352931#44352931
def resourcePath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Compressly")

        pageLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.dragDropWidget = ListDragDropWidget()

        pageLayout.addWidget(self.dragDropWidget)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar { text-align: center; }
            QProgressBar::chunk { background-color: limegreen; }
        """)
        pageLayout.addWidget(self.progress)

        pageLayout.addLayout(buttonLayout)

        self.folderSelectionWidget = FolderSelectionWidget()
        pageLayout.addWidget(self.folderSelectionWidget)

        button = QPushButton("Add")
        button.pressed.connect(self.browseFiles)
        button.setShortcut(QKeySequence("A"))
        buttonLayout.addWidget(button)

        self.dialog = QFileDialog(self)
        self.dialog.setFileMode(QFileDialog.ExistingFiles)
        self.dialog.setWindowTitle('Select videos')
        self.dialog.setNameFilter("Video files *.mov *.mp4")
        self.dialog.finished.connect(self.filesSelected)

        button = QPushButton("Remove")
        button.pressed.connect(self.remove)
        button.setShortcut(QKeySequence("Delete"))
        buttonLayout.addWidget(button)

        self.ffmpeg = QProcess()
        self.ffmpeg.setProgram(resourcePath("external/ffmpeg/ffmpeg.exe"))
        self.ffmpeg.finished.connect(self.ffmpegFinished)
        self.ffmpeg.readyReadStandardOutput.connect(self.ffmpegStdOut)
        self.ffmpeg.readyReadStandardError.connect(self.ffmpegStdErr)
        self.currentIndex = 0

        button = QPushButton("Convert")
        button.pressed.connect(self.startProcesses)
        button.setShortcut(QKeySequence("Return"))
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

    def parseDuration(self, line):
        """
        Extract the 'Duration' field from the FFmpeg output.
        """
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
        if duration_match:
            hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
            total_duration = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
            return total_duration
        return None

    def parseProgress(self, line, total_duration):
        """
        Extract the 'time' field from the FFmpeg progress line and calculate the percentage of completeness.
        """
        time_match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
        if time_match:
            hours, minutes, seconds, centiseconds = map(int, time_match.groups())
            current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
            percentage = (current_time / total_duration) * 100
            return percentage
        return None

    def ffmpegStdErr(self):
        data = self.ffmpeg.readAllStandardError()
        stderr = bytes(data).decode("utf8")

        # Forward FFmpeg output
        if log_ffmpeg:
            log.info(stderr)

        # Update progress bar
        for line in stderr.split("\n"):
            if self.total_duration is None:
                self.total_duration = self.parseDuration(line)
            if self.total_duration:
                percentage = self.parseProgress(line, self.total_duration)
                if percentage is not None:
                    self.progress.setValue(percentage)

    def ffmpegStdOut(self):
        data = self.ffmpeg.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")

        # Forward output if any
        if log_ffmpeg:
            log.info(stdout)

    def ffmpegFinished(self):
        self.progress.setValue(100)
        self.currentIndex += 1
        self.startNextProcess()
        log.info("Finished compressing file.")

    def makeFilename(self, itemWidget):
        path = Path(itemWidget.text())
        newFilename = f"{path.stem}_compressed.mp4"

        if self.folderSelectionWidget.radioSaveTo.isChecked():
            newPath = Path(self.folderSelectionWidget.outputFolder.text())
            return str(newPath.joinpath(newFilename))
        else:
            return str(path.with_name(newFilename))


    def startProcesses(self):
        self.currentIndex = 0
        self.startNextProcess()

    def startNextProcess(self):
        widget = self.dragDropWidget.listWidget
        if self.currentIndex < widget.count():
            item = widget.item(self.currentIndex)
            newFilename = self.makeFilename(item)
            self.ffmpeg.setArguments(["-i", item.text(), "-c:v", "libsvtav1", newFilename, "-y"])
            # Start the process
            self.ffmpeg.start()
            self.total_duration = None


class ListDragDropWidget(QWidget):
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

def process_cli_args() -> Tuple[argparse.ArgumentParser, List[str]]:
    """
    Process CLI arguments.

    :return: A tuple of the parsed arguments and the unparsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logging', action='store_true')
    parser.add_argument('-lf', '--logging_ffmpeg', action='store_true')

    parsed_args, unparsed_args = parser.parse_known_args()
    parsed_args.logging = parsed_args.logging or parsed_args.logging_ffmpeg
    return parsed_args, unparsed_args

if __name__ == "__main__":
    parsed_args, unparsed_args = process_cli_args()
    log_ffmpeg = parsed_args.logging_ffmpeg
    if parsed_args.logging:
        logger.init()
    log.info("App started.")
    app = QApplication(unparsed_args)
    app.setStyle('fusion')
    window = MainWindow()
    window.show()
    app.exec()