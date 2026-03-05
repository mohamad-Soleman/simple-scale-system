"""
Touch-friendly numeric keypad dialog for entering price per kg (e.g. Generic Item).
Returns validated float on OK; caller checks accepted() and get_value().
"""
from typing import Final

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui import styles as ui_styles

MAX_VALUE: Final[float] = 9999.99
MIN_BUTTON_HEIGHT: Final[int] = 64


class KeypadDialog(QDialog):
    """Numeric keypad: 0-9, decimal, backspace, clear, OK, Cancel. Returns price on accept."""

    def __init__(self, initial_value: float | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Enter price per kg (₪)")
        self._value: float | None = None
        self._digits: list[str] = []
        self._has_decimal = False
        if initial_value is not None and initial_value >= 0:
            s = f"{initial_value:.2f}".rstrip("0").rstrip(".")
            self._digits = list(s)
            self._has_decimal = "." in s
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(ui_styles.KEYPAD_DIALOG)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        self._display = QLabel(self._display_text())
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self._display.setMinimumHeight(48)
        self._display.setStyleSheet(ui_styles.KEYPAD_DISPLAY)
        layout.addWidget(self._display)
        grid = QGridLayout()
        grid.setSpacing(8)
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            (".", 3, 0), ("0", 3, 1), ("⌫", 3, 2),
        ]
        for label, row, col in buttons:
            btn = self._make_button(label)
            if label == "⌫":
                btn.clicked.connect(self._backspace)
            elif label == ".":
                btn.clicked.connect(self._decimal)
            else:
                btn.clicked.connect(lambda checked=False, c=label: self._digit(c))
            grid.addWidget(btn, row, col)
        clear_btn = self._make_button("Clear")
        clear_btn.clicked.connect(self._clear)
        grid.addWidget(clear_btn, 4, 0)
        cancel_btn = self._make_button("Cancel")
        cancel_btn.clicked.connect(self.reject)
        grid.addWidget(cancel_btn, 4, 1)
        ok_btn = self._make_button("OK", primary=True)
        ok_btn.clicked.connect(self._ok)
        grid.addWidget(ok_btn, 4, 2)
        layout.addLayout(grid)
        self._update_ok_state()

    def _make_button(self, label: str, primary: bool = False) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(MIN_BUTTON_HEIGHT)
        btn.setStyleSheet(ui_styles.KEYPAD_BTN_PRIMARY if primary else ui_styles.KEYPAD_BTN)
        return btn

    def _display_text(self) -> str:
        if not self._digits:
            return "0.00"
        return "".join(self._digits)

    def _digit(self, c: str) -> None:
        if c == "0" and not self._digits:
            return
        s = "".join(self._digits)
        if "." in s:
            after = s.split(".")[1]
            if len(after) >= 2:
                return
        self._digits.append(c)
        self._refresh_display()
        self._update_ok_state()

    def _decimal(self) -> None:
        if self._has_decimal:
            return
        if not self._digits:
            self._digits.append("0")
        self._digits.append(".")
        self._has_decimal = True
        self._refresh_display()
        self._update_ok_state()

    def _backspace(self) -> None:
        if not self._digits:
            return
        removed = self._digits.pop()
        if removed == ".":
            self._has_decimal = False
        self._refresh_display()
        self._update_ok_state()

    def _clear(self) -> None:
        self._digits.clear()
        self._has_decimal = False
        self._refresh_display()
        self._update_ok_state()

    def _refresh_display(self) -> None:
        self._display.setText(self._display_text())

    def _valid(self) -> bool:
        if not self._digits:
            return False
        s = "".join(self._digits)
        if s in (".", ""):
            return False
        if s.endswith("."):
            s += "0"
        try:
            val = float(s)
        except ValueError:
            return False
        return 0 <= val <= MAX_VALUE

    def _update_ok_state(self) -> None:
        for child in self.findChildren(QPushButton):
            if child.text() == "OK":
                child.setEnabled(self._valid())
                break

    def _ok(self) -> None:
        if not self._valid():
            return
        s = "".join(self._digits)
        if s.endswith("."):
            s += "00"
        elif "." not in s:
            s += ".00"
        else:
            a, _, b = s.partition(".")
            b = (b + "00")[:2]
            s = f"{a}.{b}"
        try:
            val = float(s)
            if val < 0 or val > MAX_VALUE:
                return
            self._value = val
            self.accept()
        except ValueError:
            pass

    def get_value(self) -> float | None:
        """Return entered price per kg after accept(); None if cancelled or invalid."""
        return self._value
