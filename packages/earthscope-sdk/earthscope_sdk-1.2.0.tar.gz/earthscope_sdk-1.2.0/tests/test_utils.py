import datetime as dt

import pytest

from earthscope_sdk.util._itertools import batched, to_list, to_set
from earthscope_sdk.util._time import time_range_periods


class TestTimeRangePeriods:
    @pytest.mark.parametrize(
        "start, end, period, expected",
        [
            (
                dt.datetime(2025, 1, 1),
                dt.datetime(2025, 1, 10),
                dt.timedelta(days=1),
                [
                    (dt.datetime(2025, 1, 1), dt.datetime(2025, 1, 2)),
                    (dt.datetime(2025, 1, 2), dt.datetime(2025, 1, 3)),
                    (dt.datetime(2025, 1, 3), dt.datetime(2025, 1, 4)),
                    (dt.datetime(2025, 1, 4), dt.datetime(2025, 1, 5)),
                    (dt.datetime(2025, 1, 5), dt.datetime(2025, 1, 6)),
                    (dt.datetime(2025, 1, 6), dt.datetime(2025, 1, 7)),
                    (dt.datetime(2025, 1, 7), dt.datetime(2025, 1, 8)),
                    (dt.datetime(2025, 1, 8), dt.datetime(2025, 1, 9)),
                    (dt.datetime(2025, 1, 9), dt.datetime(2025, 1, 10)),
                ],
            ),
            (
                dt.datetime(2025, 1, 1),
                dt.datetime(2025, 1, 10),
                dt.timedelta(days=2),
                [
                    (dt.datetime(2025, 1, 1), dt.datetime(2025, 1, 3)),
                    (dt.datetime(2025, 1, 3), dt.datetime(2025, 1, 5)),
                    (dt.datetime(2025, 1, 5), dt.datetime(2025, 1, 7)),
                    (dt.datetime(2025, 1, 7), dt.datetime(2025, 1, 9)),
                    (dt.datetime(2025, 1, 9), dt.datetime(2025, 1, 10)),
                ],
            ),
        ],
    )
    def test_time_range_periods(self, start, end, period, expected):
        periods = list(
            time_range_periods(
                start=start,
                end=end,
                period=period,
            )
        )
        assert periods == expected


class TestBatched:
    _iterable = [1, 2, 3, 4, 5]

    @pytest.mark.parametrize(
        "batch_size, expected",
        [
            (1, [(1,), (2,), (3,), (4,), (5,)]),
            (2, [(1, 2), (3, 4), (5,)]),
            (3, [(1, 2, 3), (4, 5)]),
            (4, [(1, 2, 3, 4), (5,)]),
            (5, [(1, 2, 3, 4, 5)]),
            (6, [(1, 2, 3, 4, 5)]),
            (100, [(1, 2, 3, 4, 5)]),
        ],
    )
    def test_batched(self, batch_size, expected):
        assert list(batched(self._iterable, batch_size)) == expected


class TestToList:
    @pytest.mark.parametrize(
        "input, expected",
        [
            (1, [1]),
            ([1, 2, 3], [1, 2, 3]),
            (set([1, 2, 3]), [1, 2, 3]),
        ],
    )
    def test_to_list(self, input, expected):
        assert to_list(input) == expected


class TestToSet:
    @pytest.mark.parametrize(
        "input, expected",
        [
            (1, {1}),
            ([1, 2, 3], {1, 2, 3}),
            (set([1, 2, 3]), {1, 2, 3}),
        ],
    )
    def test_to_set(self, input, expected):
        assert to_set(input) == expected
