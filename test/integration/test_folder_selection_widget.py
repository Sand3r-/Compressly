from unittest.mock import patch
import pytest
from widgets.folder_selection_widget import FolderSelectionWidget
from PySide6 import QtCore

@pytest.fixture
def widget(qtbot):
    # Create the widget for testing
    widget = FolderSelectionWidget()
    qtbot.addWidget(widget)  # Ensure widget gets cleaned up after test
    return widget

def test_initial_state(widget):
    # Test initial state: the radioOriginal is checked, folder input is disabled
    assert widget.radioOriginal.isChecked()
    assert not widget.outputFolder.isEnabled()
    assert not widget.browseButton.isEnabled()

def test_toggle_folder_input(widget, qtbot):
    # Test toggling between radio buttons to enable/disable folder input
    # Toggle the radioSaveTo button to enable the folder input and browse button
    qtbot.mouseClick(widget.radioSaveTo, QtCore.Qt.MouseButton.LeftButton)
    
    assert widget.outputFolder.isEnabled()
    assert widget.browseButton.isEnabled()

    # Toggle back to radioOriginal, the folder input should be disabled again
    qtbot.mouseClick(widget.radioOriginal, QtCore.Qt.MouseButton.LeftButton)
    
    assert not widget.outputFolder.isEnabled()
    assert not widget.browseButton.isEnabled()

@patch('folder_selection_widget.QFileDialog.getExistingDirectory', return_value='/path/to/folder')
def test_open_folder_dialog(mock_get_existing_directory, widget, qtbot):
    # Test the folder dialog opening and folder path being set
    qtbot.mouseClick(widget.radioSaveTo, QtCore.Qt.MouseButton.LeftButton)  # Enable the browse button
    qtbot.mouseClick(widget.browseButton, QtCore.Qt.MouseButton.LeftButton)  # Click the browse button

    # Verify QFileDialog was called
    mock_get_existing_directory.assert_called_once()

    # Verify the output folder text was updated
    assert widget.outputFolder.text() == '/path/to/folder'
