try:
    import pyarrow as pa
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Optional dependency 'pyarrow' is required for this feature. "
        "Install it with: pip install earthscope-sdk[arrow]"
    ) from e


from earthscope_sdk.client.discovery.models import DatasourceBaseModel


def convert_time(
    table: pa.Table,
    *,
    source_field: str = "time",
    target_field: str = "timestamp",
    unit: str = "ms",
    tz: str = "UTC",
) -> pa.Table:
    """
    Convert a unix timestamp (integer since epoch) field to a timestamp type.

    Args:
        table: The table to convert.
        source_field: The name of the field to convert.
        target_field: The name of the field to store the result.
        unit: The unit of the time field.
        tz: The timezone of the time field.

    Returns:
        The converted table.
    """
    if unit not in {"s", "ms", "us", "ns"}:
        raise ValueError(f"Invalid time unit: {unit}")

    time_idx = table.schema.get_field_index(source_field)
    if time_idx < 0:
        return table

    return table.set_column(
        time_idx,
        target_field,
        table[source_field].cast(pa.timestamp(unit, tz)),
    )


def get_datasource_metadata_table(
    datasources: list[DatasourceBaseModel],
    *,
    fields: list[str],
    namespaces: list[str],
) -> pa.Table:
    """
    Get a pyarrow table containing metadata columns for a list of datasources.

    Args:
        datasources: The list of datasources to get metadata for.
        fields: The fields to include in the metadata table.
        namespaces: The namespaces to include in the metadata table.

    Returns:
        The metadata table.
    """
    return pa.Table.from_pylist(
        [s.to_arrow_columns(fields=fields, namespaces=namespaces) for s in datasources]
    )


def load_table_with_extra(content: bytes, *, is_stream=True, **kwargs) -> pa.Table:
    """
    Load a table from an arrow stream or file. Optionally add extra metadata columns.

    Args:
        content: The content of the stream or file.
        is_stream: Whether the content is an arrow stream or an arrow file.
        **kwargs: The extra metadata columns to add to the table.

    Returns:
        The loaded table.
    """
    if is_stream:
        reader = pa.ipc.open_stream(content)
    else:
        reader = pa.ipc.open_file(content)

    table = reader.read_all()

    if kwargs:
        count = len(table)
        for key, value in kwargs.items():
            table = table.append_column(key, pa.repeat(value, count))

    return table
