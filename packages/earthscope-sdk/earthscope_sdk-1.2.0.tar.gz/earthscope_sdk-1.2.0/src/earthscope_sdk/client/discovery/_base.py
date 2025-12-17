import datetime as dt
from typing import Optional, Union

from earthscope_sdk.client.discovery.models import (
    ListNetworkDatasourcesResult,
    ListSessionDatasourcesResult,
    ListStationDatasourcesResult,
    ListStreamDatasourcesResult,
    NetworkDatasource,
    Page,
    SessionDatasource,
    StationDatasource,
    StreamDatasource,
    StreamType,
)
from earthscope_sdk.common.service import SdkService
from earthscope_sdk.util._itertools import to_list
from earthscope_sdk.util._types import ListOrItem


class DiscoveryBaseService(SdkService):
    """
    Discovery service functionality
    """

    async def _list_network_datasources(
        self,
        *,
        network_name: Optional[ListOrItem[str]] = None,
        network_edid: Optional[ListOrItem[str]] = None,
        with_edid_only=False,
        limit=50,
        offset=0,
    ) -> Union[Page[NetworkDatasource], Page[str]]:
        """
        List network datasources

        Args:
            network_name: The name(s) of the network to list datasources for.
            network_edid: The EDID(s) of the network to list datasources for.
            with_edid_only: Whether to return only the EDIDs of the datasources.
            limit: The maximum number of datasources to return.
            offset: The offset to start the list from.

        Returns:
            A list of network datasources.
        """
        params = {
            "with_edid_only": with_edid_only,
            "limit": limit,
            "offset": offset,
        }

        if network_name:
            params["network_name"] = to_list(network_name)

        if network_edid:
            params["network_edid"] = to_list(network_edid)

        req = self.ctx.httpx_client.build_request(
            method="GET",
            url=f"{self.resources.api_url}beta/discover/datasource/network",
            params=params,
        )

        resp = await self._send_with_retries(req)

        return ListNetworkDatasourcesResult.validate_json(resp.content)

    async def _list_station_datasources(
        self,
        *,
        network_name: Optional[ListOrItem[str]] = None,
        network_edid: Optional[ListOrItem[str]] = None,
        station_name: Optional[ListOrItem[str]] = None,
        station_edid: Optional[ListOrItem[str]] = None,
        with_edid_only=False,
        with_parent_edids=False,
        limit=50,
        offset=0,
    ) -> Union[Page[StationDatasource], Page[str]]:
        """
        List station datasources

        Args:
            network_name: The name(s) of the network to list datasources for.
            network_edid: The EDID(s) of the network to list datasources for.
            station_name: The name(s) of the station to list datasources for.
            station_edid: The EDID(s) of the station to list datasources for.
            with_edid_only: Whether to return only the EDIDs of the datasources.
            with_parent_edids: Whether to return the parent EDIDs of the datasources.
            limit: The maximum number of datasources to return.
            offset: The offset to start the list from.

        Returns:
            A list of station datasources.
        """
        params = {
            "with_edid_only": with_edid_only,
            "with_parent_edids": with_parent_edids,
            "limit": limit,
            "offset": offset,
        }

        if network_name:
            params["network_name"] = to_list(network_name)

        if network_edid:
            params["network_edid"] = to_list(network_edid)

        if station_name:
            params["station_name"] = to_list(station_name)

        if station_edid:
            params["station_edid"] = to_list(station_edid)

        req = self.ctx.httpx_client.build_request(
            method="GET",
            url=f"{self.resources.api_url}beta/discover/datasource/station",
            params=params,
        )

        resp = await self._send_with_retries(req)

        return ListStationDatasourcesResult.validate_json(resp.content)

    async def _list_session_datasources(
        self,
        *,
        network_name: Optional[ListOrItem[str]] = None,
        network_edid: Optional[ListOrItem[str]] = None,
        station_name: Optional[ListOrItem[str]] = None,
        station_edid: Optional[ListOrItem[str]] = None,
        session_name: Optional[ListOrItem[str]] = None,
        session_edid: Optional[ListOrItem[str]] = None,
        sample_interval: Optional[dt.timedelta] = None,
        roll: Optional[dt.timedelta] = None,
        with_edid_only=False,
        with_parents=False,
        with_parent_edids=False,
        limit=50,
        offset=0,
    ) -> Union[Page[SessionDatasource], Page[str]]:
        """
        List session datasources

        Args:
            network_name: The name(s) of the network to list datasources for.
            network_edid: The EDID(s) of the network to list datasources for.
            station_name: The name(s) of the station to list datasources for.
            station_edid: The EDID(s) of the station to list datasources for.
            session_name: The name(s) of the session to list datasources for.
            session_edid: The EDID(s) of the session to list datasources for.
            sample_interval: The sample interval to list datasources for.
            roll: The roll to list datasources for.
            with_edid_only: Whether to return only the EDIDs of the datasources.
            with_parents: Whether to return the parent datasources.
            with_parent_edids: Whether to return the parent EDIDs of the datasources.
            limit: The maximum number of datasources to return.
            offset: The offset to start the list from.

        Returns:
            A list of session datasources.
        """
        params = {
            "with_edid_only": with_edid_only,
            "with_parents": with_parents,
            "with_parent_edids": with_parent_edids,
            "limit": limit,
            "offset": offset,
        }

        if network_name:
            params["network_name"] = to_list(network_name)

        if network_edid:
            params["network_edid"] = to_list(network_edid)

        if station_name:
            params["station_name"] = to_list(station_name)

        if station_edid:
            params["station_edid"] = to_list(station_edid)

        if session_name:
            params["session_name"] = to_list(session_name)

        if session_edid:
            params["session_edid"] = to_list(session_edid)

        if sample_interval:
            # Convert to milliseconds
            params["sample_interval"] = 1000 * sample_interval.total_seconds()

        if roll:
            # Convert to seconds
            params["roll"] = roll.total_seconds()

        req = self.ctx.httpx_client.build_request(
            method="GET",
            url=f"{self.resources.api_url}beta/discover/datasource/session",
            params=params,
        )

        resp = await self._send_with_retries(req)

        return ListSessionDatasourcesResult.validate_json(resp.content)

    async def _list_stream_datasources(
        self,
        *,
        network_name: Optional[ListOrItem[str]] = None,
        network_edid: Optional[ListOrItem[str]] = None,
        station_name: Optional[ListOrItem[str]] = None,
        station_edid: Optional[ListOrItem[str]] = None,
        stream_name: Optional[ListOrItem[str]] = None,
        stream_edid: Optional[ListOrItem[str]] = None,
        stream_type: Optional[StreamType] = None,
        facility: Optional[str] = None,
        software: Optional[str] = None,
        label: Optional[str] = None,
        sample_interval: Optional[dt.timedelta] = None,
        with_edid_only=False,
        with_parents=False,
        with_parent_edids=False,
        limit=50,
        offset=0,
    ) -> Union[Page[StreamDatasource], Page[str]]:
        """
        List stream datasources

        Args:
            network_name: The name(s) of the network to list datasources for.
            network_edid: The EDID(s) of the network to list datasources for.
            station_name: The name(s) of the station to list datasources for.
            station_edid: The EDID(s) of the station to list datasources for.
            stream_name: The name(s) of the stream to list datasources for.
            stream_edid: The EDID(s) of the stream to list datasources for.
            stream_type: The type of stream to list datasources for.
            facility: The facility to list datasources for.
            software: The software to list datasources for.
            label: The label to list datasources for.
            sample_interval: The sample interval to list datasources for.
            with_edid_only: Whether to return only the EDIDs of the datasources.
            with_parents: Whether to return the parent datasources.
            with_parent_edids: Whether to return the parent EDIDs of the datasources.
            limit: The maximum number of datasources to return.
            offset: The offset to start the list from.

        Returns:
            A list of stream datasources.
        """
        params = {
            "with_edid_only": with_edid_only,
            "with_parents": with_parents,
            "with_parent_edids": with_parent_edids,
            "limit": limit,
            "offset": offset,
        }

        if network_name:
            params["network_name"] = to_list(network_name)

        if network_edid:
            params["network_edid"] = to_list(network_edid)

        if station_name:
            params["station_name"] = to_list(station_name)

        if station_edid:
            params["station_edid"] = to_list(station_edid)

        if stream_name:
            params["stream_name"] = to_list(stream_name)

        if stream_edid:
            params["stream_edid"] = to_list(stream_edid)

        if stream_type is not None:
            params["stream_type"] = stream_type.value

        if facility is not None:
            params["facility"] = facility

        if software is not None:
            params["software"] = software

        if label is not None:
            params["label"] = label

        if sample_interval is not None:
            # Convert to milliseconds
            params["sample_interval"] = 1000 * sample_interval.total_seconds()

        req = self.ctx.httpx_client.build_request(
            method="GET",
            url=f"{self.resources.api_url}beta/discover/datasource/stream",
            params=params,
        )

        resp = await self._send_with_retries(req)

        return ListStreamDatasourcesResult.validate_json(resp.content)
