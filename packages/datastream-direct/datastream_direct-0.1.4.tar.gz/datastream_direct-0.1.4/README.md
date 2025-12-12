# DataStream Direct Python Client

A Python client library for connecting to and querying the DataStream Direct API.

## Installation

```bash
pip install datastream-direct
```

## Quick Start

```python
from datastream_direct import connect

# Connect to the API
connection = connect(
    username="your_username",
    password="your_password", 
    host="your_host",
    port=5432,
    database="your_database"
)

# Get cursor and execute query
cursor = connection.cursor()
cursor.execute("SELECT * FROM well_combined LIMIT 10")
results = cursor.fetchall()

# Results will be a list of tuples
for row in results:
    print(row)

# Close the connection
connection.close()
```

## Pandas DataFrame Integration

```python
from datastream_direct import connect, fetch_frame
import pandas as pd

# Connect
conn = connect(
    username="user",
    password="pass",
    host="localhost", 
    port=5432,
    database="mydb"
)

# Get results as a DataFrame with proper type conversion
df = fetch_frame(conn.cursor(), "SELECT * FROM well_combined LIMIT 100")
print(df.dtypes)  # Shows proper column types
print(df.head())

# Clean up
conn.close()
```

## API Reference

### Functions

#### `connect(username, password, host, port, database)`

Create a connection to the DataStream Direct API.

**Parameters:**
- `username` (str): Authentication username
- `password` (str): Authentication password  
- `host` (str): Database host
- `port` (int): Database port
- `database` (str): Database name

**Returns:** `DatastreamDirectConnection` instance

**Raises:**
- `ValueError`: If any required parameter is invalid
- `AuthenticationError`: If authentication fails
- `ConnectionError`: If connection fails

**Example:**
```python
from datastream_direct import connect

connection = connect(
    username="user",
    password="pass",
    host="data-api.energydomain.com",
    port=443,
    database="energy_domain"
)
```

#### `fetch_frame(cursor, query)`

Execute a query and return results as a pandas DataFrame with proper type conversion.

**Parameters:**
- `cursor` (DatastreamDirectCursor): Cursor instance
- `query` (str): SQL query string

**Returns:** `pandas.DataFrame` with properly typed columns

**Example:**
```python
from datastream_direct import connect, fetch_frame

connection = connect(username="user", password="pass", ...)
cursor = connection.cursor()

# Get results as a DataFrame
df = fetch_frame(cursor, "SELECT * FROM well_combined LIMIT 100")
print(df.dtypes)  # Shows proper column types
```

#### `data_stream_direct_to_spotfire_types(dataframe, column_metadata)`

Set Spotfire-specific data types for a pandas DataFrame.

**Parameters:**
- `dataframe` (pandas.DataFrame): A pandas DataFrame to apply Spotfire types to
- `column_metadata` (List[DataStreamDirectColumnMetadata]): List of column metadata objects describing the columns in the DataFrame

**Returns:** None (modifies the DataFrame in-place)

**Raises:**
- `ImportError`: If the Spotfire package is not available

**Note:** This function is only available if the Spotfire package is installed.

**Example:**
```python
from datastream_direct import connect, data_stream_direct_to_spotfire_types
import pandas as pd

connection = connect(username="user", password="pass", ...)
cursor = connection.cursor()

cursor.execute("SELECT * FROM well_combined LIMIT 100")
cursor.fetchall()

df = pd.DataFrame(cursor.rows, columns=[col.name for col in cursor.metadata])
data_stream_direct_to_spotfire_types(df, cursor.metadata)
```

### Classes

#### `DatastreamDirectConnection`

Connection class for managing API connections.

**Methods:**
- `cursor()`: Create a new cursor for executing queries
- `close()`: Close the connection and clean up resources

**Properties:**
- `is_closed` (bool): Check if the connection is closed

#### `DatastreamDirectCursor`

Cursor class for executing SQL queries and retrieving results.

**Methods:**
- `execute(sql)`: Execute a SQL query
- `fetchall()`: Fetch all results from the last executed query
- `close()`: Close the cursor and clean up resources

**Properties:**
- `metadata`: Column metadata from the last executed query
- `is_closed` (bool): Check if the cursor is closed

#### `ConnectionConfig`

Configuration dataclass for connecting to the DataStream Direct API.

**Attributes:**
- `username` (str): Username for authentication
- `password` (str): Password for authentication
- `host` (str): Hostname or IP address of the DataStream Direct service
- `port` (int): Port number (must be between 1 and 65535)
- `database` (str): Name of the database to connect to

**Methods:**
- `get_base_url()`: Get the base URL for the connection

**Raises:**
- `ValueError`: If any parameter is invalid or empty

**Example:**
```python
from datastream_direct import ConnectionConfig

config = ConnectionConfig(
    username="user",
    password="pass",
    host="data-api.energydomain.com",
    port=443,
    database="energy_domain"
)

base_url = config.get_base_url()
```

#### `QueryResult`

Result of a SQL query execution. Supports iteration over rows.

**Attributes:**
- `headers` (List[str]): List of column names
- `rows` (List[Tuple[Any, ...]]): List of tuples containing row data
- `results_metadata` (Optional[Dict[str, Any]]): Optional metadata about the query results

**Example:**
```python
from datastream_direct import QueryResult

result = QueryResult(
    headers=["id", "name"],
    rows=[(1, "Alice"), (2, "Bob")]
)

print(len(result))  # 2
for row in result:
    print(row)
```

### Exceptions

#### `DataStreamDirectError`

Base exception class for all DataStream Direct errors. All exceptions raised by the client inherit from this class.

**Attributes:**
- `message` (str): The error message
- `error_code` (Optional[str]): Optional error code if provided

**Example:**
```python
from datastream_direct import connect, DataStreamDirectError

try:
    connection = connect(...)
except DataStreamDirectError as e:
    print(f"Error: {e.message}")
    if e.error_code:
        print(f"Error Code: {e.error_code}")
```

#### `AuthenticationError(DataStreamDirectError)`

Raised when authentication fails. This exception is raised when the provided credentials are invalid or when the authentication process fails.

**Example:**
```python
from datastream_direct import connect, AuthenticationError

try:
    connection = connect(username="user", password="wrong", ...)
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

#### `ConnectionError(DataStreamDirectError)`

Raised when connection to the API fails. This exception is raised when there are network issues, the service is unavailable, or when attempting to use a closed connection.

**Example:**
```python
from datastream_direct import connect, ConnectionError

try:
    connection = connect(...)
    # Later, try to use closed connection
    cursor = connection.cursor()
except ConnectionError as e:
    print(f"Connection error: {e.message}")
```

#### `QueryError(DataStreamDirectError)`

Raised when query execution fails. This exception is raised when a SQL query fails to execute, either due to syntax errors, permission issues, or other query-related problems.

**Example:**
```python
from datastream_direct import QueryError

try:
    cursor.execute("INVALID SQL")
except QueryError as e:
    print(f"Query failed: {e.message}")
```

#### `APIError(DataStreamDirectError)`

Raised when the API returns an error response. This exception is raised for general API errors that don't fall into other specific error categories.

**Attributes:**
- `message` (str): The error message
- `status_code` (Optional[HttpStatus]): HTTP status code if available
- `error_code` (Optional[str]): Optional error code if provided

**Example:**
```python
from datastream_direct import APIError

try:
    cursor.execute("SELECT * FROM nonexistent")
except APIError as e:
    print(f"API error: {e.message}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

## Error Handling

The library provides specific exception classes for different error scenarios:

- `DataStreamDirectError`: Base exception class
- `AuthenticationError`: Authentication failures
- `ConnectionError`: Connection issues
- `QueryError`: SQL execution failures
- `APIError`: General API errors

**Example:**
```python
from datastream_direct import connect, AuthenticationError, QueryError

try:
    connection = connect(username="user", password="pass", ...)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM table")
    results = cursor.fetchall()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except QueryError as e:
    print(f"Query failed: {e}")
finally:
    connection.close()
```

## Configuration

### Logging

The library uses Python's standard logging module. To enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

**Note:** For connection configuration details, see the `ConnectionConfig` class in the API Reference section above.

## License

[Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/)

