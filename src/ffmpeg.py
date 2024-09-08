import sys, os, re
import logging as log
from PySide6.QtCore import QProcess, Signal, QObject

# Source: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/44352931#44352931
def resourcePath(relative_path):
    """ Get absolute path to resource, needed by PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class FFmpeg(QObject):
    progress = Signal(int)
    fileFinished = Signal()
    def __init__(self, logging=False):
        super().__init__()
        self.process = QProcess()
        self.process.setProgram(resourcePath("../external/ffmpeg/ffmpeg.exe"))
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.finished.connect(self._finished)
        self.process.readyReadStandardOutput.connect(self._handleStdOut)
        self.process.readyReadStandardError.connect(self._handleStdErr)
        self.logging = logging
        self.total_duration = None

    def convert(self, inputFile, outputFile):
        self.process.setArguments(["-i", inputFile, "-c:v", "libsvtav1", outputFile, "-y"])
        self.process.start()

    def _parseDuration(self, line):
        """
        Extract the 'Duration' field from the FFmpeg output.
        """
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
        if duration_match:
            hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
            if minutes <= 59 or seconds <= 59:
                total_duration = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
                return total_duration
        return None

    def _parseProgress(self, line, total_duration):
        """
        Extract the 'time' field from the FFmpeg progress line and calculate the percentage of completeness.
        """
        time_match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
        if time_match:
            hours, minutes, seconds, centiseconds = map(int, time_match.groups())
            if minutes <= 59 or seconds <= 59:
                current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
                percentage = (current_time / total_duration) * 100
                return percentage
        return None

    def _handleStdErr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")

        # Forward FFmpeg output
        if self.logging:
            log.error(stderr)

    def _handleStdOut(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")

        # Forward output if any
        if self.logging:
            log.info(stdout)

        # Update progress bar
        for line in stdout.split("\n"):
            if self.total_duration is None:
                self.total_duration = self._parseDuration(line)
            if self.total_duration:
                percentage = self._parseProgress(line, self.total_duration)
                if percentage is not None:
                    self.progress.emit(percentage)

    def _finished(self):
        self.progress.emit(100)
        self.fileFinished.emit()
        log.info("Finished compressing file.")