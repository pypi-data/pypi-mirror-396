from datetime import timedelta
from enum import Enum
from typing import Annotated, Any, Generic, Iterable, Optional, TypeVar, Union

from pydantic import BaseModel, BeforeValidator, TypeAdapter

from earthscope_sdk.util._itertools import to_set


def _coerce_timedelta_ms(v: Union[int, float, timedelta, str]) -> timedelta:
    if isinstance(v, (int, float)):
        return timedelta(milliseconds=v)

    # fallback to Pydantic's timedelta parser
    return v


P = TypeVar("P")


class Page(BaseModel, Generic[P]):
    has_next: bool
    offset: int
    limit: int
    items: list[P]
    total: Optional[int] = None


class DatasourceBaseModel(BaseModel):
    edid: str
    names: dict[str, str]
    description: Optional[str] = None

    def to_arrow_columns(
        self,
        *,
        fields: Union[list[str], str] = ["edid", "names"],
        namespaces: Union[list[str], str] = [],
    ) -> dict[str, Any]:
        """
        Convert the datasource model to a dictionary suitable for use in an Arrow table.
        """
        result = {}
        namespaces = to_set(namespaces)
        fields = to_set(fields)

        # Add names to fields if namespaces are requested
        if namespaces:
            fields.add("names")

        for field in fields:
            if field != "names":
                result[field] = getattr(self, field)
                continue

            # Explode names to own columns
            if not namespaces:
                names = {k.lower(): v for k, v in self.names.items()}
            else:
                names = {
                    k_lower: v
                    for k, v in self.names.items()
                    if (k_lower := k.lower()) in namespaces
                }

            result.update(names)

        return result


class NetworkDatasource(DatasourceBaseModel): ...


ListNetworkDatasourcesResult = TypeAdapter(Union[Page[str], Page[NetworkDatasource]])


class StationDatasource(DatasourceBaseModel):
    network_edids: Optional[list[str]] = None
    networks: Optional[list[NetworkDatasource]] = None


ListStationDatasourcesResult = TypeAdapter(Union[Page[str], Page[StationDatasource]])


class _StationDatasourceMember(DatasourceBaseModel):
    station_edid: Optional[str] = None
    station: Optional[StationDatasource] = None

    def to_arrow_columns(
        self,
        *,
        fields: list[str] = ["edid", "names"],
        namespaces: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        result = super().to_arrow_columns(fields=fields, namespaces=namespaces)
        if self.station:
            parent_columns = self.station.to_arrow_columns(
                fields=["names"],
                namespaces=namespaces,
            )
            result.update(parent_columns)

        return result


class SessionDatasource(_StationDatasourceMember):
    sample_interval: Annotated[timedelta, BeforeValidator(_coerce_timedelta_ms)]
    """
    Session sample interval.
    """

    roll: timedelta  # already in seconds
    """
    Session file roll cadence.
    """


ListSessionDatasourcesResult = TypeAdapter(Union[Page[str], Page[SessionDatasource]])


class StreamType(Enum):
    GNSS_RAW = "gnss_raw"
    GNSS_PPP = "gnss_ppp"


class StreamDatasource(_StationDatasourceMember):
    stream_type: StreamType
    facility: str
    software: str
    label: str
    sample_interval: Annotated[timedelta, BeforeValidator(_coerce_timedelta_ms)]
    """
    Stream sample interval.
    """

    def to_arrow_columns(
        self,
        *,
        fields: Iterable[str] = ["edid", "names", "facility", "software", "label"],
    ) -> dict[str, Any]:
        return super().to_arrow_columns(fields=fields)


ListStreamDatasourcesResult = TypeAdapter(Union[Page[str], Page[StreamDatasource]])
