import pytest
from unittest.mock import MagicMock, patch
from ffmpeg import FFmpeg

@pytest.fixture
def ffmpeg():
    return FFmpeg()

def test_convert(ffmpeg):
    # Mock the QProcess object inside the FFmpeg class
    mock_process = MagicMock()
    ffmpeg.process = mock_process

    # Call the convert method
    input_file = "input.mp4"
    output_file = "output.mp4"
    ffmpeg.convert(input_file, output_file)

    # Assertions
    # Check that setArguments was called with the correct arguments
    mock_process.setArguments.assert_called_once_with(["-i", input_file, "-c:v", "libsvtav1", output_file, "-y"])

    # Check that the process was started
    mock_process.start.assert_called_once()

@patch("ffmpeg.log")  # Mock the logging module
def test_handle_stdout_integration(mock_log, ffmpeg):
    # Mock the QProcess object inside the FFmpeg class
    mock_process = MagicMock()
    # Simulating FFmpeg stdout output, assuming duration is parsed first, then progress
    stdout_data = b"Duration: 00:05:10.50\ntime=00:02:35.25\n"
    mock_process.readAllStandardOutput.return_value = stdout_data
    ffmpeg.process = mock_process

    # Mock the progress signal to track emits
    ffmpeg.progress = MagicMock()

    # Enable logging in the FFmpeg instance
    ffmpeg.logging = True

    # Call the function
    ffmpeg._handleStdOut()

    # Assertions
    # Check that the log.info was called for both lines of the stdout
    mock_log.info.assert_called_with(stdout_data.decode("utf8"))

    # Ensure _parseDuration was called and set total_duration
    assert ffmpeg.total_duration == 310.50  # 5 minutes * 60 + 10 seconds + 0.50 seconds

    # Ensure _parseProgress was called and the correct percentage was emitted
    percentage = (155.25 / 310.50) * 100  # Progress calculation for 2 minutes 35.25 seconds out of 5:10.50
    ffmpeg.progress.emit.assert_called_once_with(percentage)


@patch("ffmpeg.log")  # Mock the logging module
def test_handle_stdout_no_progress(mock_log, ffmpeg):
    # Mock the QProcess object inside the FFmpeg class
    mock_process = MagicMock()
    stdout_data = b"No valid duration or time here\n"
    mock_process.readAllStandardOutput.return_value = stdout_data
    ffmpeg.process = mock_process

    # Mock the progress signal
    ffmpeg.progress = MagicMock()

    # Enable logging in the FFmpeg instance
    ffmpeg.logging = True

    # Call the function
    ffmpeg._handleStdOut()

    # Assertions
    # Check that the log.info was called with the stdout
    mock_log.info.assert_called_with(stdout_data.decode("utf8"))

    # Ensure that _parseDuration and _parseProgress did not result in progress emits
    ffmpeg.progress.emit.assert_not_called()

@patch("ffmpeg.log")  # Mock the logging module
def test_handle_stderr_with_logging_enabled(mock_log, ffmpeg):
    # Mock the QProcess object inside the FFmpeg class
    mock_process = MagicMock()
    stderr_data = b"Sample FFmpeg error output"
    mock_process.readAllStandardError.return_value = stderr_data
    ffmpeg.process = mock_process

    # Enable logging in the FFmpeg instance
    ffmpeg.logging = True

    # Call the function
    ffmpeg._handleStdErr()

    # Assert that the log.info was called with the decoded stderr
    mock_log.error.assert_called_once_with("Sample FFmpeg error output")


@patch("ffmpeg.log")  # Mock the logging module
def test_handle_stderr_with_logging_disabled(mock_log, ffmpeg):
    # Mock the QProcess object inside the FFmpeg class
    mock_process = MagicMock()
    stderr_data = b"Sample FFmpeg error output"
    mock_process.readAllStandardError.return_value = stderr_data
    ffmpeg.process = mock_process

    # Disable logging in the FFmpeg instance
    ffmpeg.logging = False

    # Call the function
    ffmpeg._handleStdErr()

    # Assert that log.info was NOT called
    mock_log.error.assert_not_called()