import datetime as dt
import logging
from itertools import product
from typing import TYPE_CHECKING, Literal, NamedTuple, Optional

from typing_extensions import Self

from earthscope_sdk.client.data_access._query_plan._query_plan import (
    AsyncQueryPlan,
    QueryPlan,
)
from earthscope_sdk.client.data_access.models import (
    FloatFilter,
    GeodeticCoordinate,
    SatelliteSystem,
)
from earthscope_sdk.util._itertools import to_set
from earthscope_sdk.util._time import TimePeriod, time_range_periods
from earthscope_sdk.util._types import ListOrItem

if TYPE_CHECKING:
    import pyarrow as pa

    from earthscope_sdk.client import AsyncEarthScopeClient

logger = logging.getLogger(__name__)


_MAX_EPOCHS_PER_REQUEST = 11520
"""
Maximum number of epochs per GNSS satellite ephemeris positions request.
"""


GnssEphemerisPositionsField = Literal[
    "x",
    "y",
    "z",
    "elevation",
    "azimuth",
    "clock",
    "relativity",
]
"""
Fields available when fetching GNSS satellite ephemeris positions.

- x: satellite x coordinate (meters)
- y: satellite y coordinate (meters)
- z: satellite z coordinate (meters)
- elevation: elevation (degrees) from reference point to satellite in local ENU frame
- azimuth: azimuth (degrees) from reference point to satellite in local ENU frame
- clock: clock correction (seconds)
- relativity: relativity correction (seconds)
"""


class GnssEphemerisPositionsRequest(NamedTuple):
    """
    An individual request for GNSS satellite ephemeris positions.
    """

    period: TimePeriod
    system: SatelliteSystem


def _get_max_request_period(sample_interval: dt.timedelta) -> dt.timedelta:
    """
    Get the maximum request period for a sample interval.

    Even though the API supports up to 11520 epochs per request, we limit
    request periods to nice round numbers that easily group into days.
    """

    if sample_interval == dt.timedelta(milliseconds=200):
        return dt.timedelta(minutes=30)

    if sample_interval == dt.timedelta(seconds=1):
        return dt.timedelta(hours=3)

    # fallback to actual limit of 11520 epochs per request
    # 15s -> 2 days
    # 30s -> 4 days
    # 1m -> 8 days
    # etc.
    return sample_interval * _MAX_EPOCHS_PER_REQUEST


class AsyncGnssEphemerisPositionsQueryPlan(
    AsyncQueryPlan[GnssEphemerisPositionsRequest],
):
    """
    A query plan for GNSS satellite ephemeris positions.
    """

    def __init__(
        self,
        client: "AsyncEarthScopeClient",
        start_datetime: dt.datetime,
        end_datetime: dt.datetime,
        system: ListOrItem[SatelliteSystem],
        satellite: ListOrItem[str] = [],
        field: ListOrItem[GnssEphemerisPositionsField] = [],
        sample_interval: Optional[dt.timedelta] = None,
        reference_point: Optional[GeodeticCoordinate] = None,
        elevation_filter: Optional[FloatFilter] = None,
        azimuth_filter: Optional[FloatFilter] = None,
    ):
        super().__init__(client)

        # Validate parameters
        field_set = to_set(field)
        requires_reference_point = "elevation" in field_set or "azimuth" in field_set
        if requires_reference_point and reference_point is None:
            raise ValueError(
                "Reference point required to compute elevation and azimuth"
            )

        # Common parameters
        self.satellite = satellite
        self.field = field
        self.sample_interval = sample_interval
        self.reference_point = reference_point
        self.elevation_filter = elevation_filter
        self.azimuth_filter = azimuth_filter

        # Request parameters
        self.period = TimePeriod(start=start_datetime, end=end_datetime)
        self.system = sorted(to_set(system))

        # Local state
        self._max_request_period: Optional[dt.timedelta] = None

    async def _build_requests(self) -> list[GnssEphemerisPositionsRequest]:
        max_period = _get_max_request_period(self.sample_interval)
        if self._max_request_period is not None:
            max_period = min(max_period, self._max_request_period)

        time_periods = time_range_periods(
            start=self.period.start,
            end=self.period.end,
            period=max_period,
        )
        return [
            GnssEphemerisPositionsRequest(p, s)
            for p, s in product(time_periods, self.system)
        ]

    async def _execute_one(
        self,
        args: GnssEphemerisPositionsRequest,
    ) -> Optional["pa.Table"]:
        from httpx import HTTPStatusError  # lazy import

        try:
            return await self._client.data._get_gnss_ephemeris_positions(
                start_datetime=args.period.start,
                end_datetime=args.period.end,
                system=args.system,
                satellite=self.satellite,
                field=self.field,
                sample_interval=self.sample_interval,
                reference_point=self.reference_point,
                elevation_filter=self.elevation_filter,
                azimuth_filter=self.azimuth_filter,
            )
        except HTTPStatusError as e:
            if e.response.status_code != 404:
                raise e

            logger.debug(
                "No data available for system %s (%s to %s)",
                args.system,
                args.period.start,
                args.period.end,
            )
            return None

    def group_by_day(self) -> Self:
        """
        Group the requests by day.

        This will configure the query plan to fetch data for all systems
        one day at a time.

        NOTE: This groups requests by their start times. Should a request span a
        day boundary, it will only be included in the day of its start time.
        """
        # Truncate requests to the day of their start time
        self._max_request_period = dt.timedelta(days=1)

        return self.group_by(lambda r: r.period.start.date())

    def group_by_system(self) -> Self:
        """
        Group the requests by GNSS system.

        This will configure the query plan to fetch data for the entire time
        range one system at a time.
        """
        return self.group_by(lambda r: r.system)

    def sort_by_system(self, *, reverse: bool = False) -> Self:
        """
        Sort the requests by GNSS system.
        """
        return self.sort_by(lambda r: r.system, reverse=reverse)


class GnssEphemerisPositionsQueryPlan(
    QueryPlan[GnssEphemerisPositionsRequest],
):
    """
    A query plan for GNSS satellite ephemeris positions.
    """

    def __init__(self, async_plan: AsyncGnssEphemerisPositionsQueryPlan):
        super().__init__(async_plan)

        self.group_by_day = self._wrap_and_return_self(async_plan.group_by_day)
        self.group_by_system = self._wrap_and_return_self(async_plan.group_by_system)
        self.sort_by_system = self._wrap_and_return_self(async_plan.sort_by_system)
