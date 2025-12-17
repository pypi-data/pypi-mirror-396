import datetime as dt
import logging
from typing import TYPE_CHECKING, Literal, NamedTuple, Optional

from typing_extensions import Self

from earthscope_sdk.client.data_access._arrow._common import (
    get_datasource_metadata_table,
)
from earthscope_sdk.client.data_access._arrow._gnss import prettify_observations_table
from earthscope_sdk.client.data_access._query_plan._query_plan import (
    AsyncQueryPlan,
    QueryPlan,
)
from earthscope_sdk.client.data_access.models import SatelliteSystem
from earthscope_sdk.client.discovery.models import SessionDatasource
from earthscope_sdk.util._itertools import to_set
from earthscope_sdk.util._time import TimePeriod, time_range_periods
from earthscope_sdk.util._types import ListOrItem

if TYPE_CHECKING:
    import pyarrow as pa

    from earthscope_sdk.client import AsyncEarthScopeClient

logger = logging.getLogger(__name__)


_MAX_EPOCHS_PER_REQUEST = 11520
"""
Maximum number of epochs per GNSS observations request.
"""


_NAMESPACES = {"igs", "4charid", "dataflow"}


GnssObservationField = Literal[
    "range",
    "phase",
    "doppler",
    "snr",
    "slip",
    "flags",
    "fcn",
]
"""
Fields available when fetching GNSS observations.

- range: code / psuedorange
- phase: carrier phase
- doppler: doppler shift
- snr: signal to noise ratio
- slip: carrier phase cycle slip occurred
- flags: event flags
- fcn: GLONASS frequency channel number
"""


GnssObservationsMetaField = Literal[
    "edid",
    "igs",
    "4charid",
    "dataflow",
    "sample_interval",
    "roll",
]
"""
Metadata fields available for joining to GNSS observations.
"""


class GnssObservationsRequest(NamedTuple):
    """
    An individual request for GNSS observations.
    """

    period: TimePeriod
    session: SessionDatasource


def _get_max_request_period(session: SessionDatasource) -> dt.timedelta:
    """
    Get the maximum request period for a session.

    Even though the API supports up to 115200 epochs per request, we limit
    request periods to nice round numbers that easily group into days.
    """

    if session.sample_interval == dt.timedelta(milliseconds=200):
        return dt.timedelta(minutes=30)

    if session.sample_interval == dt.timedelta(seconds=1):
        return dt.timedelta(hours=3)

    # fallback to actual limit of 11520 epochs per request
    # 15s -> 2 days
    # 30s -> 4 days
    # 1m -> 8 days
    # etc.
    return session.sample_interval * _MAX_EPOCHS_PER_REQUEST


class AsyncGnssObservationsQueryPlan(
    AsyncQueryPlan[GnssObservationsRequest],
):
    """
    A query plan for GNSS observations.
    """

    def __init__(
        self,
        client: "AsyncEarthScopeClient",
        # observation parameters
        start_datetime: dt.datetime,
        end_datetime: dt.datetime,
        system: ListOrItem[SatelliteSystem] = [],
        satellite: ListOrItem[str] = [],
        obs_code: ListOrItem[str] = [],
        field: ListOrItem[GnssObservationField] = [],
        # session parameters
        network_name: ListOrItem[str] = [],
        network_edid: ListOrItem[str] = [],
        station_name: ListOrItem[str] = [],
        station_edid: ListOrItem[str] = [],
        session_name: ListOrItem[str] = [],
        session_edid: ListOrItem[str] = [],
        roll: Optional[dt.timedelta] = None,
        sample_interval: Optional[dt.timedelta] = None,
        # metadata parameters
        meta_fields: ListOrItem[GnssObservationsMetaField] = ["igs"],
    ):
        if (
            not network_name
            and not network_edid
            and not station_name
            and not station_edid
            and not session_name
            and not session_edid
        ):
            raise ValueError("Expected at least one station or session name or edid")

        super().__init__(client)

        # Common parameters
        self.system = system
        self.satellite = satellite
        self.obs_code = obs_code
        self.field = field

        # Request parameters
        self.period = TimePeriod(start=start_datetime, end=end_datetime)

        # Session parameters
        self.network_name = network_name
        self.network_edid = network_edid
        self.station_name = station_name
        self.station_edid = station_edid
        self.session_name = session_name
        self.session_edid = session_edid
        self.roll = roll
        self.sample_interval = sample_interval

        # Metadata parameters
        meta_fields = to_set(meta_fields)
        self.meta_namespaces = list(meta_fields & _NAMESPACES)
        self.meta_fields = list(meta_fields - _NAMESPACES)

        # Local state
        self._meta_table: Optional["pa.Table"] = None
        self._max_request_period: Optional[dt.timedelta] = None

    async def _build_requests(self) -> list[GnssObservationsRequest]:
        # Expand station/session names into session_edids
        sessions: list[SessionDatasource]
        sessions = await self._client.discover.list_session_datasources(
            network_name=self.network_name,
            network_edid=self.network_edid,
            station_name=self.station_name,
            station_edid=self.station_edid,
            session_name=self.session_name,
            session_edid=self.session_edid,
            roll=self.roll,
            sample_interval=self.sample_interval,
            with_parents=True,
        )

        # Pre-compute metadata table
        if self.meta_fields or self.meta_namespaces:
            self._meta_table = get_datasource_metadata_table(
                sessions,
                fields=self.meta_fields + ["edid"],  # edid is required for join
                namespaces=self.meta_namespaces,
            )

        requests: list[GnssObservationsRequest] = []
        for session in sessions:
            max_period = _get_max_request_period(session)
            if self._max_request_period is not None:
                max_period = min(max_period, self._max_request_period)

            time_periods = time_range_periods(
                start=self.period.start,
                end=self.period.end,
                period=max_period,
            )
            requests.extend(GnssObservationsRequest(p, session) for p in time_periods)

        return requests

    async def _execute_one(self, args: GnssObservationsRequest) -> Optional["pa.Table"]:
        from httpx import HTTPStatusError  # lazy import

        try:
            return await self._client.data._get_gnss_observations(
                start_datetime=args.period.start,
                end_datetime=args.period.end,
                session_edid=args.session.edid,
                system=self.system,
                satellite=self.satellite,
                obs_code=self.obs_code,
                field=self.field,
            )
        except HTTPStatusError as e:
            if e.response.status_code != 404:
                raise e

            logger.debug(
                "No data available for session %s (%s to %s)",
                args.session.edid,
                args.period.start,
                args.period.end,
            )
            return None

    def _hook(self, table: "pa.Table") -> "pa.Table":
        table = prettify_observations_table(table)

        # Add metadata columns
        if self._meta_table:
            table = table.join(self._meta_table, "edid")

        # Drop edid column if not requested
        if "edid" not in self.meta_fields:
            table = table.drop_columns(["edid"])

        return table

    def group_by_day(self) -> Self:
        """
        Group the requests by day.

        This will configure the query plan to fetch data for all stations
        one day at a time.

        NOTE: This groups requests by their start times. Should a request span a
        day boundary, it will only be included in the day of its start time.
        """
        # Truncate requests to the day of their start time
        self._max_request_period = dt.timedelta(days=1)

        return self.group_by(lambda r: r.period.start.date())

    def group_by_station(self) -> Self:
        """
        Group the requests by station.

        This will configure the query plan to fetch data for the entire time
        range one station at a time.
        """
        return self.group_by(lambda r: r.session.station.edid)

    def sort_by_station(self, *, reverse: bool = False) -> Self:
        """
        Sort the requests by station name.
        """
        return self.sort_by(lambda r: r.session.station.names["IGS"], reverse=reverse)


class GnssObservationsQueryPlan(
    QueryPlan[GnssObservationsRequest],
):
    """
    A query plan for GNSS observations.
    """

    def __init__(self, async_plan: AsyncGnssObservationsQueryPlan):
        super().__init__(async_plan)

        self.group_by_day = self._wrap_and_return_self(async_plan.group_by_day)
        self.group_by_station = self._wrap_and_return_self(async_plan.group_by_station)
        self.sort_by_station = self._wrap_and_return_self(async_plan.sort_by_station)
