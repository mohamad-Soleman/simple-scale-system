"""
Background serial scale reader. Emits weight and status via Qt signals.
Never blocks the UI thread.
"""
import logging
import time
from typing import TYPE_CHECKING

from PyQt6.QtCore import QThread, pyqtSignal

from app.config import BAUD, COM_PORT, load_optional_config
from app.scale.parser import parse_weight_line

if TYPE_CHECKING:
    import serial

logger = logging.getLogger(__name__)


class SerialScaleReader(QThread):
    """Reads weight from scale over serial in a background thread."""
    weight_changed = pyqtSignal(float)
    status_changed = pyqtSignal(str)

    def __init__(self, port: str | None = None, baud: int | None = None) -> None:
        super().__init__()
        load_optional_config()
        self._port = port or COM_PORT
        self._baud = baud or BAUD
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(self) -> None:
        import serial
        while not self._stop_requested:
            try:
                msg = f"Connecting to {self._port} @ {self._baud}..."
                logger.info(msg)
                self.status_changed.emit(msg)
                ser = serial.Serial(port=self._port, baudrate=self._baud, timeout=1.0)
                msg = f"Connected: {self._port}"
                logger.info(msg)
                self.status_changed.emit(msg)
                while not self._stop_requested:
                    raw = ser.readline()
                    if not raw:
                        continue
                    line = raw.decode(errors="ignore").strip()
                    w = parse_weight_line(line)
                    if w is not None:
                        self.weight_changed.emit(w)
            except serial.SerialException as e:
                msg = f"Serial error: {e} (COM port busy? Close other apps using the scale.)"
                logger.error(msg)
                self.status_changed.emit(msg)
                time.sleep(2)
            except Exception:
                logger.exception("Unexpected serial error")
                self.status_changed.emit("Unexpected serial error. Check scale_app.log")
                time.sleep(2)
