"""Database access layer."""
from app.database.product_repository import ProductRepositoryProtocol, SqliteProductRepository

__all__ = ["ProductRepositoryProtocol", "SqliteProductRepository"]
