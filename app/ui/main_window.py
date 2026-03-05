"""
Main window: live weight, product grid, selected product + price/kg + total,
Generic Item with keypad, Print button, full-screen toggle.
"""
import logging
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import DB_PATH, load_optional_config
from app.database import SqliteProductRepository
from app.models import Product
from app.printer import WindowsLabelPrinter
from app.scale import SerialScaleReader
from app.services import PriceService
from app.ui.keypad_dialog import KeypadDialog
from app.ui.products_management_tab import ProductsManagementTab
from app.ui import styles as ui_styles

logger = logging.getLogger(__name__)

GENERIC_ITEM_NAME = "פריט כללי"


class MainWindow(QMainWindow):
    """POS scale main window: weight, products, print."""

    def __init__(self) -> None:
        super().__init__()
        load_optional_config()
        self.setWindowTitle("POS Scale — Butcher Shop")
        self.setMinimumSize(900, 560)
        self._price_service = PriceService()
        self._product_repo = SqliteProductRepository(DB_PATH)
        self._printer = WindowsLabelPrinter()
        self._scale_reader: Optional[SerialScaleReader] = None
        self._current_weight: Optional[float] = None
        self._selected_product: Optional[Product] = None
        self._generic_price_per_kg: Optional[float] = None
        self._build_ui()
        self._load_products()
        self._start_scale()
        self._refresh_selection_display()
        self._update_print_enabled()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setStyleSheet(ui_styles.MAIN_WINDOW)
        self.setCentralWidget(central)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        tabs = QTabWidget()
        tabs.setStyleSheet(ui_styles.MAIN_WINDOW)
        weighing_tab = QWidget()
        root = QVBoxLayout(weighing_tab)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(16)
        # Weight (largest)
        self._weight_label = QLabel("0.000 kg")
        self._weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._weight_label.setStyleSheet(ui_styles.WEIGHT_LABEL)
        self._weight_label.setFont(QFont("Arial", 72, QFont.Weight.Bold))
        root.addWidget(self._weight_label, stretch=2)
        # Status
        self._status_label = QLabel("Starting...")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(ui_styles.STATUS_LABEL)
        root.addWidget(self._status_label, stretch=0)
        # Selected product block (centered for Hebrew names and prices)
        sel_w = QWidget()
        sel_layout = QVBoxLayout(sel_w)
        sel_layout.setSpacing(4)
        sel_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self._selected_name_label = QLabel("—")
        self._selected_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._selected_name_label.setStyleSheet(ui_styles.SELECTED_NAME)
        self._selected_price_kg_label = QLabel("— ₪/kg")
        self._selected_price_kg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._selected_price_kg_label.setStyleSheet(ui_styles.SELECTED_PRICE_KG)
        self._selected_total_label = QLabel("— ₪")
        self._selected_total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._selected_total_label.setStyleSheet(ui_styles.SELECTED_TOTAL)
        sel_layout.addWidget(self._selected_name_label)
        sel_layout.addWidget(self._selected_price_kg_label)
        sel_layout.addWidget(self._selected_total_label)
        self._generic_price_btn = QPushButton("הגדר מחיר לק\"ג (פריט כללי)")
        self._generic_price_btn.setMinimumHeight(44)
        self._generic_price_btn.setStyleSheet(ui_styles.BTN_SECONDARY)
        self._generic_price_btn.clicked.connect(self._open_keypad_for_generic)
        self._generic_price_btn.hide()
        sel_layout.addWidget(self._generic_price_btn)
        root.addWidget(sel_w, stretch=0)
        # Product grid (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        grid_container = QWidget()
        self._grid_layout = QGridLayout(grid_container)
        self._grid_layout.setSpacing(12)
        scroll.setWidget(grid_container)
        root.addWidget(scroll, stretch=4)
        # Print + fullscreen row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        fullscreen_btn = QPushButton("Full screen (F11)")
        fullscreen_btn.setMinimumHeight(44)
        fullscreen_btn.setStyleSheet(ui_styles.BTN_SECONDARY)
        fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        self._print_btn = QPushButton("Print label")
        self._print_btn.setMinimumHeight(52)
        self._print_btn.setStyleSheet(ui_styles.BTN_PRIMARY)
        self._print_btn.clicked.connect(self._print_label)
        btn_row.addWidget(fullscreen_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self._print_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)
        tabs.addTab(weighing_tab, "שקילה")
        management_tab = ProductsManagementTab(
            get_repo=lambda: self._product_repo,
            on_products_changed=self._reload_weighing_products,
        )
        tabs.addTab(management_tab, "ניהול מוצרים")
        central_layout.addWidget(tabs)
        logger.info("Main window ready")

    def _reload_weighing_products(self) -> None:
        """Reload product grid (e.g. after add/edit/delete in management tab)."""
        self._load_products()

    def _load_products(self) -> None:
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        products = self._product_repo.list_active()
        row, col = 0, 0
        cols = 3
        for p in products:
            btn = QPushButton(p.name)
            btn.setMinimumHeight(56)
            btn.setStyleSheet(ui_styles.BTN_PRODUCT)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, prod=p: self._select_product(prod))
            self._grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        generic_btn = QPushButton(GENERIC_ITEM_NAME)
        generic_btn.setMinimumHeight(56)
        generic_btn.setStyleSheet(ui_styles.BTN_GENERIC)
        generic_btn.setCheckable(True)
        generic_btn.clicked.connect(self._select_generic_item)
        self._grid_layout.addWidget(generic_btn, row, col)

    def _start_scale(self) -> None:
        self._scale_reader = SerialScaleReader()
        self._scale_reader.weight_changed.connect(self._on_weight)
        self._scale_reader.status_changed.connect(self._on_status)
        self._scale_reader.start()

    def _on_weight(self, w: float) -> None:
        self._current_weight = w
        self._weight_label.setText(f"{w:.3f} kg")
        self._refresh_selection_display()
        self._update_print_enabled()

    def _on_status(self, s: str) -> None:
        self._status_label.setText(s)

    def _select_product(self, product: Product) -> None:
        self._selected_product = product
        self._generic_price_per_kg = None
        for btn in self._grid_layout.parent().findChildren(QPushButton):
            if btn.isCheckable():
                btn.setChecked(btn.text() == product.name)
        self._generic_price_btn.hide()
        self._refresh_selection_display()
        self._update_print_enabled()

    def _select_generic_item(self) -> None:
        self._selected_product = None
        for btn in self._grid_layout.parent().findChildren(QPushButton):
            if btn.isCheckable():
                btn.setChecked(btn.text() == GENERIC_ITEM_NAME)
        self._generic_price_btn.show()
        self._refresh_selection_display()
        self._update_print_enabled()

    def _open_keypad_for_generic(self) -> None:
        dlg = KeypadDialog(initial_value=self._generic_price_per_kg, parent=self)
        dlg.setMinimumWidth(320)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            val = dlg.get_value()
            if val is not None:
                self._generic_price_per_kg = val
                self._refresh_selection_display()
                self._update_print_enabled()

    def _refresh_selection_display(self) -> None:
        if self._selected_product is not None:
            self._selected_name_label.setText(self._selected_product.name)
            self._selected_price_kg_label.setText(
                f"{self._selected_product.price_per_kg:.2f} ₪/kg"
            )
            if self._current_weight is not None:
                total = self._price_service.compute_total(
                    self._current_weight, self._selected_product.price_per_kg
                )
                self._selected_total_label.setText(self._price_service.format_currency(total))
            else:
                self._selected_total_label.setText("— ₪")
            return
        if self._generic_price_btn.isVisible():
            self._selected_name_label.setText(GENERIC_ITEM_NAME)
            if self._generic_price_per_kg is not None:
                self._selected_price_kg_label.setText(f"{self._generic_price_per_kg:.2f} ₪/kg")
                if self._current_weight is not None:
                    total = self._price_service.compute_total(
                        self._current_weight, self._generic_price_per_kg
                    )
                    self._selected_total_label.setText(self._price_service.format_currency(total))
                else:
                    self._selected_total_label.setText("— ₪")
            else:
                self._selected_price_kg_label.setText("הגדר מחיר (לחץ על הכפתור למטה)")
                self._selected_total_label.setText("— ₪")
            return
        self._selected_name_label.setText("—")
        self._selected_price_kg_label.setText("— ₪/kg")
        self._selected_total_label.setText("— ₪")

    def _update_print_enabled(self) -> None:
        has_product = self._selected_product is not None or (
            self._generic_price_btn.isVisible() and self._generic_price_per_kg is not None
        )
        self._print_btn.setEnabled(
            bool(has_product and self._current_weight is not None)
        )

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F11:
            self._toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def _print_label(self) -> None:
        if self._current_weight is None:
            self._status_label.setText("No weight yet.")
            return
        name: str
        price_per_kg: float
        if self._selected_product is not None:
            name = self._selected_product.name
            price_per_kg = self._selected_product.price_per_kg
        elif self._generic_price_per_kg is not None:
            name = GENERIC_ITEM_NAME
            price_per_kg = self._generic_price_per_kg
        else:
            self._status_label.setText("בחר מוצר או הגדר מחיר לפריט כללי.")
            return
        total = float(
            self._price_service.compute_total(self._current_weight, price_per_kg)
        )
        self._status_label.setText("Printing...")
        try:
            result = self._printer.print_label(
                product_name=name,
                weight_kg=self._current_weight,
                price_per_kg=price_per_kg,
                total=total,
                date_time=datetime.now(),
            )
            self._status_label.setText(result)
            if "failed" in result.lower() or "error" in result.lower():
                QMessageBox.warning(self, "Print", result)
        except Exception:
            logger.exception("Print button handler error")
            self._status_label.setText("Print failed. Check scale_app.log")
            QMessageBox.warning(self, "Print", "Print failed. Check scale_app.log")

    def closeEvent(self, event) -> None:
        if self._scale_reader is not None:
            self._scale_reader.request_stop()
        super().closeEvent(event)
