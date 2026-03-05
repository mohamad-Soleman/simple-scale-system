"""
POS Scale App entry point.
Sets up logging to scale_app.log (next to EXE or script), then runs the Qt application.
"""
import logging
import sys

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from app.config import load_optional_config
from app.ui import MainWindow
from app.ui.styles import BG_MAIN, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY


def setup_logging() -> None:
    """Configure structured logging to scale_app.log in base dir."""
    load_optional_config()
    from app.config import LOG_PATH
    log_path = LOG_PATH
    if hasattr(log_path, "parent"):
        log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(str(log_path), encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    logging.info("=== POS Scale App started ===")


def main() -> int:
    setup_logging()
    app = QApplication(sys.argv)
    # Light palette so message boxes and dialogs have readable text
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(BG_MAIN))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    pal.setColor(QPalette.ColorRole.Base, QColor(BG_CARD))
    pal.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRIMARY))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))
    app.setPalette(pal)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
