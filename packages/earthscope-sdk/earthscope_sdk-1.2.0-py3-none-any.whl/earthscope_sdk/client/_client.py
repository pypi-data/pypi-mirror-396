from functools import cached_property

from earthscope_sdk.common.client import AsyncSdkClient, SdkClient


class AsyncEarthScopeClient(AsyncSdkClient):
    """
    An async client for interacting with api.earthscope.org
    """

    @cached_property
    def data(self):
        """
        Data access functionality
        """
        # lazy load
        from earthscope_sdk.client.data_access._service import AsyncDataAccessService

        return AsyncDataAccessService(self)

    @cached_property
    def discover(self):
        """
        Data discovery functionality
        """
        # lazy load
        from earthscope_sdk.client.discovery._service import AsyncDiscoveryService

        return AsyncDiscoveryService(self._ctx)

    @cached_property
    def user(self):
        """
        User and Identity Management functionality
        """
        # lazy load
        from earthscope_sdk.client.user._service import AsyncUserService

        return AsyncUserService(self._ctx)


class EarthScopeClient(SdkClient):
    """
    A client for interacting with api.earthscope.org
    """

    @cached_property
    def _async_client(self):
        """
        An async client for interacting with api.earthscope.org
        """
        return AsyncEarthScopeClient(ctx=self._ctx)

    @cached_property
    def data(self):
        """
        Data access functionality
        """
        # lazy load
        from earthscope_sdk.client.data_access._service import DataAccessService

        return DataAccessService(self._async_client)

    @cached_property
    def discover(self):
        """
        Data discovery functionality
        """
        # lazy load
        from earthscope_sdk.client.discovery._service import DiscoveryService

        return DiscoveryService(self._ctx)

    @cached_property
    def user(self):
        """
        User and Identity Management functionality
        """
        # lazy load
        from earthscope_sdk.client.user._service import UserService

        return UserService(self._ctx)
