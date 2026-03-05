"""
Dialog to add or edit a product: name, price per kg, category, is_active.
Price can be entered via keypad for touch-friendly use.
"""
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models import Product
from app.ui import styles as ui_styles
from app.ui.keypad_dialog import KeypadDialog


class ProductFormDialog(QDialog):
    """Add or edit product. get_product() returns (name, price_per_kg, category, is_active) on accept."""

    def __init__(
        self,
        parent: QWidget | None = None,
        product: Product | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("ערוך מוצר" if product else "הוסף מוצר")
        self._product = product
        self._build_ui()
        if product:
            self._name_edit.setText(product.name)
            self._price_edit.setText(f"{product.price_per_kg:.2f}")
            self._category_edit.setText(product.category or "")
            self._active_check.setChecked(product.is_active)

    def _build_ui(self) -> None:
        self.setStyleSheet(ui_styles.FORM_DIALOG)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("שם המוצר")
        self._name_edit.setMinimumHeight(44)
        form.addRow("שם:", self._name_edit)
        self._price_edit = QLineEdit()
        self._price_edit.setPlaceholderText("מחיר לק\"ג (₪)")
        self._price_edit.setMinimumHeight(44)
        self._price_edit.setReadOnly(True)
        _price_btn = QPushButton("הזן מחיר")
        _price_btn.setMinimumHeight(44)
        _price_btn.clicked.connect(self._open_keypad)
        price_row = QHBoxLayout()
        price_row.addWidget(self._price_edit)
        price_row.addWidget(_price_btn)
        form.addRow("מחיר לק\"ג (₪):", price_row)
        self._category_edit = QLineEdit()
        self._category_edit.setPlaceholderText("קטגוריה (אופציונלי)")
        self._category_edit.setMinimumHeight(44)
        form.addRow("קטגוריה:", self._category_edit)
        self._active_check = QCheckBox("פעיל (מופיע במסך השקילה)")
        self._active_check.setChecked(True)
        form.addRow("", self._active_check)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _open_keypad(self) -> None:
        try:
            text = self._price_edit.text().strip()
            initial = float(text) if text else None
        except ValueError:
            initial = None
        dlg = KeypadDialog(initial_value=initial, parent=self)
        dlg.setMinimumWidth(320)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            val = dlg.get_value()
            if val is not None:
                self._price_edit.setText(f"{val:.2f}")

    def _accept_if_valid(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "שגיאה", "נא להזין שם מוצר.")
            return
        try:
            price = float(self._price_edit.text().strip().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "שגיאה", "נא להזין מחיר תקין.")
            return
        if price < 0:
            QMessageBox.warning(self, "שגיאה", "המחיר לא יכול להיות שלילי.")
            return
        category = self._category_edit.text().strip() or None
        is_active = self._active_check.isChecked()
        self._result = (name, price, category, is_active)
        self.accept()

    def get_product_data(self) -> Optional[tuple[str, float, str | None, bool]]:
        """After accept(), returns (name, price_per_kg, category, is_active)."""
        return getattr(self, "_result", None)
