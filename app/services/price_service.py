"""Price calculation and currency formatting."""
from decimal import Decimal

from app.config import CURRENCY_SYMBOL


class PriceService:
    """Compute total price and format currency."""

    def __init__(self, currency_symbol: str = CURRENCY_SYMBOL) -> None:
        self._currency = currency_symbol

    def compute_total(self, weight_kg: float, price_per_kg: float) -> Decimal:
        """Total = weight * price_per_kg, rounded to 2 decimal places."""
        return (Decimal(str(weight_kg)) * Decimal(str(price_per_kg))).quantize(Decimal("0.01"))

    def format_currency(self, value: float | Decimal) -> str:
        """Format as e.g. '12.34 ₪'."""
        if isinstance(value, Decimal):
            value = float(value)
        return f"{value:.2f} {self._currency}"
