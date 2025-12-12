import datetime
import decimal
import logging

import pandas as pd

from .cursor import DatastreamDirectCursor
from .models import DataStreamDirectTypes

logger = logging.getLogger(__name__)

try:
    from .spotfire_extras import data_stream_direct_to_spotfire_types

    logger.info("Spotfire extras available")
except ImportError:
    data_stream_direct_to_spotfire_types = None
    logger.info("Spotfire extras not available")

_SPOTFIRE_AVAILABLE = data_stream_direct_to_spotfire_types is not None


def _apply_type(type: DataStreamDirectTypes, values: pd.Series) -> pd.Series:
    """Apply the type to the value."""

    def _safe_apply(func, values):
        valid_mask = values.notna() & (values.str.strip() != "")
        values = values.copy()
        values[valid_mask] = values[valid_mask].apply(func)
        values[~valid_mask] = None
        return values

    if type == DataStreamDirectTypes.BOOLEAN:
        return (
            values.str.lower()
            .str.strip()
            .replace({"false": False, "true": True, "": None})
        )
    elif type == DataStreamDirectTypes.DATE:
        return _safe_apply(datetime.date.fromisoformat, values)
    elif type == DataStreamDirectTypes.DECIMAL:
        return _safe_apply(decimal.Decimal, values)
    elif type == DataStreamDirectTypes.DOUBLE:
        return values.str.strip().replace("", None).astype("float64")
    elif type == DataStreamDirectTypes.INTEGER:
        return values.str.strip().replace("", None).astype("Int32")
    elif type == DataStreamDirectTypes.LONG:
        return values.str.strip().replace("", None).astype("Int64")
    elif type == DataStreamDirectTypes.TIMESTAMP:
        return _safe_apply(datetime.datetime.fromisoformat, values)
    elif type == DataStreamDirectTypes.VARCHAR:
        return values


def fetch_frame(
    cursor: DatastreamDirectCursor,
    query: str,
    use_spotfire: bool = _SPOTFIRE_AVAILABLE,
) -> pd.DataFrame:
    """
    Execute a query and return results as a pandas DataFrame.

    This convenience function executes a SQL query using the provided cursor
    and returns the results as a pandas DataFrame with proper type conversions
    based on the column metadata. Optionally sets Spotfire-specific types if
    the `spotfire` package is available, easing integration with Python Data Functions
    in Spotfire.

    Args:
        cursor: A DatastreamDirectCursor instance
        query: SQL query string to execute
        use_spotfire: Whether to apply Spotfire type mappings (default: True if available)

    Returns:
        pandas.DataFrame: Query results with properly typed columns

    Raises:
        QueryError: If query execution fails
        ConnectionError: If cursor or connection is closed

    Example:
        >>> conn = connect(username="user", password="pass",
        ...                host="data-api.energydomain.com", port=443, database="energy_domain")
        >>> cursor = conn.cursor()
        >>> df = fetch_frame(cursor, "SELECT * FROM well_combined limit 100")
        >>> print(df.head())
    """
    cursor.execute(query)
    cursor.fetchall()
    data = pd.DataFrame(cursor.rows, columns=cursor.headers)
    if not cursor.metadata:
        return data
    for idx, column_metadata in enumerate(cursor.metadata):
        column = data.iloc[:, idx]
        data.iloc[:, idx] = _apply_type(column_metadata.type, column)
    if use_spotfire:
        if _SPOTFIRE_AVAILABLE:
            data_stream_direct_to_spotfire_types(data, cursor.metadata)
            logger.info("Spotfire types set successfully")
        else:
            logger.warning("Spotfire is not available, skipping type setting")
    return data
