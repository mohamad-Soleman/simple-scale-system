"""
Windows default printer implementation using pywin32 GDI.
Formats label in Hebrew, RTL: מוצר, מחיר, סכום. No timestamp.
"""
import logging
import traceback
from datetime import datetime

from app.config import (
    CURRENCY_SYMBOL,
    LABEL_FONT_HEIGHT,
    LABEL_FONT_NAME,
    LABEL_FONT_WEIGHT,
    LABEL_RTL_MARGIN_PX,
)

logger = logging.getLogger(__name__)

# Hebrew units for label (no symbols); space before unit so it doesn't run into the number
_UNIT_KG_HE = " קגרם"
_UNIT_SHEKEL_HE = " שח"


def _format_label_lines(
    product_name: str,
    weight_kg: float,
    price_per_kg: float,
    total: float,
    date_time: datetime,
    currency: str = CURRENCY_SYMBOL,
) -> list[str]:
    """One full line per row, RTL. Format: key : value; units in Hebrew (קגרם, שח)."""
    return [
        f"מוצר : {product_name}",
        f"משקל : {weight_kg:.3f}{_UNIT_KG_HE}",
        f"מחיר : {price_per_kg:.2f}{_UNIT_SHEKEL_HE}",
        f"סכום : {total:.2f}{_UNIT_SHEKEL_HE}",
    ]


class WindowsLabelPrinter:
    """Print labels to Windows default printer. Never raises; returns error string on failure."""

    def __init__(
        self,
        font_name: str = LABEL_FONT_NAME,
        font_height: int = LABEL_FONT_HEIGHT,
        font_weight: int = LABEL_FONT_WEIGHT,
    ) -> None:
        self._font_name = font_name
        self._font_height = font_height
        self._font_weight = font_weight

    def print_label(
        self,
        product_name: str,
        weight_kg: float,
        price_per_kg: float,
        total: float,
        date_time: datetime,
    ) -> str:
        try:
            import win32con
            import win32print
            import win32ui
        except Exception as e:
            msg = f"pywin32 is missing or broken: {e}. Install: pip install pywin32"
            logger.error(msg)
            return msg
        lines = _format_label_lines(product_name, weight_kg, price_per_kg, total, date_time, CURRENCY_SYMBOL)
        try:
            printer_name = win32print.GetDefaultPrinter()
            dc = win32ui.CreateDC()
            dc.CreatePrinterDC(printer_name)
            width_px = dc.GetDeviceCaps(win32con.HORZRES)
            height_px = dc.GetDeviceCaps(win32con.VERTRES)
            dc.StartDoc("Scale Label")
            dc.StartPage()
            font = win32ui.CreateFont({
                "name": self._font_name,
                "height": self._font_height,
                "weight": self._font_weight,
            })
            dc.SelectObject(font)
            line_height = dc.GetTextExtent("X")[1] + 4
            margin = LABEL_RTL_MARGIN_PX
            total_text_height = line_height * len(lines)
            y = max(0, (height_px - total_text_height) // 2)
            for line in lines:
                tw, _ = dc.GetTextExtent(line)
                x = max(0, width_px - tw - margin)
                dc.TextOut(x, y, line)
                y += line_height
            dc.EndPage()
            dc.EndDoc()
            logger.info("Printed label to %s", printer_name)
            return f"Printed to {printer_name}"
        except Exception:
            logger.error("Print failed: %s", traceback.format_exc())
            return "Print failed. Check scale_app.log"
