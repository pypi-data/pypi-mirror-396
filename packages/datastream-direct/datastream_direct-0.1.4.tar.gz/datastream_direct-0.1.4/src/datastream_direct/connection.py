"""
Connection class for the DataStream Direct Python client.
"""

import logging

from .api_client import DataStreamDirectAPIClient
from .cursor import DatastreamDirectCursor
from .exceptions import ConnectionError
from .models import ConnectionConfig


logger = logging.getLogger(__name__)


class DatastreamDirectConnection:
    """
    Connection to the DataStream Direct API.

    This class represents an active connection to the DataStream Direct service.
    It manages authentication tokens and provides methods for creating cursors
    to execute queries. The usual method for creating a connection is to use the
    `connect` function.

    Attributes:
        api_client: The API client used to communicate with the service
    """

    def __init__(
        self,
        api_client: DataStreamDirectAPIClient,
    ) -> None:
        """
        Initialize a connection.

        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        self._closed = False

        logger.debug(f"Connection established with ID: {self.api_client.connection_id}")

    def connect(self) -> None:
        """Connect to the DataStream Direct API."""
        self.api_client.connect()
        logger.debug(f"Connection established with ID: {self.api_client.connection_id}")

    def cursor(self) -> DatastreamDirectCursor:
        """
        Create a new cursor for executing queries.

        Returns:
            New cursor instance

        Raises:
            ConnectionError: If connection is closed
        """
        if self._closed:
            raise ConnectionError("Connection is closed")

        return DatastreamDirectCursor(self)

    def close(self) -> None:
        """Close the connection and clean up resources."""
        if not self._closed:
            self._closed = True
            self.api_client.close()
            logger.debug("Connection closed")

    @property
    def is_closed(self) -> bool:
        """Check if the connection is closed."""
        return self._closed


def connect(
    username: str,
    password: str,
    host: str,
    port: int,
    database: str,
) -> DatastreamDirectConnection:
    """
    Connect to the DataStream Direct API.

    Args:
        username: Authentication username
        password: Authentication password
        host: Database host
        port: Database port
        database: Database name

    Returns:
        Connection instance

    Raises:
        ValueError: If any required parameter is invalid
        AuthenticationError: If authentication fails
        ConnectionError: If connection fails
    """
    # Validate and create configuration
    config = ConnectionConfig(
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    # Create API client and connect
    api_client = DataStreamDirectAPIClient(config)
    connection = DatastreamDirectConnection(api_client)
    connection.connect()

    # Create and return connection
    return connection
