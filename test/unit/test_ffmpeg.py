import os
import pytest
from ffmpeg import FFmpeg

@pytest.fixture
def ffmpeg():
    return FFmpeg()

@pytest.mark.parametrize("line, expected", [
    ("Duration: 00:05:10.50", 310.50),     # 5 minutes * 60 + 10 seconds + 0.50 seconds
    ("Duration: 01:45:30.25", 6330.25),    # 1 hour * 3600 + 45 minutes * 60 + 30 seconds + 0.25 seconds
    ("Duration: 00:00:00.00", 0.00),       # Edge case with zero duration
    ("No Duration here", None),            # No duration present in the line
    ("Duration: 99:99:99.99", None),       # Invalid time format should return None
    ("Duration: 01:05", None)              # Partial duration should return None
])
def test_parse_duration(ffmpeg, line, expected):
    result = ffmpeg._parseDuration(line)
    assert result == expected

@pytest.mark.parametrize("line, total_duration, expected", [
    ("time=00:00:10.50", 310.50, (10.50 / 310.50) * 100),  # 10.50 seconds out of 310.50 total seconds
    ("time=00:05:10.50", 310.50, 100.0),                   # Complete progress (time equals total duration)
    ("time=00:02:35.25", 310.50, (155.25 / 310.50) * 100), # Partial progress
    ("time=01:45:30.25", 6330.25, 100.0),                  # Full progress for a long duration
    ("No time here", 310.50, None),                        # No time match should return None
    ("time=99:99:99.99", 310.50, None),                    # Invalid time format should return None
    ("time=00:00:00.00", 310.50, 0.0),                     # Edge case with zero time
])
def test_parse_progress(ffmpeg, line, total_duration, expected):
    result = ffmpeg._parseProgress(line, total_duration)
    assert result == expected

def test_finished():
    def handleProgress(progress):
        assert progress == 100
        assert ffmpeg.process.exitCode() == 0

    def handleFinished():
        assert ffmpeg.process.exitCode() == 0

    ffmpeg = FFmpeg()
    ffmpeg.progress.connect(handleProgress)
    ffmpeg.fileFinished.connect(handleFinished)
    ffmpeg._finished()

def test_program_exists():
    assert os.path.exists(FFmpeg().process.program())