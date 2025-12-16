"""Database-agnostic SQL query builder with dialect support.

This module provides SQL query generation for multiple database backends
through a dialect pattern, supporting SQLite and Azure SQL.

The module has been refactored into a package structure for better maintainability.
All public APIs remain unchanged for backward compatibility.
"""

from .azuresql import AzureSQLDialect
from .base import Dialect
from .builder import QueryBuilder
from .sqlite import SQLiteDialect

__all__ = [
    "Dialect",
    "SQLiteDialect",
    "AzureSQLDialect",
    "QueryBuilder",
]
