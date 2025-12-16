"""Azure SQL database adapter for Ingenious chat history.

Provides repository implementation for storing chat history, threads,
messages, and metadata in Azure SQL Database using pyodbc.
"""

import json
from typing import Any

import pyodbc

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
from ingenious.db.query_builder import AzureSQLDialect, QueryBuilder
from ingenious.errors import (
    DatabaseQueryError,
)

logger = get_logger(__name__)


class azuresql_ChatHistoryRepository(BaseSQLRepository):
    """Azure SQL implementation of chat history repository.

    Stores chat history, threads, messages, and metadata in Azure SQL Database
    using pyodbc with MERGE operations for upsert functionality.
    """

    def __init__(self, config: IngeniousSettings) -> None:
        """Initialize Azure SQL chat history repository with connection configuration.

        Args:
            config: Ingenious settings containing Azure SQL connection configuration.

        Raises:
            ValueError: If neither azure_sql_services nor chat_history connection string is configured.
        """
        # Try to get connection string from azure_sql_services first, then fallback to chat_history
        self.connection_string = None
        if config.azure_sql_services and config.azure_sql_services.database_connection_string:
            self.connection_string = config.azure_sql_services.database_connection_string
        elif config.chat_history.database_connection_string:
            self.connection_string = config.chat_history.database_connection_string

        if not self.connection_string:
            raise ValueError(
                "Azure SQL connection string is required for azuresql chat history repository. "
                "Please set either INGENIOUS_AZURE_SQL_SERVICES__CONNECTION_STRING or "
                "INGENIOUS_CHAT_HISTORY__DATABASE_CONNECTION_STRING"
            )

        # Initialize query builder with Azure SQL dialect
        query_builder = QueryBuilder(AzureSQLDialect())

        # Call parent constructor which will call _init_connection and _create_tables
        super().__init__(config, query_builder)

    def _init_connection(self) -> None:
        """Initialize Azure SQL connection with retry logic."""
        import time

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting Azure SQL connection (attempt {attempt + 1}/{max_retries})"
                )
                self.connection = pyodbc.connect(self.connection_string)
                self.connection.autocommit = True
                logger.info("Azure SQL connection established successfully")
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("All connection attempts failed")
                    raise

    def _execute_sql(
        self, sql: str, params: list[Any] | None = None, expect_results: bool = True
    ) -> Any:
        """Execute SQL with Azure SQL connection handling."""
        if params is None:
            params = []
        cursor = None
        try:
            cursor = self.connection.cursor()

            if expect_results:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                # Convert to list of dictionaries
                columns = [column[0] for column in cursor.description]
                result = [dict(zip(columns, row)) for row in rows]
                return result
            else:
                cursor.execute(sql, params)
                self.connection.commit()

        except Exception as e:
            logger.error(
                "SQL execution failed",
                error=str(e),
                sql_query=sql[:100] + "..." if len(sql) > 100 else sql,
                param_count=len(params) if params else 0,
                operation="sql_execute",
            )
            raise DatabaseQueryError(
                "SQL query execution failed",
                context={
                    "query_preview": sql[:100] + "..." if len(sql) > 100 else sql,
                    "param_count": len(params) if params else 0,
                    "expect_results": expect_results,
                },
                cause=e,
            ) from e

        finally:
            if cursor:
                cursor.close()

    def execute_sql(
        self, sql: str, params: list[Any] | None = None, expect_results: bool = True
    ) -> Any:
        """Legacy method for backward compatibility."""
        if params is None:
            params = []
        return self._execute_sql(sql, params, expect_results)

    # Removed empty _create_tables override - using base class implementation

    async def _get_user_by_id(self, user_id: str) -> User | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT id, identifier, metadata, createdAt FROM users WHERE id = ?""",
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return User(id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3])
        return None

    def _parse_json_field(self, value: Any, default: Any = None) -> Any:
        """Parse a JSON field, returning default if parsing fails.

        Args:
            value: Value to parse (may be string or already parsed).
            default: Default value to return on parse failure.

        Returns:
            Parsed value or default.
        """
        if not isinstance(value, str):
            return value if value is not None else default
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default if default is not None else {}

    async def update_memory(self) -> None:
        """Update the chat history summary table to retain only the latest record per thread.

        Uses a temporary table to identify the most recent record for each thread by timestamp,
        then clears and repopulates the chat_history_summary table with only these latest records.
        """
        cursor = self.connection.cursor()

        # Create a temporary table for the latest records
        cursor.execute("""
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            INTO #latest_chat_history
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
            FROM #latest_chat_history
        """)

        # Drop the temporary table
        cursor.execute("DROP TABLE #latest_chat_history")
        cursor.close()
