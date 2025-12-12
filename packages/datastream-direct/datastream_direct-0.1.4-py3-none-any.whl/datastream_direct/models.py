"""
Data models for the DataStream Direct Python client.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import urlparse, urlunparse


class HttpMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class HttpStatus(int, Enum):
    """HTTP status codes."""

    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    OTHER = 0

    @classmethod
    def of(cls, code: int) -> "HttpStatus":
        """Get HTTP status code from integer."""
        if code in list(cls):
            return cls(code)
        return cls.OTHER


class DataStreamDirectEndpoint(str, Enum):
    """DataStream Direct endpoints."""

    CONNECT = "connect"
    REFRESH = "refresh"
    QUERY = "query"
    QUERY_RESULTS = "query-results"


class DataStreamDirectTypes(str, Enum):
    """DataStream Direct types."""

    BOOLEAN = "boolean"
    DATE = "date"
    DECIMAL = "decimal"
    DOUBLE = "double"
    LONG = "bigint"
    INTEGER = "integer"
    TIMESTAMP = "timestamp"
    VARCHAR = "varchar"


@dataclass
class DataStreamDirectColumnMetadata:
    """DataStream Direct column metadata."""

    name: str
    type: DataStreamDirectTypes
    precision: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataStreamDirectColumnMetadata":
        """Create a DataStreamDirectColumnMetadata from a dictionary."""
        return cls(
            name=data["name"],
            type=DataStreamDirectTypes(data["type"]),
            precision=int(data["precision"]) if data["precision"] else None,
        )


@dataclass
class ConnectionConfig:
    """
    Configuration for connecting to the DataStream Direct API.

    This dataclass holds all the parameters needed to establish a connection
    to the DataStream Direct service. All fields are validated upon initialization.

    Args:
        username: Username for authentication
        password: Password for authentication
        host: Hostname or IP address of the DataStream Direct service
        port: Port number (must be between 1 and 65535)
        database: Name of the database to connect to

    Raises:
        ValueError: If username, password, host, or database is empty
        ValueError: If port is not between 1 and 65535

    Example:
        >>> config = ConnectionConfig(
        ...     username="user",
        ...     password="pass",
        ...     host="data-api.energydomain.com",
        ...     port=443,
        ...     database="energy_domain"
        ... )
    """

    username: str
    password: str
    host: str
    port: int
    database: str

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.username:
            raise ValueError("username cannot be empty")
        if not self.password:
            raise ValueError("password cannot be empty")
        if not self.host:
            raise ValueError("host cannot be empty")
        if not self.database:
            raise ValueError("database cannot be empty")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")

    def get_base_url(self) -> str:
        """Get the base URL for the connection."""
        parsed_host = urlparse(self.host)
        netloc = parsed_host.netloc or parsed_host.path
        host = netloc.split(":")[0]
        netloc = f"{host}:{self.port}"
        if host == "127.0.0.1" or host == "localhost":
            scheme = "http"
        else:
            scheme = "https"
        return urlunparse([scheme, netloc, "", "", "", ""])


@dataclass
class QueryResult:
    """
    Result of a SQL query execution.

    This dataclass encapsulates the results returned from executing a SQL query,
    including column headers, data rows, and optional metadata.

    Args:
        headers: List of column names
        rows: List of tuples containing row data
        results_metadata: Optional metadata about the query results
    """

    headers: List[str]
    rows: List[Tuple[Any, ...]]
    results_metadata: Optional[Dict[str, Any]] = None

    def __len__(self) -> int:
        """Return the number of rows in the result."""
        return len(self.rows)

    def __iter__(self):
        """Allow iteration over rows."""
        return iter(self.rows)

    def __getitem__(self, index):
        """Allow indexing into rows."""
        return self.rows[index]
