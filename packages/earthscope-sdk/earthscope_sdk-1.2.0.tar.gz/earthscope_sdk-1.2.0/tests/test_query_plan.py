import asyncio
from typing import NamedTuple

import pyarrow as pa
import pytest

from earthscope_sdk.client._client import AsyncEarthScopeClient, EarthScopeClient
from earthscope_sdk.client.data_access._query_plan._query_plan import (
    AsyncQueryPlan,
    QueryPlan,
)
from earthscope_sdk.client.data_access.error import (
    MemoryLimitExceededError,
    TimeoutExceededError,
)

_responses = {
    1: pa.table({"key": [1, 2, 3], "value": ["a", "b", "c"]}),
    2: pa.table({"key": [4, 5, 6], "value": ["d", "e", "f"]}),
    3: pa.table({"key": [7, 8, 9], "value": ["g", "h", "i"]}),
    4: pa.table({"key": [10, 11, 12], "value": ["j", "k", "l"]}),
}

_join_table = pa.table(
    {
        "key": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "meta": [
            "foo",
            "bar",
            "baz",
            "qux",
            "quux",
            "corge",
            "grault",
            "garply",
            "waldo",
            "fred",
            "plugh",
            "xyzzy",
        ],
    }
)


class MyReq(NamedTuple):
    request_key: int


class MyAsyncQueryPlan(AsyncQueryPlan[MyReq]):
    def __init__(self, client: AsyncEarthScopeClient):
        super().__init__(client)

    async def _build_requests(self) -> list[MyReq]:
        return [MyReq(request_key=k) for k in _responses.keys()]

    async def _execute_one(self, req: MyReq) -> pa.Table:
        return _responses[req.request_key]

    def _hook(self, table: pa.Table) -> pa.Table:
        return table.join(_join_table, keys="key").combine_chunks().sort_by("key")


class MySyncQueryPlan(QueryPlan[MyReq]): ...


class TestAsyncQueryPlan:
    @pytest.mark.asyncio
    async def test_fetch(self):
        async with AsyncEarthScopeClient() as client:
            plan = MyAsyncQueryPlan(client)

            assert len(plan) == 0
            assert repr(plan) == "MyAsyncQueryPlan(unplanned)"

            table = await plan.fetch()
            assert table == pa.table(
                {
                    "key": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    "value": [
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                    ],
                    "meta": [
                        "foo",
                        "bar",
                        "baz",
                        "qux",
                        "quux",
                        "corge",
                        "grault",
                        "garply",
                        "waldo",
                        "fred",
                        "plugh",
                        "xyzzy",
                    ],
                }
            )

    @pytest.mark.asyncio
    async def test_iteration(self):
        async with AsyncEarthScopeClient() as client:
            plan = await MyAsyncQueryPlan(client).plan()

            assert len(plan) == 4
            assert len(plan.request_groups) == 4

            plan.group_by(lambda r: r.request_key % 2)
            assert len(plan.request_groups) == 2

            it = plan.__aiter__()
            t0 = await it.__anext__()
            t1 = await it.__anext__()
            with pytest.raises(StopAsyncIteration):
                await it.__anext__()

            assert t0 == pa.table(
                {
                    "key": [1, 2, 3, 7, 8, 9],
                    "value": ["a", "b", "c", "g", "h", "i"],
                    "meta": ["foo", "bar", "baz", "grault", "garply", "waldo"],
                }
            )
            assert t1 == pa.table(
                {
                    "key": [4, 5, 6, 10, 11, 12],
                    "value": ["d", "e", "f", "j", "k", "l"],
                    "meta": ["qux", "quux", "corge", "fred", "plugh", "xyzzy"],
                }
            )

    @pytest.mark.asyncio
    async def test_task_cancellation_on_error(self):
        """
        Verify that if _execute_one raises an exception, all remaining
        tasks are properly cancelled.
        """
        started = set()
        cancelled = set()

        class FailingQueryPlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                started.add(req.request_key)

                # Request 1 fails immediately
                if req.request_key == 1:
                    raise ValueError(f"Intentional error for request {req.request_key}")

                # Other requests take time (would complete if not cancelled)
                try:
                    await asyncio.sleep(1.0)
                    return pa.table({"key": [req.request_key], "value": ["data"]})
                except asyncio.CancelledError:
                    # Track that this task was cancelled
                    cancelled.add(req.request_key)
                    raise

        async with AsyncEarthScopeClient() as client:
            plan = FailingQueryPlan(client)

            with pytest.raises(ValueError, match="Intentional error for request 1"):
                await plan.fetch()

            # Verify behavior immediately - no sleep needed
            assert len(started) == 5, "All 5 requests should have been started"
            assert len(cancelled) == 4, (
                f"4 requests should have been cancelled, got {len(cancelled)}"
            )
            assert cancelled == {2, 3, 4, 5}, "Requests 2-5 should be cancelled"
            assert 1 not in cancelled, "Request 1 raised, not cancelled"

    @pytest.mark.asyncio
    async def test_memory_limit_not_exceeded(self):
        """
        Verify that queries under memory limit complete successfully.
        """
        async with AsyncEarthScopeClient() as client:
            plan = MyAsyncQueryPlan(client)

            # Set a high limit that won't be exceeded
            table = await plan.with_memory_limit(10_000_000).fetch()

            # Should get all data
            assert len(table) == 12
            assert set(table["key"].to_pylist()) == set(range(1, 13))

    @pytest.mark.asyncio
    async def test_memory_limit_exceeded_with_partial_data(self):
        """
        Verify that exceeding memory limit raises exception with partial table.
        """

        class LargeTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                # 8 bytes per row == 800 KB per table
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        async with AsyncEarthScopeClient() as client:
            plan = LargeTablePlan(client)

            # Set limit to ~2 MB - should get 3 tables before exceeding
            with pytest.raises(MemoryLimitExceededError) as exc_info:
                await plan.with_memory_limit(2_000_000).fetch()

            # Should have partial data
            assert exc_info.value.partial_table is not None

            # Should have some but not all data
            partial = exc_info.value.partial_table
            assert len(partial) == 300_000  # 3 tables of 100_000 rows
            assert partial.nbytes == 2_400_000  # 3 tables of 800 KB each

    @pytest.mark.asyncio
    async def test_memory_limit_different_values(self):
        """
        Verify that different memory limits produce different results.
        """

        class LargeTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 4)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        async with AsyncEarthScopeClient() as client:
            plan = LargeTablePlan(client)

            # Fetch with low limit - should fail after second table
            # Note: limit is checked AFTER adding table, so can exceed by 1 table
            with pytest.raises(MemoryLimitExceededError) as exc_info:
                await plan.with_memory_limit(1_000_000).fetch()

            # Should have partial data (2 tables: 800KB * 2 = 1.6MB total)
            partial = exc_info.value.partial_table
            assert partial is not None
            assert len(partial) == 200_000
            assert partial.nbytes == 1_600_000

            # Fetch with higher limit - should succeed
            table = await plan.with_memory_limit(10_000_000).fetch()
            assert len(table) == 300_000  # All 3 tables
            assert table.nbytes == 2_400_000  # 3 tables of 800 KB each

    @pytest.mark.asyncio
    async def test_memory_limit_last_element_succeeds(self):
        """
        Verify that if the limit is exceeded on the LAST element, we don't raise.
        """

        class LargeTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 4)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                # 8 bytes per row == 800 KB per table
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        async with AsyncEarthScopeClient() as client:
            plan = LargeTablePlan(client)

            # Set limit that will be exceeded only after all 3 tables are collected
            # 3 tables * 800 KB = 2.4 MB total, but limit is 2 MB
            # Should succeed anyway since all requests completed
            table = await plan.with_memory_limit(2_000_000).fetch()

            # Should have all data (not raise exception)
            assert len(table) == 300_000  # All 3 tables
            assert table.nbytes == 2_400_000  # 2.4 MB total

    @pytest.mark.asyncio
    async def test_memory_limit_cancels_remaining_tasks(self):
        """
        Verify that hitting memory limit cancels pending requests.
        """
        started = set()
        cancelled = set()

        class LargeTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                started.add(req.request_key)

                # Request 1 returns quickly with large table
                if req.request_key == 1:
                    data = [req.request_key] * 1_000_000
                    return pa.table({"key": data})

                # Other requests take time (should be cancelled)
                try:
                    await asyncio.sleep(5.0)  # Long enough to be cancelled
                    return pa.table({"key": [req.request_key]})
                except asyncio.CancelledError:
                    cancelled.add(req.request_key)
                    raise

        async with AsyncEarthScopeClient() as client:
            plan = LargeTablePlan(client)

            with pytest.raises(MemoryLimitExceededError) as exc_info:
                await plan.with_memory_limit(1_000_000).fetch()

            assert started == {1, 2, 3, 4, 5}
            assert cancelled == {2, 3, 4, 5}

            partial = exc_info.value.partial_table
            assert partial is not None
            assert len(partial) == 1_000_000
            assert partial.nbytes == 8_000_000

    @pytest.mark.asyncio
    async def test_timeout_not_exceeded(self):
        """
        Verify that queries under timeout complete successfully.
        """
        async with AsyncEarthScopeClient() as client:
            plan = MyAsyncQueryPlan(client)

            # Set a high timeout that won't be exceeded
            table = await plan.with_timeout(10).fetch()

            # Should get all data
            assert len(table) == 12
            assert set(table["key"].to_pylist()) == set(range(1, 13))

    @pytest.mark.asyncio
    async def test_timeout_exceeded_with_partial_data(self):
        """
        Verify that exceeding timeout raises exception with partial table.
        """

        class SlowTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                # Requests take progressively longer
                await asyncio.sleep(0.1 * req.request_key)  # 0.1s, 0.2s, 0.3s, etc.
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        async with AsyncEarthScopeClient() as client:
            plan = SlowTablePlan(client)

            # Set timeout to 0.25s - should get 2 tables before exceeding
            # (requests run in parallel so the 0.1s and 0.2s requests will complete)
            with pytest.raises(TimeoutExceededError) as exc_info:
                await plan.with_timeout(0.25).fetch()

            # Should have partial data
            assert exc_info.value.partial_table is not None
            partial = exc_info.value.partial_table
            assert len(partial) == 200_000

            # Verify exception has context
            assert exc_info.value.timeout_seconds == 0.25
            assert exc_info.value.successful_request_count == 2
            assert exc_info.value.total_request_count == 5

    @pytest.mark.asyncio
    async def test_timeout_cancels_remaining_tasks(self):
        """
        Verify that hitting timeout cancels pending requests.
        """
        started = set()
        cancelled = set()

        class SlowTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                started.add(req.request_key)

                # Request 1 returns quickly
                if req.request_key == 1:
                    data = [req.request_key] * 100_000
                    return pa.table({"key": data})

                # Other requests take time (should be cancelled by timeout)
                try:
                    await asyncio.sleep(5.0)
                    return pa.table({"key": [req.request_key]})
                except asyncio.CancelledError:
                    cancelled.add(req.request_key)
                    raise

        async with AsyncEarthScopeClient() as client:
            plan = SlowTablePlan(client)

            # Set low timeout - first request completes, then timeout hits
            with pytest.raises(TimeoutExceededError) as exc_info:
                await plan.with_timeout(0.3).fetch()

            # All started, but only request 1 completed before timeout
            assert started == {1, 2, 3, 4, 5}
            assert cancelled == {2, 3, 4, 5}

            # Should have partial data (just table 1)
            partial = exc_info.value.partial_table
            assert partial is not None
            assert len(partial) == 100_000

    @pytest.mark.asyncio
    async def test_timeout_and_memory_limit_together(self):
        """
        Verify that timeout and memory limit can be used together.
        """

        class LargeSlowTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                await asyncio.sleep(0.1)
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        async with AsyncEarthScopeClient() as client:
            plan = LargeSlowTablePlan(client)

            # Memory limit will be hit first (after 3 tables)
            with pytest.raises(MemoryLimitExceededError):
                await plan.with_memory_limit(2_000_000).with_timeout(10).fetch()

            # Timeout will be hit first (requests run concurrently)
            plan2 = LargeSlowTablePlan(client)
            with pytest.raises(TimeoutExceededError):
                await plan2.with_memory_limit(10_000_000).with_timeout(0.05).fetch()

    @pytest.mark.asyncio
    async def test_settings_defaults(self):
        """
        Verify that query plans use defaults from client settings.
        """
        from earthscope_sdk.config.settings import SdkSettings

        # Create settings with query defaults
        settings = SdkSettings(
            query_plan={
                "memory_limit_bytes": 1_000_000,
                "timeout_seconds": 5.0,
            }
        )

        async with AsyncEarthScopeClient(settings=settings) as client:
            plan = MyAsyncQueryPlan(client)

            # Verify defaults are applied
            assert plan._memory_limit_bytes == 1_000_000
            assert plan._timeout_seconds == 5.0

            # Verify fluent methods override
            plan.with_memory_limit(2_000_000)
            assert plan._memory_limit_bytes == 2_000_000
            assert plan._timeout_seconds == 5.0  # Unchanged

            plan.with_timeout(10.0)
            assert plan._memory_limit_bytes == 2_000_000  # Unchanged
            assert plan._timeout_seconds == 10.0

    @pytest.mark.asyncio
    async def test_fluent_pattern(self):
        """
        Verify that fluent methods return self for chaining.
        """
        async with AsyncEarthScopeClient() as client:
            plan = MyAsyncQueryPlan(client)
            await plan.plan()  # Build requests

            # Verify fluent methods return self
            assert plan.group_by(lambda req: req.request_key % 2) is plan
            assert len(plan.request_groups) == 2  # Grouped by even/odd

            # Reset for next test
            plan = await MyAsyncQueryPlan(client).plan()
            assert plan.with_memory_limit(1000) is plan
            assert plan._memory_limit_bytes == 1000

            # Reset for next test
            plan = await MyAsyncQueryPlan(client).plan()
            assert plan.with_timeout(30) is plan
            assert plan._timeout_seconds == 30

            # Chaining works
            plan = await MyAsyncQueryPlan(client).plan()
            result = (
                plan.group_by(lambda req: req.request_key % 2)
                .with_memory_limit(2000)
                .with_timeout(60)
            )
            assert result is plan
            assert len(plan.request_groups) == 2
            assert plan._memory_limit_bytes == 2000
            assert plan._timeout_seconds == 60


class TestSyncQueryPlan:
    def test_fetch(self):
        with EarthScopeClient() as client:
            async_plan = MyAsyncQueryPlan(client._async_client)
            plan = MySyncQueryPlan(async_plan)

            assert len(plan) == 0
            assert repr(plan) == "MySyncQueryPlan(unplanned)"

            table = plan.fetch()
            assert table == pa.table(
                {
                    "key": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    "value": [
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                    ],
                    "meta": [
                        "foo",
                        "bar",
                        "baz",
                        "qux",
                        "quux",
                        "corge",
                        "grault",
                        "garply",
                        "waldo",
                        "fred",
                        "plugh",
                        "xyzzy",
                    ],
                }
            )

    def test_iteration(self):
        with EarthScopeClient() as client:
            async_plan = MyAsyncQueryPlan(client._async_client)
            plan = MySyncQueryPlan(async_plan).plan()

            assert len(plan) == 4
            assert len(plan.request_groups) == 4

            plan.group_by(lambda r: r.request_key % 2)
            assert len(plan.request_groups) == 2

            it = iter(plan)
            t0 = next(it)
            t1 = next(it)
            with pytest.raises(StopIteration):
                next(it)

            assert t0 == pa.table(
                {
                    "key": [1, 2, 3, 7, 8, 9],
                    "value": ["a", "b", "c", "g", "h", "i"],
                    "meta": ["foo", "bar", "baz", "grault", "garply", "waldo"],
                }
            )
            assert t1 == pa.table(
                {
                    "key": [4, 5, 6, 10, 11, 12],
                    "value": ["d", "e", "f", "j", "k", "l"],
                    "meta": ["qux", "quux", "corge", "fred", "plugh", "xyzzy"],
                }
            )

    def test_memory_limit_exceeded_sync(self):
        """
        Verify memory limit works with sync wrapper.
        """

        class LargeTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                # 8 bytes per row == 800 KB per table
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        class LargeSyncQueryPlan(QueryPlan[MyReq]):
            pass

        with EarthScopeClient() as client:
            async_plan = LargeTablePlan(client._async_client)
            plan = LargeSyncQueryPlan(async_plan)

            # Set limit to ~2 MB - should get 3 tables before exceeding
            with pytest.raises(MemoryLimitExceededError) as exc_info:
                plan.with_memory_limit(2_000_000).fetch()

            # Should have partial data
            assert exc_info.value.partial_table is not None
            partial = exc_info.value.partial_table
            assert len(partial) == 300_000  # 3 tables of 100_000 rows
            assert partial.nbytes == 2_400_000  # 3 tables of 800 KB each

            # Verify exception has context
            assert exc_info.value.memory_limit_bytes == 2_000_000
            assert exc_info.value.successful_request_count == 3
            assert exc_info.value.total_request_count == 5

    def test_memory_limit_last_element_succeeds_sync(self):
        """
        Verify that if the limit is exceeded on the LAST element in sync mode, we don't raise.
        """

        class LargeTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 4)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                # 8 bytes per row == 800 KB per table
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        class LargeSyncQueryPlan(QueryPlan[MyReq]):
            pass

        with EarthScopeClient() as client:
            async_plan = LargeTablePlan(client._async_client)
            plan = LargeSyncQueryPlan(async_plan)

            # Set limit that will be exceeded only after all 3 tables are collected
            # Should succeed anyway since all requests completed
            table = plan.with_memory_limit(2_000_000).fetch()

            # Should have all data (not raise exception)
            assert len(table) == 300_000  # All 3 tables
            assert table.nbytes == 2_400_000  # 2.4 MB total

    def test_timeout_exceeded_sync(self):
        """
        Verify timeout works with sync wrapper.
        """

        class SlowTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 6)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                # Requests take increasing amounts of time
                await asyncio.sleep(0.1 * req.request_key)
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        class SlowSyncQueryPlan(QueryPlan[MyReq]):
            pass

        with EarthScopeClient() as client:
            async_plan = SlowTablePlan(client._async_client)
            plan = SlowSyncQueryPlan(async_plan)

            # Set timeout to 0.25s - should get 2 requests before timeout
            with pytest.raises(TimeoutExceededError) as exc_info:
                plan.with_timeout(0.25).fetch()

            # Should have partial data
            assert exc_info.value.partial_table is not None
            partial = exc_info.value.partial_table
            assert len(partial) == 200_000

            # Verify exception has context
            assert exc_info.value.timeout_seconds == 0.25
            assert exc_info.value.successful_request_count == 2
            assert exc_info.value.total_request_count == 5

    def test_timeout_and_memory_limit_chaining_sync(self):
        """
        Verify that timeout and memory limit can be chained in sync mode.
        """

        class LargeSlowTablePlan(AsyncQueryPlan[MyReq]):
            def __init__(self, client: AsyncEarthScopeClient):
                super().__init__(client)

            async def _build_requests(self) -> list[MyReq]:
                return [MyReq(request_key=i) for i in range(1, 4)]

            async def _execute_one(self, req: MyReq) -> pa.Table:
                await asyncio.sleep(0.1)
                data = [req.request_key] * 100_000
                return pa.table({"key": data})

        class LargeSlowSyncQueryPlan(QueryPlan[MyReq]):
            pass

        with EarthScopeClient() as client:
            async_plan = LargeSlowTablePlan(client._async_client)
            plan = LargeSlowSyncQueryPlan(async_plan)

            # Chain both limits - should succeed
            table = plan.with_memory_limit(10_000_000).with_timeout(10).fetch()
            assert len(table) == 300_000
