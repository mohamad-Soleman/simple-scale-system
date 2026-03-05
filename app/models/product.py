"""Product model for DB and UI."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """Product with name, price per kg, optional category, and active flag."""
    id: int
    name: str
    price_per_kg: float
    category: Optional[str]
    is_active: bool

    def __post_init__(self) -> None:
        if isinstance(self.is_active, int):
            self.is_active = bool(self.is_active)
