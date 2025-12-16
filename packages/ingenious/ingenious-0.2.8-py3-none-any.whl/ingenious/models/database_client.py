"""Database client interfaces and types."""

import enum


class DatabaseClientType(enum.Enum):
    """Enumeration of supported database client types.

    Attributes:
        SQLITE: SQLite database client.
        AZURESQL: Azure SQL database client.
        COSMOS: Azure Cosmos DB client.
    """

    SQLITE = "sqlite"
    AZURESQL = "azuresql"
    COSMOS = "cosmos"
