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
    TODO: Remove filename from the QListWidget once the compression is finished
    TODO: Consider rearchitecting to MVC using QAbstractListModel etc.
        TODO: Reimplement data source as a queue from which the elemnts are popped
    TODO: Ensure that only supported files can be dragged/dropped
    TODO: Create a list of supported formats and use it for filtering in both
          file dialog, as well as drag and drop.
    TODO: If some drag-drop fails due to unmet conditions, report that to the user
    TODO: If there's a selection present, convert only the selected files
    TODO: Apply appropriate green styling to QListWidget for selected items
    TODO: Clean-up the code, ensure consistent style
    TODO: Add type-annotations
    TODO: Learn how to use linter and lint the code
    TODO: Show file progress 3/5 below progress bar
    TODO: Disable buttons on conversion
    TODO: Add cancel button
    TODO: Add icons to buttons
    TODO: Add Application icon
    TODO: Allow for customization of the conversion settings
    TODO: Allow for output suffix customization
    TODO: Make convert button bigger or coloured so that its easier to find
    TODO: Make a git hook for linting
    TODO: Figure out how to do stylesheets properly
    TODO: Learn how to and create Unit and Integration tests
    TODO: Create a CI for running tests and making sure linting was done
    TODO: Implement QML instead of traditional Qt

    pyinstaller --name "Compressly" --noconsole main.py --add-binary "external/ffmpeg/ffmpeg.exe;external/ffmpeg/" --add-binary "external/ffmpeg/SvtAv1Enc.dll;external/ffmpeg/" --noconfirm
"""

import logging as log
import argparse, logger
from pathlib import Path
from typing import List, Tuple
from PySide6.QtWidgets import ( QApplication, QMainWindow, QFileDialog, QDialog)
from PySide6.QtCore import Slot
from PySide6.QtGui import QKeySequence
from ui_mainwindow import Ui_MainWindow
from ffmpeg import FFmpeg

class MainWindow(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.ui = Ui_MainWindow()  # Create an instance of the UI class
        self.ui.setupUi(self)  # Set up the UI

        # File dialog configuration
        self.dialog = QFileDialog(self)
        self.dialog.setFileMode(QFileDialog.ExistingFiles)
        self.dialog.setWindowTitle('Select videos')
        self.dialog.setNameFilter("Video files *.mov *.mp4")
        self.dialog.finished.connect(self.filesSelected)

        # Button connections
        self.ui.addButton.pressed.connect(self.dialog.open)
        self.ui.addButton.setShortcut(QKeySequence("A"))
        self.ui.removeButton.pressed.connect(self.removeSelectedEntries)
        self.ui.removeButton.setShortcut(QKeySequence("Delete"))
        self.ui.compressButton.pressed.connect(self.startProcesses)
        self.ui.compressButton.setShortcut(QKeySequence("Return"))

        # FFmpeg process setup
        self.ffmpeg = FFmpeg(args.logging_ffmpeg)
        self.ffmpeg.progress.connect(self.ui.progress.setValue)
        self.ffmpeg.fileFinished.connect(self.fileFinished)

        # Index for file processing
        self.currentIndex = 0  

    @Slot(QDialog.DialogCode)
    def filesSelected(self, result: QDialog.DialogCode) -> None:
        if result == QDialog.Accepted:
            self.ui.dragDropWidget.listWidget.addItems(self.dialog.selectedFiles())

    def removeSelectedEntries(self) -> None:
        widget = self.ui.dragDropWidget.listWidget
        items = widget.selectedItems()
        for item in items:
            widget.takeItem(widget.row(item))

    def createOutputFilename(self, inputFile):
        path = Path(inputFile)
        newFilename = f"{path.stem}_compressed.mp4"

        if self.ui.folderSelectionWidget.radioSaveTo.isChecked():
            newPath = Path(self.ui.folderSelectionWidget.outputFolder.text())
            return str(newPath.joinpath(newFilename))
        else:
            return str(path.with_name(newFilename))

    def startProcesses(self):
        self.currentIndex = 0
        self.startNextProcess()

    def startNextProcess(self):
        widget = self.ui.dragDropWidget.listWidget
        if self.currentIndex < widget.count():
            item = widget.item(self.currentIndex)
            inputFile = item.text()
            outputFile = self.createOutputFilename(inputFile)
            self.ffmpeg.convert(inputFile, outputFile)

    def fileFinished(self):
        self.currentIndex += 1
        self.startNextProcess()

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
    if parsed_args.logging:
        logger.init()
    log.info("App started.")
    app = QApplication(unparsed_args)
    app.setStyle('fusion')
    window = MainWindow(parsed_args)
    window.show()
    app.exec()

