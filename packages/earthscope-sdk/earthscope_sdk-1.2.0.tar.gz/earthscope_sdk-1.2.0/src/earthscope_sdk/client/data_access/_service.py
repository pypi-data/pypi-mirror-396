import datetime as dt
from typing import TYPE_CHECKING, Optional

from earthscope_sdk.client.data_access._base import DataAccessBaseService
from earthscope_sdk.client.data_access._query_plan._gnss_ephemeris_positions import (
    AsyncGnssEphemerisPositionsQueryPlan,
    GnssEphemerisPositionsField,
    GnssEphemerisPositionsQueryPlan,
)
from earthscope_sdk.client.data_access._query_plan._gnss_observations import (
    AsyncGnssObservationsQueryPlan,
    GnssObservationField,
    GnssObservationsMetaField,
    GnssObservationsQueryPlan,
    SatelliteSystem,
)
from earthscope_sdk.client.data_access.models import FloatFilter, GeodeticCoordinate
from earthscope_sdk.util._types import ListOrItem

if TYPE_CHECKING:
    from earthscope_sdk.client._client import AsyncEarthScopeClient


class _DataAccessService(DataAccessBaseService):
    """
    L2 data access service functionality
    """

    def __init__(self, client: "AsyncEarthScopeClient"):
        super().__init__(client._ctx)
        self._client = client

    def _gnss_observations(
        self,
        *,
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
        """
        Retrieve GNSS observations.

        Args:
            start_datetime: The start datetime to retrieve observations for.
            end_datetime: The end datetime to retrieve observations for.
            system: The system(s) to retrieve observations for.
            satellite: The satellite(s) to retrieve observations for.
            obs_code: The observation code(s) to retrieve observations for.
            field: The observation field(s) to retrieve.
            network_name: The network name to retrieve observations for.
            network_edid: The network edid to retrieve observations for.
            station_name: The station name to retrieve observations for.
            station_edid: The station edid to retrieve observations for.
            session_name: The session name to retrieve observations for.
            session_edid: The session edid to retrieve observations for.
            roll: The session roll to retrieve observations for.
            sample_interval: The session sample interval to retrieve observations for.
            meta_fields: Metadata fields to add to the table.

        Returns:
            A query plan for GNSS observations.
        """

        return AsyncGnssObservationsQueryPlan(
            client=self._client,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            system=system,
            satellite=satellite,
            obs_code=obs_code,
            field=field,
            network_name=network_name,
            network_edid=network_edid,
            station_name=station_name,
            station_edid=station_edid,
            session_name=session_name,
            session_edid=session_edid,
            roll=roll,
            sample_interval=sample_interval,
            meta_fields=meta_fields,
        )

    def _gnss_ephemeris_positions(
        self,
        *,
        start_datetime: dt.datetime,
        end_datetime: dt.datetime,
        system: ListOrItem[SatelliteSystem],
        satellite: ListOrItem[str] = [],
        field: ListOrItem[GnssEphemerisPositionsField] = [],
        sample_interval: Optional[dt.timedelta] = dt.timedelta(seconds=15),
        reference_point: Optional[GeodeticCoordinate] = None,
        elevation_filter: Optional[FloatFilter] = None,
        azimuth_filter: Optional[FloatFilter] = None,
    ):
        """
        Retrieve GNSS satellite ephemeris positions.

        Args:
            start_datetime: The start datetime to retrieve positions for.
            end_datetime: The end datetime to retrieve positions for.
            system: The system(s) to retrieve positions for.
            satellite: The satellite(s) to retrieve positions for.
            field: The field(s) to retrieve.
            sample_interval: The sample interval to retrieve positions for.
            reference_point: The reference point to compute elevation and azimuth for.
            elevation_filter: The filter to apply to the elevation field.
            azimuth_filter: The filter to apply to the azimuth field.

        Returns:
            A query plan for GNSS satellite ephemeris positions.
        """
        return AsyncGnssEphemerisPositionsQueryPlan(
            client=self._client,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            system=system,
            satellite=satellite,
            field=field,
            sample_interval=sample_interval,
            reference_point=reference_point,
            elevation_filter=elevation_filter,
            azimuth_filter=azimuth_filter,
        )


class AsyncDataAccessService(_DataAccessService):
    """
    Data access functionality
    """

    def __init__(self, client: "AsyncEarthScopeClient"):
        super().__init__(client)

        self.gnss_observations = self._gnss_observations
        self.gnss_ephemeris_positions = self._gnss_ephemeris_positions


class DataAccessService(_DataAccessService):
    """
    Data access functionality
    """

    def __init__(self, client: "AsyncEarthScopeClient"):
        super().__init__(client)

        self.gnss_observations = GnssObservationsQueryPlan._syncify_query_plan(
            self._gnss_observations
        )
        self.gnss_ephemeris_positions = (
            GnssEphemerisPositionsQueryPlan._syncify_query_plan(
                self._gnss_ephemeris_positions
            )
        )
