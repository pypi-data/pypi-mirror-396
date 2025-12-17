from typing import NamedTuple

import pytest

from earthscope_sdk.client.data_access._query_plan._request_set import RequestSet
from earthscope_sdk.util._itertools import batched


class MyReq(NamedTuple):
    foo: int
    bar: str


test_reqs = [
    MyReq(foo=11, bar="aa"),
    MyReq(foo=12, bar="ab"),
    MyReq(foo=23, bar="bb"),
    MyReq(foo=24, bar="ac"),
    MyReq(foo=35, bar="bc"),
]


class TestRequestSet:
    def test_basic_behavior(self):
        req_set = RequestSet(test_reqs)
        single_groups = list(list(b) for b in batched(test_reqs, 1))

        assert req_set.all_requests == test_reqs
        assert req_set.request_groups == single_groups

        assert len(req_set) == 5
        assert repr(req_set) == "RequestSet(requests=5, groups=5)"

        for g, e in zip(req_set.request_groups, single_groups):
            assert g == e

    @pytest.mark.parametrize(
        "group_by, expected_groups",
        [
            (
                lambda r: r.foo // 10,
                [
                    [test_reqs[0], test_reqs[1]],
                    [test_reqs[2], test_reqs[3]],
                    [test_reqs[4]],
                ],
            ),
            (
                lambda r: r.bar[0],
                [
                    [test_reqs[0], test_reqs[1], test_reqs[3]],
                    [test_reqs[2], test_reqs[4]],
                ],
            ),
            (
                lambda r: r.bar[1],
                [
                    [test_reqs[0]],
                    [test_reqs[1], test_reqs[2]],
                    [test_reqs[3], test_reqs[4]],
                ],
            ),
        ],
    )
    def test_grouping(self, group_by, expected_groups):
        req_set = RequestSet(test_reqs)

        req_set.group_by(group_by)
        assert req_set.request_groups == expected_groups

    @pytest.mark.parametrize(
        "sort_by, expected_order",
        [
            (
                lambda r: r.foo,
                [test_reqs[0], test_reqs[1], test_reqs[2], test_reqs[3], test_reqs[4]],
            ),
            (
                lambda r: r.bar,
                [test_reqs[0], test_reqs[1], test_reqs[3], test_reqs[2], test_reqs[4]],
            ),
            (
                lambda r: r.bar[::-1],
                [test_reqs[0], test_reqs[1], test_reqs[2], test_reqs[3], test_reqs[4]],
            ),
        ],
    )
    def test_sorting(self, sort_by, expected_order):
        req_set = RequestSet(test_reqs)
        req_set.sort_by(sort_by)
        assert req_set.all_requests == expected_order

    def test_replace_requests(self):
        req_set = RequestSet(test_reqs)
        assert req_set.all_requests == test_reqs

        req_set.group_by(lambda r: r.foo // 10)
        req_set.sort_by(lambda r: r.bar)

        new_reqs = [
            MyReq(foo=41, bar="za"),
            MyReq(foo=62, bar="zb"),
            MyReq(foo=53, bar="yb"),
            MyReq(foo=44, bar="yc"),
            MyReq(foo=45, bar="xc"),
        ]
        req_set._replace_requests(new_reqs)
        assert req_set.all_requests == [
            new_reqs[4],
            new_reqs[2],
            new_reqs[3],
            new_reqs[0],
            new_reqs[1],
        ], "Sorting was applied globally to the new requests"

        assert req_set.request_groups == [
            [new_reqs[4], new_reqs[3], new_reqs[0]],
            [new_reqs[2]],
            [new_reqs[1]],
        ], "Sorting and grouping were applied to the new requests"
