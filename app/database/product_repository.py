"""
SQLite product repository. Creates schema on first run if DB is missing.
"""
import logging
import sqlite3
from pathlib import Path
from typing import Protocol

from app.models import Product

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price_per_kg REAL NOT NULL,
    category TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
"""


class ProductRepositoryProtocol(Protocol):
    """Interface for product repository."""

    def list_active(self) -> list[Product]:
        ...

    def list_all(self) -> list[Product]:
        ...

    def add(self, name: str, price_per_kg: float, category: str | None, is_active: bool) -> int:
        ...

    def update(
        self, id: int, name: str, price_per_kg: float, category: str | None, is_active: bool
    ) -> None:
        ...

    def delete(self, id: int) -> None:
        ...


class SqliteProductRepository:
    """SQLite implementation of product repository."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(SCHEMA_SQL)

    def list_active(self) -> list[Product]:
        """Return all active products, ordered by name."""
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self._db_path)) as conn:
                self._ensure_schema(conn)
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    "SELECT id, name, price_per_kg, category, is_active FROM products WHERE is_active = 1 ORDER BY name"
                )
                return [
                    Product(
                        id=row["id"],
                        name=row["name"],
                        price_per_kg=row["price_per_kg"],
                        category=row["category"],
                        is_active=bool(row["is_active"]),
                    )
                    for row in cur.fetchall()
                ]
        except sqlite3.Error as e:
            logger.exception("Failed to load products: %s", e)
            return []

    def list_all(self) -> list[Product]:
        """Return all products (active and inactive), ordered by name."""
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self._db_path)) as conn:
                self._ensure_schema(conn)
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    "SELECT id, name, price_per_kg, category, is_active FROM products ORDER BY name"
                )
                return [
                    Product(
                        id=row["id"],
                        name=row["name"],
                        price_per_kg=row["price_per_kg"],
                        category=row["category"],
                        is_active=bool(row["is_active"]),
                    )
                    for row in cur.fetchall()
                ]
        except sqlite3.Error as e:
            logger.exception("Failed to list all products: %s", e)
            return []

    def add(self, name: str, price_per_kg: float, category: str | None, is_active: bool) -> int:
        """Insert a product. Returns the new row id."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self._db_path)) as conn:
            self._ensure_schema(conn)
            cur = conn.execute(
                "INSERT INTO products (name, price_per_kg, category, is_active) VALUES (?, ?, ?, ?)",
                (name.strip(), float(price_per_kg), category.strip() if category else None, 1 if is_active else 0),
            )
            conn.commit()
            return cur.lastrowid or 0

    def update(
        self, id: int, name: str, price_per_kg: float, category: str | None, is_active: bool
    ) -> None:
        """Update an existing product by id."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute(
                "UPDATE products SET name=?, price_per_kg=?, category=?, is_active=? WHERE id=?",
                (name.strip(), float(price_per_kg), category.strip() if category else None, 1 if is_active else 0, id),
            )
            conn.commit()

    def delete(self, id: int) -> None:
        """Delete a product by id."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("DELETE FROM products WHERE id=?", (id,))
            conn.commit()
