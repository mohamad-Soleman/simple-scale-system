"""
Tab widget for managing products: list all, add, edit, delete.
"""
import logging
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models import Product
from app.ui import styles as ui_styles
from app.ui.product_form_dialog import ProductFormDialog

logger = logging.getLogger(__name__)

COL_ID, COL_NAME, COL_PRICE, COL_CATEGORY, COL_ACTIVE = 0, 1, 2, 3, 4


class ProductsManagementTab(QWidget):
    """Table of all products with Add, Edit, Delete. on_products_changed() called after any change."""

    def __init__(
        self,
        get_repo,
        on_products_changed: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._get_repo = get_repo
        self._on_products_changed = on_products_changed or (lambda: None)
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["#", "שם", "מחיר לק\"ג (₪)", "קטגוריה", "פעיל"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setStyleSheet(ui_styles.TABLE_STYLE)
        self._table.setMinimumHeight(300)
        layout.addWidget(self._table)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        add_btn = QPushButton("הוסף מוצר")
        add_btn.setMinimumHeight(56)
        add_btn.setMinimumWidth(140)
        add_btn.setStyleSheet(ui_styles.BTN_PRIMARY)
        add_btn.clicked.connect(self._add_product)
        edit_btn = QPushButton("ערוך")
        edit_btn.setMinimumHeight(56)
        edit_btn.setMinimumWidth(120)
        edit_btn.setStyleSheet(ui_styles.BTN_SECONDARY)
        edit_btn.clicked.connect(self._edit_product)
        delete_btn = QPushButton("מחק")
        delete_btn.setMinimumHeight(56)
        delete_btn.setMinimumWidth(120)
        delete_btn.setStyleSheet(ui_styles.BTN_DANGER)
        delete_btn.clicked.connect(self._delete_product)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

    def _refresh_table(self) -> None:
        repo = self._get_repo()
        products = repo.list_all()
        self._table.setRowCount(len(products))
        for row, p in enumerate(products):
            self._table.setItem(row, COL_ID, QTableWidgetItem(str(p.id)))
            self._table.setItem(row, COL_NAME, QTableWidgetItem(p.name))
            self._table.setItem(row, COL_PRICE, QTableWidgetItem(f"{p.price_per_kg:.2f}"))
            self._table.setItem(row, COL_CATEGORY, QTableWidgetItem(p.category or ""))
            self._table.setItem(row, COL_ACTIVE, QTableWidgetItem("כן" if p.is_active else "לא"))
        self._table.resizeRowsToContents()

    def _selected_product(self) -> Product | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        id_item = self._table.item(row, COL_ID)
        name_item = self._table.item(row, COL_NAME)
        price_item = self._table.item(row, COL_PRICE)
        cat_item = self._table.item(row, COL_CATEGORY)
        active_item = self._table.item(row, COL_ACTIVE)
        if not all([id_item, name_item, price_item]):
            return None
        try:
            return Product(
                id=int(id_item.text()),
                name=name_item.text(),
                price_per_kg=float(price_item.text().replace(",", ".")),
                category=cat_item.text().strip() or None if cat_item else None,
                is_active=active_item.text() == "כן" if active_item else True,
            )
        except ValueError:
            return None

    def _add_product(self) -> None:
        dlg = ProductFormDialog(parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_product_data()
        if not data:
            return
        name, price_per_kg, category, is_active = data
        try:
            repo = self._get_repo()
            repo.add(name, price_per_kg, category, is_active)
            self._refresh_table()
            self._on_products_changed()
        except Exception as e:
            logger.exception("Failed to add product: %s", e)
            QMessageBox.critical(self, "שגיאה", f"לא ניתן להוסיף מוצר: {e}")

    def _edit_product(self) -> None:
        product = self._selected_product()
        if not product:
            QMessageBox.warning(self, "בחירה", "נא לבחור שורה לעריכה.")
            return
        dlg = ProductFormDialog(parent=self, product=product)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_product_data()
        if not data:
            return
        name, price_per_kg, category, is_active = data
        try:
            repo = self._get_repo()
            repo.update(product.id, name, price_per_kg, category, is_active)
            self._refresh_table()
            self._on_products_changed()
        except Exception as e:
            logger.exception("Failed to update product: %s", e)
            QMessageBox.critical(self, "שגיאה", f"לא ניתן לעדכן מוצר: {e}")

    def _delete_product(self) -> None:
        product = self._selected_product()
        if not product:
            QMessageBox.warning(self, "בחירה", "נא לבחור שורה למחיקה.")
            return
        ok = QMessageBox.question(
            self,
            "מחיקת מוצר",
            f"למחוק את \"{product.name}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ok != QMessageBox.StandardButton.Yes:
            return
        try:
            repo = self._get_repo()
            repo.delete(product.id)
            self._refresh_table()
            self._on_products_changed()
        except Exception as e:
            logger.exception("Failed to delete product: %s", e)
            QMessageBox.critical(self, "שגיאה", f"לא ניתן למחוק מוצר: {e}")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._refresh_table()
