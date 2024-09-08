import pytest
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from widgets.list_drag_drop_file_widget import ListDragDropFileWidget

@pytest.fixture
def widget(qtbot):
    # Create the widget for testing
    widget = ListDragDropFileWidget()
    widget.show()
    qtbot.addWidget(widget)
    return widget

def test_drag_enter_event(widget, qtbot):
    # Simulate dragging a file into the widget
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("C:/path/to/file.mp4")])
    event = QDragEnterEvent(widget.rect().center(), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    
    # Trigger the dragEnterEvent
    widget.dragEnterEvent(event)
    
    # Assert that the list is hidden and the drag-and-drop label is shown
    assert not widget.listWidget.isVisible()
    assert widget.dragAndDropLabel.isVisible()

def test_drag_enter_event_no_urls(widget, qtbot):
    # Simulate dragging a file into the widget
    mime_data = QMimeData()
    mime_data.setHtml("<html><body><p>Some text</p></body></html>")
    event = QDragEnterEvent(widget.rect().center(), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    
    # Trigger the dragEnterEvent
    widget.dragEnterEvent(event)
    
    # Assert that the list is hidden and the drag-and-drop label is shown
    assert widget.listWidget.isVisible()
    assert not widget.dragAndDropLabel.isVisible()
    
def test_drag_leave_event(widget, qtbot):
    # First simulate dragging a file into the widget
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("C:/path/to/file.mp4")])
    enter_event = QDragEnterEvent(widget.rect().center(), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    widget.dragEnterEvent(enter_event)
    
    # Then simulate leaving the drag area
    leave_event = QDragEnterEvent(widget.rect().center(), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    widget.dragLeaveEvent(leave_event)
    
    # Assert that the list is visible again and the drag-and-drop label is hidden
    assert widget.listWidget.isVisible()
    assert not widget.dragAndDropLabel.isVisible()

def test_drop_event(widget, qtbot):
    # Simulate dropping files into the widget
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("C:/path/to/file1.mp4"), QUrl.fromLocalFile("C:/path/to/file2.mp4")])
    event = QDropEvent(widget.rect().center(), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
    
    with qtbot.waitSignal(widget.dropped):
        widget.dropEvent(event)
    
    # Assert that the files were added to the list
    assert widget.listWidget.count() == 2
    assert widget.listWidget.item(0).text() == "C:/path/to/file1.mp4"
    assert widget.listWidget.item(1).text() == "C:/path/to/file2.mp4"

    # Assert that the list is visible again and the drag-and-drop label is hidden
    assert widget.listWidget.isVisible()
    assert not widget.dragAndDropLabel.isVisible()
