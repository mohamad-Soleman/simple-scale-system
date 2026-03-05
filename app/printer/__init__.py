"""Label printer abstraction and Windows implementation."""
from app.printer.interface import LabelPrinterProtocol
from app.printer.windows_printer import WindowsLabelPrinter

__all__ = ["LabelPrinterProtocol", "WindowsLabelPrinter"]
