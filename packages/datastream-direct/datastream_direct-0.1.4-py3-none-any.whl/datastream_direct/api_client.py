"""
API client for communicating with the DataStream Direct API.
"""

import csv
from io import StringIO
import json
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    QueryError,
    APIError,
)
from .models import (
    ConnectionConfig,
    QueryResult,
    HttpStatus,
    HttpMethod,
    DataStreamDirectEndpoint,
)


logger = logging.getLogger(__name__)


class DataStreamDirectAPIClient:
    """Client for communicating with the DataStream Direct API."""

    def __init__(
        self, config: ConnectionConfig, timeout: int = 600, max_retries: int = 5
    ) -> None:
        """
        Initialize the API client.

        Args:
            config: Connection configuration
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.config = config
        self.base_url = config.get_base_url()
        self.timeout = timeout
        self.max_retries = max_retries

        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2,
            allowed_methods=None,
            status_forcelist=[503],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Connection state
        self.connection_id: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[float] = None

    def _make_request(
        self,
        method: HttpMethod,
        endpoint: DataStreamDirectEndpoint,
        data: Optional[Dict[str, Any]] = None,
        use_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request data
            use_auth: Whether to include authentication headers

        Returns:
            Parsed JSON response

        Raises:
            ConnectionError: If the request fails
            APIError: If the API returns an error
        """
        url = urljoin(self.base_url, f"/api-data-stream-direct/{endpoint.value}")

        # Add authentication header if needed
        headers = {}
        if use_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            logger.debug(f"Making {method} request to {url}")
            if data:
                logger.debug(f"Request data: {json.dumps(data, indent=2)}")

            response = self.session.request(
                method=method, url=url, json=data, headers=headers, timeout=self.timeout
            )

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")

            # Handle different status codes
            if response.status_code == HttpStatus.OK:
                return self._handle_response(response)
            elif response.status_code == HttpStatus.UNAUTHORIZED:
                if use_auth and self.refresh_token:
                    # Try to refresh token and retry
                    if self._refresh_token():
                        return self._make_request(method, endpoint, data, use_auth)
                    else:
                        raise AuthenticationError(
                            "Authentications failed. Please check your credentials and try again."
                        )
                else:
                    raise AuthenticationError(
                        "Authentications failed. Please check your credentials and try again."
                    )
            elif response.status_code == HttpStatus.BAD_REQUEST:
                raise QueryError(response.json().get("message", "Bad request"))
            elif response.status_code == HttpStatus.FORBIDDEN:
                raise APIError("Forbidden", status_code=HttpStatus.FORBIDDEN)
            elif response.status_code == HttpStatus.NOT_FOUND:
                raise APIError("Not found", status_code=HttpStatus.NOT_FOUND)
            elif response.status_code >= HttpStatus.INTERNAL_SERVER_ERROR:
                raise APIError(
                    f"Server error: {response.status_code}",
                    status_code=HttpStatus.of(response.status_code),
                )
            else:
                raise APIError(
                    f"Unexpected status code: {response.status_code}",
                    status_code=HttpStatus.of(response.status_code),
                )

        except requests.exceptions.Timeout:
            raise ConnectionError("Request timed out")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError("Connection failed") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError("Request failed") from e

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and extract JSON data.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON data

        Raises:
            APIError: If response cannot be parsed
        """
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise APIError("Failed to parse JSON response") from e

    def _handle_error(self, error_data: Dict[str, Any]) -> None:
        """
        Handle API error response.

        Args:
            error_data: Error data from API response

        Raises:
            Appropriate exception based on error type
        """
        error_message = error_data.get("message", "Unknown error")
        error_code = error_data.get("error_code")

        if (
            "authentication" in error_message.lower()
            or "unauthorized" in error_message.lower()
        ):
            raise AuthenticationError(error_message, error_code)
        elif "connection" in error_message.lower():
            raise ConnectionError(error_message, error_code)
        elif "query" in error_message.lower() or "sql" in error_message.lower():
            raise QueryError(error_message, error_code)
        else:
            raise APIError(error_message, error_code=error_code)

    def connect(self) -> Dict[str, Any]:
        """
        Establish connection to the DataStream Direct API.

        Returns:
            Connection data including connection ID and tokens

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
        """
        login_data = {
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "username": self.config.username,
            "password": self.config.password,
        }

        response = self._make_request(
            HttpMethod.POST,
            DataStreamDirectEndpoint.CONNECT,
            login_data,
            use_auth=False,
        )

        if response.get("status") != "success":
            error_message = response.get("message", "Login failed")
            raise AuthenticationError(error_message)

        # Store connection details
        self.connection_id = response.get("connectionId")
        self.access_token = response.get("access_token")
        self.refresh_token = response.get("refresh_token")
        expires_in = response.get("expires_in", 3600)
        self.token_expiry = time.time() + expires_in

        logger.debug("Successfully connected to DataStream Direct API")

    def _refresh_token(self) -> bool:
        """
        Refresh the access token using the refresh token.

        Returns:
            True if refresh was successful, False otherwise
        """
        if not self.refresh_token:
            return False

        try:
            refresh_data = {"refresh_token": self.refresh_token}
            response = self._make_request(
                HttpMethod.POST,
                DataStreamDirectEndpoint.REFRESH,
                refresh_data,
                use_auth=False,
            )

            if "access_token" in response:
                self.access_token = response["access_token"]
                expires_in = response.get("expires_in", 3600)
                self.token_expiry = time.time() + expires_in
                logger.info("Successfully refreshed access token")
                return True

            return False

        except Exception:
            logger.error("Token refresh failed.", exc_info=True)
            return False

    def execute_query(self, sql: str) -> str:
        """
        Execute a SQL query.

        Args:
            sql: SQL query string

        Returns:
            Query execution ID

        Raises:
            QueryError: If query execution fails
            ConnectionError: If connection is not established
        """
        if not self.connection_id:
            raise ConnectionError("Not connected to API")

        query_data = {
            "database": self.config.database,
            "query": sql,
            "connection_id": self.connection_id,
        }

        try:
            response = self._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.QUERY, query_data
            )

            if response.get("status") == "error":
                error_message = response.get("message", "Query execution failed")
                raise QueryError(error_message)

            query_id = response.get("queryId")
            if not query_id:
                raise QueryError("No query ID returned from API")

            logger.info(f"Query executed successfully, ID: {query_id}")
            return query_id

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    def get_query_results(self, query_id: str) -> QueryResult:
        """
        Retrieve query results.

        Args:
            query_id: Query execution ID
            next_token: Pagination token for next page of results

        Returns:
            QueryResult object containing the results

        Raises:
            QueryError: If results cannot be retrieved
        """
        results_data = {
            "queryExecutionId": query_id,
            "fetchRows": False,
        }

        try:
            response = self._make_request(
                HttpMethod.POST, DataStreamDirectEndpoint.QUERY_RESULTS, results_data
            )

            if response.get("status") == "error":
                error_message = response.get(
                    "message", "Failed to retrieve query results"
                )
                raise QueryError(error_message)

            url = response.get("resultsUrl")
            data = requests.get(url)
            data.raise_for_status()
            rows = data.content.decode()
            if not rows:
                raise QueryError("No results returned from API")
            reader = csv.reader(StringIO(rows))
            headers = next(reader)
            rows = [tuple(row) for row in reader]
            metadata = response.get("resultsMetadata")

            return QueryResult(
                headers=headers,
                rows=rows,
                results_metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Failed to retrieve query results: {str(e)}")
            raise

    def close(self) -> None:
        """Close the API client and clean up resources."""
        self.connection_id = None
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.session.close()
        logger.info("API client closed")
