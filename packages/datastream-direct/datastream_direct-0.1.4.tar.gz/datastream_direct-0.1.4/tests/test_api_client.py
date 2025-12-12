"""Tests for API client module."""

import pytest
import json
from unittest.mock import Mock, patch
import requests

from datastream_direct.api_client import DataStreamDirectAPIClient
from datastream_direct.exceptions import (
    AuthenticationError,
    ConnectionError,
    QueryError,
    APIError,
)
from datastream_direct.models import (
    ConnectionConfig,
    HttpMethod,
    DataStreamDirectEndpoint,
)


class TestDataStreamDirectAPIClient:
    """Test cases for DataStreamDirectAPIClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = ConnectionConfig(
            username="test_user",
            password="test_pass",
            host="localhost",
            port=5432,
            database="testdb",
        )
        self.client = DataStreamDirectAPIClient(self.config)

    def test_initialization(self):
        """Test client initialization."""
        assert self.client.config == self.config
        assert self.client.timeout == 600
        assert self.client.max_retries == 3
        assert self.client.connection_id is None
        assert self.client.access_token is None
        assert self.client.refresh_token is None
        assert self.client.token_expiry is None

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_success(self, mock_session_class):
        """Test successful API request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_response.headers = {}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Replace the session
        self.client.session = mock_session

        result = self.client._make_request(
            HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
        )

        assert result == {"status": "success", "data": "test"}
        mock_session.request.assert_called_once()

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_unauthorized_with_refresh(self, mock_session_class):
        """Test request with 401 status and successful token refresh."""
        mock_session = Mock()

        # First call returns 401, second call returns 200
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.headers = {}

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"status": "success"}
        mock_response_200.headers = {}

        mock_session.request.side_effect = [mock_response_401, mock_response_200]
        mock_session_class.return_value = mock_session

        # Replace the session and set up refresh token
        self.client.session = mock_session
        self.client.refresh_token = "test_refresh"

        with patch.object(self.client, "_refresh_token", return_value=True):
            result = self.client._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
            )

        assert result == {"status": "success"}
        assert mock_session.request.call_count == 2

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_unauthorized_no_refresh(self, mock_session_class):
        """Test request with 401 status and no refresh token."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Replace the session
        self.client.session = mock_session

        with pytest.raises(AuthenticationError, match="Authentications failed"):
            self.client._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
            )

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_forbidden(self, mock_session_class):
        """Test request with 403 status."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Replace the session
        self.client.session = mock_session

        with pytest.raises(APIError, match="Forbidden"):
            self.client._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
            )

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_server_error(self, mock_session_class):
        """Test request with 500 status."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Replace the session
        self.client.session = mock_session

        with pytest.raises(APIError, match="Server error: 500"):
            self.client._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
            )

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_connection_error(self, mock_session_class):
        """Test request with connection error."""
        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )
        mock_session_class.return_value = mock_session

        # Replace the session
        self.client.session = mock_session

        with pytest.raises(ConnectionError, match="Connection failed"):
            self.client._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
            )

    @patch("datastream_direct.api_client.requests.Session")
    def test_make_request_timeout(self, mock_session_class):
        """Test request with timeout."""
        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.Timeout()
        mock_session_class.return_value = mock_session

        # Replace the session
        self.client.session = mock_session

        with pytest.raises(ConnectionError, match="Request timed out"):
            self.client._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.CONNECT, {"key": "value"}
            )

    def test_handle_response_success(self):
        """Test successful response handling."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "data": "test"}

        result = self.client._handle_response(mock_response)

        assert result == {"status": "success", "data": "test"}

    def test_handle_response_json_error(self):
        """Test response handling with JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with pytest.raises(APIError, match="Failed to parse JSON response"):
            self.client._handle_response(mock_response)

    def test_handle_error_authentication(self):
        """Test error handling for authentication errors."""
        error_data = {"message": "Authentication failed", "error_code": "AUTH_001"}

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            self.client._handle_error(error_data)

    def test_handle_error_connection(self):
        """Test error handling for connection errors."""
        error_data = {"message": "Connection failed", "error_code": "CONN_001"}

        with pytest.raises(ConnectionError, match="Connection failed"):
            self.client._handle_error(error_data)

    def test_handle_error_query(self):
        """Test error handling for query errors."""
        error_data = {"message": "SQL syntax error", "error_code": "QUERY_001"}

        with pytest.raises(QueryError, match="SQL syntax error"):
            self.client._handle_error(error_data)

    def test_handle_error_general(self):
        """Test error handling for general API errors."""
        error_data = {"message": "Unknown error", "error_code": "UNKNOWN_001"}

        with pytest.raises(APIError, match="Unknown error"):
            self.client._handle_error(error_data)

    @patch.object(DataStreamDirectAPIClient, "_make_request")
    def test_connect_success(self, mock_make_request):
        """Test successful connection."""
        mock_make_request.return_value = {
            "status": "success",
            "connectionId": "conn_123",
            "access_token": "access_123",
            "refresh_token": "refresh_123",
            "expires_in": 3600,
        }

        self.client.connect()

        assert self.client.connection_id == "conn_123"
        assert self.client.access_token == "access_123"
        assert self.client.refresh_token == "refresh_123"

    @patch.object(DataStreamDirectAPIClient, "_make_request")
    def test_connect_failure(self, mock_make_request):
        """Test connection failure."""
        mock_make_request.return_value = {
            "status": "error",
            "message": "Invalid credentials",
        }

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            self.client.connect()

    @patch.object(DataStreamDirectAPIClient, "_refresh_token")
    def test_refresh_token_success(self, mock_refresh_token):
        """Test successful token refresh."""
        self.client.refresh_token = "refresh_123"
        mock_refresh_token.return_value = True

        result = self.client._refresh_token()

        assert result is True

    @patch.object(DataStreamDirectAPIClient, "_refresh_token")
    def test_refresh_token_failure(self, mock_refresh_token):
        """Test token refresh failure."""
        self.client.refresh_token = "refresh_123"
        mock_refresh_token.return_value = False

        result = self.client._refresh_token()

        assert result is False

    def test_refresh_token_no_token(self):
        """Test token refresh without refresh token."""
        result = self.client._refresh_token()
        assert result is False

    @patch.object(DataStreamDirectAPIClient, "_make_request")
    def test_execute_query_success(self, mock_make_request):
        """Test successful query execution."""
        self.client.connection_id = "conn_123"
        mock_make_request.return_value = {"status": "success", "queryId": "query_123"}

        result = self.client.execute_query("SELECT * FROM users")

        assert result == "query_123"
        mock_make_request.assert_called_once_with(
            "POST",
            "query",
            {
                "database": "testdb",
                "query": "SELECT * FROM users",
                "connection_id": "conn_123",
            },
        )

    def test_execute_query_no_connection(self):
        """Test query execution without connection."""
        with pytest.raises(ConnectionError, match="Not connected to API"):
            self.client.execute_query("SELECT * FROM users")

    @patch.object(DataStreamDirectAPIClient, "_make_request")
    def test_execute_query_error(self, mock_make_request):
        """Test query execution with error."""
        self.client.connection_id = "conn_123"
        mock_make_request.return_value = {
            "status": "error",
            "message": "SQL syntax error",
        }

        with pytest.raises(QueryError, match="SQL syntax error"):
            self.client.execute_query("INVALID SQL")

    @patch.object(DataStreamDirectAPIClient, "_make_request")
    @patch("datastream_direct.api_client.requests.get")
    def test_get_query_results_success(self, mock_requests_get, mock_make_request):
        """Test successful query results retrieval."""
        # Mock the API response with resultsUrl
        mock_make_request.return_value = {
            "status": "success",
            "resultsUrl": "https://example.com/results",
            "resultsMetadata": {},
        }

        # Mock the CSV data response
        mock_response = Mock()
        mock_response.content = b"id,name\n1,John\n2,Jane"
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        result = self.client.get_query_results("query_123")

        assert result.headers == ["id", "name"]
        assert result.rows == [("1", "John"), ("2", "Jane")]

    @patch.object(DataStreamDirectAPIClient, "_make_request")
    def test_get_query_results_error(self, mock_make_request):
        """Test query results retrieval with error."""
        mock_make_request.return_value = {
            "status": "error",
            "message": "Query not found",
        }

        with pytest.raises(QueryError, match="Query not found"):
            self.client.get_query_results("query_123")

    def test_close(self):
        """Test client close."""
        self.client.connection_id = "conn_123"
        self.client.access_token = "access_123"
        self.client.refresh_token = "refresh_123"
        self.client.token_expiry = 1234567890

        self.client.close()

        assert self.client.connection_id is None
        assert self.client.access_token is None
        assert self.client.refresh_token is None
        assert self.client.token_expiry is None
