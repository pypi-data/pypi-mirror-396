"""SQLite database adapter for Ingenious chat history.

Provides lightweight local repository implementation for storing chat history,
threads, messages, and metadata using SQLite database.
"""

import os
import sqlite3
from typing import Any

from ingenious.config import IngeniousSettings

# Future import placeholders for advanced error handling
# from ingenious.core.error_handling import (
#     database_operation,
#     operation_context,
#     with_correlation_id,
# )
from ingenious.core.structured_logging import get_logger
from ingenious.db.base_sql import BaseSQLRepository
from ingenious.db.chat_history_models import User
from ingenious.db.connection_pool import ConnectionPool, SQLiteConnectionFactory
from ingenious.db.query_builder import QueryBuilder, SQLiteDialect
from ingenious.errors import (
    DatabaseQueryError,
)

logger = get_logger(__name__)


class sqlite_ChatHistoryRepository(BaseSQLRepository):
    """SQLite implementation of chat history repository.

    Provides lightweight local storage for chat history, threads, and messages
    using SQLite database with INSERT OR REPLACE operations.
    """

    def __init__(self, config: IngeniousSettings) -> None:
        """Initialize SQLite chat history repository with database path and connection pool.

        Args:
            config: Ingenious settings containing database path and configuration.
        """
        self.db_path = config.chat_history.database_path
        # Check if the directory exists, if not, create it
        db_dir_check = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir_check):
            os.makedirs(db_dir_check)

        # Initialize connection pool
        pool_size = getattr(config.chat_history, "connection_pool_size", 8)
        connection_factory = SQLiteConnectionFactory(self.db_path)
        self.pool = ConnectionPool(connection_factory, pool_size=pool_size)

        # Initialize query builder with SQLite dialect
        query_builder = QueryBuilder(SQLiteDialect())

        # Call parent constructor which will call _init_connection and _create_tables
        super().__init__(config, query_builder)

    def __del__(self) -> None:
        """Destructor to ensure connections are properly closed."""
        try:
            self.close()
        except Exception:
            pass  # nosec B110 - intentional cleanup, ignoring errors in destructor

    def close(self) -> None:
        """Close all connections in the pool."""
        if hasattr(self, "pool"):
            self.pool.close_all()

    def _init_connection(self) -> None:
        """Connection already initialized in __init__ via connection pool."""
        pass

    def _execute_sql(
        self, sql: str, params: list[Any] | None = None, expect_results: bool = True
    ) -> Any:
        if params is None:
            params = []
        try:
            with self.pool.get_connection() as connection:
                cursor = connection.cursor()
                logger.debug(
                    "Executing SQL query",
                    sql_preview=sql[:100] + "..." if len(sql) > 100 else sql,
                    param_count=len(params) if params else 0,
                    operation="sql_execute",
                )

                if expect_results:
                    res = cursor.execute(sql, params)
                    rows = res.fetchall()
                    result = [dict(row) for row in rows]
                    return result
                else:
                    connection.execute(sql, params)
                    connection.commit()

        except sqlite3.Error as e:
            logger.error(
                "SQLite error during query execution",
                error=str(e),
                sql_preview=sql[:100] + "..." if len(sql) > 100 else sql,
                param_count=len(params) if params else 0,
                operation="sql_execute",
            )
            raise DatabaseQueryError(
                "SQLite query execution failed",
                context={
                    "query_preview": sql[:100] + "..." if len(sql) > 100 else sql,
                    "param_count": len(params) if params else 0,
                    "expect_results": expect_results,
                },
                cause=e,
            ) from e

    def execute_sql(
        self, sql: str, params: list[Any] | None = None, expect_results: bool = True
    ) -> Any:
        """Legacy method for backward compatibility."""
        return self._execute_sql(sql, params, expect_results)

    def _create_table(self) -> None:
        """Legacy method for backward compatibility. Tables are now created via base class."""
        pass

    async def _get_user_by_id(self, user_id: str) -> User | None:
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """SELECT id, identifier, metadata, createdAt FROM users WHERE id = ?""",
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return User(id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3])
            return None

    async def update_memory(self) -> None:
        """Update chat history summary to keep only the latest record per thread.

        Creates a temporary table with the latest record per thread, clears the
        summary table, and re-inserts only the latest records.
        """
        with self.pool.get_connection() as connection:
            cursor = connection.cursor()

            # Create a temporary table for the latest records
            cursor.execute("""
                CREATE TEMP TABLE latest_chat_history AS
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM (
                    SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                           content_filter_results, tool_calls, tool_call_id, tool_call_function,
                           ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY timestamp DESC) AS row_num
                    FROM chat_history_summary
                ) AS LatestRecords
                WHERE row_num = 1
            """)

            # Clear the original table
            cursor.execute("DELETE FROM chat_history_summary")

            # Insert the latest records back into the original table
            cursor.execute("""
                INSERT INTO chat_history_summary (user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                                                  content_filter_results, tool_calls, tool_call_id, tool_call_function)
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function
                FROM latest_chat_history
            """)

            # Drop the temporary table
            cursor.execute("DROP TABLE latest_chat_history")

            cursor.close()
