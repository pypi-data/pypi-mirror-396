import datetime as dt
from functools import partial
from typing import Any, AsyncIterator, Coroutine, Optional, TypeVar, Union

from earthscope_sdk.client.discovery._base import DiscoveryBaseService
from earthscope_sdk.client.discovery.models import (
    NetworkDatasource,
    Page,
    SessionDatasource,
    StationDatasource,
    StreamDatasource,
    StreamType,
)
from earthscope_sdk.common.context import SdkContext
from earthscope_sdk.util._types import ListOrItem

P = TypeVar("P")


class _DiscoveryService(DiscoveryBaseService):
    """
    L2 discovery service functionality
    """

    async def _iter_pages(
        self,
        fn: Coroutine[Any, Any, Page[P]],
        limit: int,
    ) -> AsyncIterator[Page[P]]:
        """
        Iterate over pages of results from a function.

        Args:
            fn: The function to call to get a page of results.
            limit: The maximum number of results to return.

        Returns:
            An iterator over the pages of results.
        """
        offset = 0
        page_size = 100
        has_next = True
        result_ct = 0

        while has_next and result_ct < limit:
            page_size = min(page_size, limit - result_ct)
            page: Page[P] = await fn(offset=offset, limit=page_size)
            yield page
            has_next = page.has_next
            offset += page_size
            result_ct += len(page.items)

    async def _load_all_pages(
        self,
        fn: Coroutine[Any, Any, Page[P]],
        limit: int,
    ) -> list[P]:
        """
        Load all pages of results from a function.
        """
        results: list[P] = []
        async for p in self._iter_pages(fn=fn, limit=limit):
            results.extend(p.items)

        return results

    async def _list_network_datasources(
        self,
        *,
        network_name: Optional[ListOrItem[str]] = None,
        network_edid: Optional[ListOrItem[str]] = None,
        with_edid_only=False,
        limit=1000,
    ) -> Union[list[NetworkDatasource], list[str]]:
        return await self._load_all_pages(
            fn=partial(
                super()._list_network_datasources,
                network_name=network_name,
                network_edid=network_edid,
                with_edid_only=with_edid_only,
            ),
            limit=limit,
        )

    async def _list_station_datasources(
        self,
        *,
        network_name: Optional[ListOrItem[str]] = None,
        network_edid: Optional[ListOrItem[str]] = None,
        station_name: Optional[ListOrItem[str]] = None,
        station_edid: Optional[ListOrItem[str]] = None,
        with_edid_only=False,
        with_parent_edids=False,
        limit=1000,
    ) -> Union[list[StationDatasource], list[str]]:
        return await self._load_all_pages(
            fn=partial(
                super()._list_station_datasources,
                network_name=network_name,
                network_edid=network_edid,
                station_name=station_name,
                station_edid=station_edid,
                with_edid_only=with_edid_only,
                with_parent_edids=with_parent_edids,
            ),
            limit=limit,
        )

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
        limit=1000,
    ) -> Union[list[SessionDatasource], list[str]]:
        return await self._load_all_pages(
            fn=partial(
                super()._list_session_datasources,
                network_name=network_name,
                network_edid=network_edid,
                station_name=station_name,
                station_edid=station_edid,
                session_name=session_name,
                session_edid=session_edid,
                sample_interval=sample_interval,
                roll=roll,
                with_edid_only=with_edid_only,
                with_parents=with_parents,
                with_parent_edids=with_parent_edids,
            ),
            limit=limit,
        )

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
        limit=1000,
    ) -> Union[list[StreamDatasource], list[str]]:
        return await self._load_all_pages(
            fn=partial(
                super()._list_stream_datasources,
                network_name=network_name,
                network_edid=network_edid,
                station_name=station_name,
                station_edid=station_edid,
                stream_name=stream_name,
                stream_edid=stream_edid,
                stream_type=stream_type,
                facility=facility,
                software=software,
                label=label,
                sample_interval=sample_interval,
                with_edid_only=with_edid_only,
                with_parents=with_parents,
                with_parent_edids=with_parent_edids,
            ),
            limit=limit,
        )


class AsyncDiscoveryService(_DiscoveryService):
    """
    Discovery service functionality
    """

    def __init__(self, ctx: SdkContext):
        super().__init__(ctx)

        self.list_network_datasources = self._list_network_datasources
        self.list_station_datasources = self._list_station_datasources
        self.list_session_datasources = self._list_session_datasources
        self.list_stream_datasources = self._list_stream_datasources


class DiscoveryService(_DiscoveryService):
    """
    Discovery service functionality
    """

    def __init__(self, ctx: SdkContext):
        super().__init__(ctx)

        self.list_network_datasources = ctx.syncify(self._list_network_datasources)
        self.list_station_datasources = ctx.syncify(self._list_station_datasources)
        self.list_session_datasources = ctx.syncify(self._list_session_datasources)
        self.list_stream_datasources = ctx.syncify(self._list_stream_datasources)
