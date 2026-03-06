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

# Left-to-right mark: keeps value+unit (e.g. "0.092 kg", "100.00 ₪") beside the value, not the key, in RTL
_LTR = "\u200e"

# Key strings (Hebrew label + colon); values built per line so keys and values can be drawn in two aligned columns
_KEY_MOTSAR = "מוצר :"
_KEY_MISHKAL = "משקל :"
_KEY_MECHIR = "מחיר :"
_KEY_SUM = "סכום :"


def _format_label_pairs(
    product_name: str,
    weight_kg: float,
    price_per_kg: float,
    total: float,
    date_time: datetime,
    currency: str = CURRENCY_SYMBOL,
) -> list[tuple[str, str]]:
    """Return (key, value) pairs. Keys align RTL; values align RTL; kg/₪ stay beside numbers via LTR."""
    return [
        (_KEY_MOTSAR, product_name),
        (_KEY_MISHKAL, f"{_LTR}{weight_kg:.3f} kg"),
        (_KEY_MECHIR, f"{_LTR}{price_per_kg:.2f} {currency}"),
        (_KEY_SUM, f"{_LTR}{total:.2f} {currency}"),
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
        pairs = _format_label_pairs(product_name, weight_kg, price_per_kg, total, date_time, CURRENCY_SYMBOL)
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
            gap_px = 8
            margin = LABEL_RTL_MARGIN_PX
            max_key_w = 0
            for key, _ in pairs:
                kw, _ = dc.GetTextExtent(key)
                if kw > max_key_w:
                    max_key_w = kw
            x_key_right = width_px - margin
            x_value_right = x_key_right - max_key_w - gap_px
            total_text_height = line_height * len(pairs)
            y = max(0, (height_px - total_text_height) // 2)
            for key, value in pairs:
                kw, _ = dc.GetTextExtent(key)
                vw, _ = dc.GetTextExtent(value)
                dc.TextOut(x_value_right - vw, y, value)
                dc.TextOut(x_key_right - kw, y, key)
                y += line_height
            dc.EndPage()
            dc.EndDoc()
            logger.info("Printed label to %s", printer_name)
            return f"Printed to {printer_name}"
        except Exception:
            logger.error("Print failed: %s", traceback.format_exc())
            return "Print failed. Check scale_app.log"
