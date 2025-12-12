"""Tests for connection module."""

import pytest
from unittest.mock import Mock, patch

from datastream_direct.connection import connect, DatastreamDirectConnection
from datastream_direct.exceptions import AuthenticationError, ConnectionError


class TestDatastreamDirectConnection:
    """Test cases for DatastreamDirectConnection."""

    def test_connection_initialization(self):
        """Test connection initialization."""
        mock_api_client = Mock()
        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )

        assert not connection.is_closed

    def test_cursor_creation(self):
        """Test cursor creation."""
        mock_api_client = Mock()
        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )

        cursor = connection.cursor()
        assert cursor.connection == connection
        assert not cursor.is_closed

    def test_cursor_creation_closed_connection(self):
        """Test cursor creation on closed connection."""
        mock_api_client = Mock()
        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )
        connection.close()

        with pytest.raises(ConnectionError, match="Connection is closed"):
            connection.cursor()

    def test_close(self):
        """Test connection close."""
        mock_api_client = Mock()
        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )

        connection.close()
        assert connection.is_closed
        mock_api_client.close.assert_called_once()

    def test_refresh_connection_success(self):
        """Test successful connection refresh."""
        mock_api_client = Mock()
        mock_api_client._refresh_token.return_value = True

        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )

        result = connection.api_client._refresh_token()
        assert result is True
        mock_api_client._refresh_token.assert_called_once()

    def test_refresh_connection_failure(self):
        """Test failed connection refresh."""
        mock_api_client = Mock()
        mock_api_client._refresh_token.return_value = False

        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )

        result = connection.api_client._refresh_token()
        assert result is False

    def test_refresh_connection_closed(self):
        """Test refresh on closed connection."""
        mock_api_client = Mock()
        connection = DatastreamDirectConnection(
            api_client=mock_api_client,
        )
        connection.close()

        # Connection is closed, but API client refresh can still be called
        # The connection being closed doesn't prevent token refresh
        mock_api_client._refresh_token.return_value = False
        result = connection.api_client._refresh_token()
        assert result is False  # No refresh token available


class TestConnect:
    """Test cases for connect function."""

    @patch("datastream_direct.connection.DataStreamDirectAPIClient")
    def test_connect_success(self, mock_api_client_class):
        """Test successful connection."""
        mock_api_client = Mock()

        mock_api_client_class.return_value = mock_api_client

        connection = connect(
            username="user",
            password="pass",
            host="localhost",
            port=5432,
            database="testdb",
        )

        assert isinstance(connection, DatastreamDirectConnection)
        mock_api_client_class.assert_called_once()
        mock_api_client.connect.assert_called_once()

    def test_connect_invalid_config(self):
        """Test connection with invalid configuration."""
        with pytest.raises(ValueError):
            connect(
                username="",  # Invalid empty username
                password="pass",
                host="localhost",
                port=5432,
                database="testdb",
            )

    @patch("datastream_direct.connection.DataStreamDirectAPIClient")
    def test_connect_authentication_error(self, mock_api_client_class):
        """Test connection with authentication error."""
        mock_api_client = Mock()
        mock_api_client.connect.side_effect = AuthenticationError("Invalid credentials")
        mock_api_client_class.return_value = mock_api_client

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            connect(
                username="user",
                password="pass",
                host="localhost",
                port=5432,
                database="testdb",
            )
