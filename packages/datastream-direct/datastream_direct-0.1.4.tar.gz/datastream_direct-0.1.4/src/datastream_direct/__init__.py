"""
DataStream Direct Python Client

A Python client library for connecting to and querying the DataStream Direct API.
"""

from .connection import connect, DatastreamDirectConnection
from .cursor import DatastreamDirectCursor
from .exceptions import (
    DataStreamDirectError,
    AuthenticationError,
    ConnectionError,
    QueryError,
    APIError,
)
from .models import ConnectionConfig, QueryResult
from .pandas_extras import fetch_frame

try:
    from .spotfire_extras import data_stream_direct_to_spotfire_types
except ImportError:
    __spotfire_available__ = False
else:
    __spotfire_available__ = True

__version__ = "0.1.4"
__author__ = "Energy Domain"
__email__ = "developers@energydomain.com"

__all__ = [
    "connect",
    "DatastreamDirectConnection",
    "DatastreamDirectCursor",
    "fetch_frame",
    "DataStreamDirectError",
    "AuthenticationError",
    "ConnectionError",
    "QueryError",
    "APIError",
    "ConnectionConfig",
    "QueryResult",
]

if __spotfire_available__:
    __all__.append("data_stream_direct_to_spotfire_types")
