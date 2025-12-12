"""Tests for cursor module."""

import pytest
from unittest.mock import Mock

from datastream_direct.cursor import DatastreamDirectCursor
from datastream_direct.exceptions import QueryError, ConnectionError


class TestDatastreamDirectCursor:
    """Test cases for DatastreamDirectCursor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_connection.is_closed = False
        self.mock_api_client = Mock()
        self.mock_connection.api_client = self.mock_api_client

        self.cursor = DatastreamDirectCursor(self.mock_connection)

    def test_cursor_initialization(self):
        """Test cursor initialization."""
        assert self.cursor.connection == self.mock_connection
        assert not self.cursor.is_closed
        assert self.cursor._query_id is None
        assert self.cursor._metadata is None

    def test_execute_success(self):
        """Test successful query execution."""
        self.mock_api_client.execute_query.return_value = "query_123"

        self.cursor.execute("SELECT * FROM users")

        assert self.cursor._query_id == "query_123"
        self.mock_api_client.execute_query.assert_called_once_with(
            "SELECT * FROM users"
        )

    def test_execute_closed_cursor(self):
        """Test execute on closed cursor."""
        self.cursor.close()

        with pytest.raises(ConnectionError, match="Cursor is closed"):
            self.cursor.execute("SELECT * FROM users")

    def test_execute_closed_connection(self):
        """Test execute with closed connection."""
        self.mock_connection.is_closed = True

        with pytest.raises(ConnectionError, match="Connection is closed"):
            self.cursor.execute("SELECT * FROM users")

    def test_execute_query_error(self):
        """Test execute with query error."""
        self.mock_api_client.execute_query.side_effect = QueryError("SQL syntax error")

        with pytest.raises(QueryError, match="Failed to execute query"):
            self.cursor.execute("INVALID SQL")

    def test_fetchall_no_query(self):
        """Test fetchall without executed query."""
        with pytest.raises(QueryError, match="No query has been executed"):
            self.cursor.fetchall()

    def test_fetchall_closed_cursor(self):
        """Test fetchall on closed cursor."""
        self.cursor.close()

        with pytest.raises(ConnectionError, match="Cursor is closed"):
            self.cursor.fetchall()

    def test_close(self):
        """Test cursor close."""
        self.cursor._query_id = "query_123"
        self.cursor._last_result = [(1, "test")]
        self.cursor._metadata = []

        self.cursor.close()

        assert self.cursor.is_closed
        assert self.cursor._query_id is None
        assert self.cursor._metadata is None

    def test_properties(self):
        """Test cursor properties."""
        # Test initial state
        assert self.cursor.metadata is None
        assert not self.cursor.is_closed

        # Test after query execution
        self.cursor._query_id = "query_123"
        from datastream_direct.models import (
            DataStreamDirectColumnMetadata,
            DataStreamDirectTypes,
        )

        self.cursor._metadata = [
            DataStreamDirectColumnMetadata(
                name="id", type=DataStreamDirectTypes.INTEGER, precision=None
            )
        ]

        assert self.cursor.metadata is not None
        assert len(self.cursor.metadata) == 1
        assert self.cursor.metadata[0].name == "id"
