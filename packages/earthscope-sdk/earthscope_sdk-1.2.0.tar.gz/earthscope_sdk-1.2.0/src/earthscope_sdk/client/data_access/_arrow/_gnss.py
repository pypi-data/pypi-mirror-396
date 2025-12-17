import pyarrow as pa
import pyarrow.compute as pc

from earthscope_sdk.client.data_access._arrow._common import convert_time

_SYSTEM_ID = "system_id"
_SYSTEM_TABLE = pa.Table.from_pylist(
    [
        {_SYSTEM_ID: 1, "system": "G"},  # GPS
        {_SYSTEM_ID: 2, "system": "R"},  # GLONASS
        {_SYSTEM_ID: 3, "system": "S"},  # SBAS
        {_SYSTEM_ID: 4, "system": "E"},  # Galileo
        {_SYSTEM_ID: 5, "system": "C"},  # BeiDou
        {_SYSTEM_ID: 6, "system": "J"},  # QZSS
        {_SYSTEM_ID: 7, "system": "I"},  # IRNSS/NavIC
    ],
    schema=pa.schema(
        [
            pa.field(_SYSTEM_ID, pa.uint8()),
            pa.field("system", pa.string()),
        ]
    ),
)


def _convert_obs_code(
    table: pa.Table,
    *,
    source_field: str = "obs",
    target_field: str = "obs_code",
) -> pa.Table:
    """
    Convert the obs_code field from packed chars to a string.

    Args:
        table: The table to convert.
        source_field: The name of the field to convert.
        target_field: The name of the field to store the result.

    Returns:
        The converted table.
    """
    # extract obs_code (encoded as packed chars)
    result_chunks = [
        pc.cast(
            pa.FixedSizeBinaryArray.from_buffers(
                type=pa.binary(2),
                length=len(chunk),
                buffers=[None, chunk.buffers()[1]],
            ),
            pa.string(),
        )
        for chunk in table[source_field].chunks
    ]

    return table.set_column(
        table.schema.get_field_index(source_field),
        target_field,
        # can't easily swap endianness of packed chars, so reverse the string
        pc.utf8_reverse(pa.chunked_array(result_chunks, type=pa.string())),
    )


def _convert_system(table: pa.Table, *, field: str) -> pa.Table:
    """
    Convert the sys field from integer to string.

    Args:
        table: The table to convert.
        field: The name of the field to convert.

    Returns:
        The converted table.
    """
    return table.join(_SYSTEM_TABLE, field, right_keys=_SYSTEM_ID).drop(field)


def prettify_observations_table(table: pa.Table) -> pa.Table:
    """
    Clean up a raw observations table (as stored in TileDB) for easier use.

    Args:
        table: The table to prettify.

    Returns:
        The prettified table.
    """
    # Cast time column (integer milliseconds since epoch) to timestamp type
    table = convert_time(table)

    # Expose friendlier column names
    table = table.rename_columns({"sat": "satellite"})

    # Convert system column from integer to string
    table = _convert_system(table, field="sys")

    # Convert obs_code column from packed chars to string
    table = _convert_obs_code(table)

    return table


def prettify_positions_table(table: pa.Table) -> pa.Table:
    """
    Clean up a raw positions table (as stored in TileDB) for easier use.

    Args:
        table: The table to prettify.

    Returns:
        The prettified table.
    """
    # Convert time column (integer milliseconds since epoch) to timestamp type
    table = convert_time(table)

    return table
