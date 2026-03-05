"""Printer abstraction: label printing returns success or error message."""
from datetime import datetime
from typing import Protocol


class LabelPrinterProtocol(Protocol):
    """Interface for printing a label."""

    def print_label(
        self,
        product_name: str,
        weight_kg: float,
        price_per_kg: float,
        total: float,
        date_time: datetime,
    ) -> str:
        """Print label. Returns success message or error string. Never raises."""
        ...
