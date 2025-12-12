"""
Cursor class for executing queries and retrieving results.
"""

import logging
from typing import List, Tuple, Any, Optional, TYPE_CHECKING


from .exceptions import APIError, QueryError, ConnectionError
from .models import DataStreamDirectColumnMetadata

if TYPE_CHECKING:
    from .connection import DatastreamDirectConnection


logger = logging.getLogger(__name__)


class DatastreamDirectCursor:
    """
    Cursor for executing SQL queries and retrieving results.

    A cursor provides methods to execute SQL queries against the DataStream Direct
    API and retrieve results. Cursors are created by calling the cursor() method
    on a connection object.

    Attributes:
        connection: The parent connection object
        metadata: Column metadata from the last executed query
        headers: Column headers from the last executed query
        rows: Row data from the last executed query
        is_closed: Whether this cursor has been closed

    Example:
        >>> cursor = connection.cursor()
        >>> cursor.execute("SELECT * FROM well_combined limit 100")
        >>> rows = cursor.fetchall()
        >>> for row in rows:
        ...     print(row)
        >>> cursor.close()
    """

    def __init__(self, connection: "DatastreamDirectConnection") -> None:
        """
        Initialize a cursor.

        Args:
            connection: DatastreamDirectConnection instance
        """
        self.connection = connection
        self._closed = False
        self._query_id: Optional[str] = None
        self._rows: List[Tuple[Any, ...]] = []
        self._headers: List[str] = []
        self._metadata: Optional[List[DataStreamDirectColumnMetadata]] = None

    def execute(self, sql: str) -> None:
        """
        Execute a SQL query.

        Args:
            sql: SQL query string

        Raises:
            QueryError: If query execution fails
            ConnectionError: If connection is closed
        """
        if self._closed:
            raise ConnectionError("Cursor is closed")

        if self.connection.is_closed:
            raise ConnectionError("Connection is closed")

        try:
            logger.debug(f"Executing query: {sql}")
            self._query_id = self.connection.api_client.execute_query(sql)
            self._rows = None
            self._headers = None
            self._metadata = None
            logger.debug(f"Query executed successfully with ID: {self._query_id}")

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise QueryError(f"Failed to execute query: {str(e)}")

    def fetchall(self) -> List[Tuple[Any, ...]]:
        """
        Fetch all results from the last executed query.

        Returns:
            List of tuples containing query results

        Raises:
            QueryError: If no query has been executed or results cannot be retrieved
            ConnectionError: If cursor is closed
        """
        if self._closed:
            raise ConnectionError("Cursor is closed")

        if not self._query_id:
            raise QueryError("No query has been executed")

        if self._rows is not None:
            return self._rows

        try:
            results = self.connection.api_client.get_query_results(self._query_id)
            self._metadata = [
                DataStreamDirectColumnMetadata.from_dict(metadata)
                for metadata in results.results_metadata
            ]

            self._headers = results.headers
            self._rows = results.rows
            return self._rows

        except (QueryError, APIError) as e:
            raise e.with_traceback(None)
        except Exception as e:
            logger.error("Failed to fetch results", exc_info=True)
            raise QueryError("Failed to fetch results") from e

    def close(self) -> None:
        """Close the cursor and clean up resources."""
        if not self._closed:
            self._closed = True
            self._query_id = None
            self._rows = None
            self._headers = None
            self._metadata = None
            logger.debug("Cursor closed")

    @property
    def metadata(self) -> Optional[List[DataStreamDirectColumnMetadata]]:
        """
        Get the metadata of the last executed query.
        """
        return self._metadata

    @property
    def headers(self) -> List[str]:
        """Get the headers of the last executed query."""
        return self._headers

    @property
    def rows(self) -> List[Tuple[Any, ...]]:
        """Get the rows of the last executed query."""
        return self._rows

    @property
    def is_closed(self) -> bool:
        """Check if the cursor is closed."""
        return self._closed
