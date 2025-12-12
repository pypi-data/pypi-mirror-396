from enum import Enum
from typing import TYPE_CHECKING

import spotfire

from .models import DataStreamDirectColumnMetadata, DataStreamDirectTypes

if TYPE_CHECKING:
    import pandas as pd


class _SpotfireTypes(str, Enum):
    BOOLEAN = "Boolean"
    INTEGER = "Integer"
    LONG_INTEGER = "LongInteger"
    SINGLE_REAL = "SingleReal"
    REAL = "Real"
    DATETIME = "DateTime"
    DATE = "Date"
    TIME = "Time"
    TIME_SPAN = "TimeSpan"
    STRING = "String"
    BINARY = "Binary"
    CURRENCY = "Currency"


_SPOTFIRE_TYPE_MAP = {
    DataStreamDirectTypes.BOOLEAN: _SpotfireTypes.BOOLEAN.value,
    DataStreamDirectTypes.DATE: _SpotfireTypes.DATE.value,
    DataStreamDirectTypes.DECIMAL: _SpotfireTypes.CURRENCY.value,
    DataStreamDirectTypes.DOUBLE: _SpotfireTypes.REAL.value,
    DataStreamDirectTypes.INTEGER: _SpotfireTypes.INTEGER.value,
    DataStreamDirectTypes.LONG: _SpotfireTypes.LONG_INTEGER.value,
    DataStreamDirectTypes.TIMESTAMP: _SpotfireTypes.DATETIME.value,
    DataStreamDirectTypes.VARCHAR: _SpotfireTypes.STRING.value,
}


def _spotfire_type_map(column_metadata: list[DataStreamDirectColumnMetadata]):
    """Map a DataStream Direct column metadata to a Spotfire column type."""
    return {
        column_metadata.name: _SPOTFIRE_TYPE_MAP[column_metadata.type]
        for column_metadata in column_metadata
    }


def data_stream_direct_to_spotfire_types(
    dataframe: "pd.DataFrame", column_metadata: list[DataStreamDirectColumnMetadata]
):
    """
    Set Spotfire-specific data types for a pandas DataFrame.

    This function applies Spotfire type metadata to a pandas DataFrame based on
    the column metadata from a DataStream Direct query. This ensures that data
    types are properly recognized when using the DataFrame in Spotfire.

    Args:
        dataframe: A pandas DataFrame to apply Spotfire types to
        column_metadata: List of DataStreamDirectColumnMetadata objects describing
                        the columns in the DataFrame

    Returns:
        None: The DataFrame is modified in-place

    Raises:
        ImportError: If the Spotfire package is not available

    Example:
        >>> cursor.execute("SELECT * FROM well_combined limit 100")
        >>> cursor.fetchall()
        >>> df = pd.DataFrame(cursor.rows, columns=cursor.headers)
        >>> data_stream_direct_to_spotfire_types(df, cursor.metadata)
    """
    spotfire.set_spotfire_types(dataframe, _spotfire_type_map(column_metadata))
