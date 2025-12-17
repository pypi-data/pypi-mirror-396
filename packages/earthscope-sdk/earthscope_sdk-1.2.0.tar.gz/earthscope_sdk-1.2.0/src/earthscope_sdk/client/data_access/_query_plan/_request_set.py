from copy import copy
from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

from typing_extensions import Self

from earthscope_sdk.util._itertools import batched

Req = TypeVar("Req")
"""
A request type.
"""

GroupByPredicate = Callable[[Req], Any]
"""
A function that takes a request and returns a value to group by.
"""

SortByPredicate = Callable[[Req], Any]
"""
A function that takes a request and returns a value to sort by.
"""


class RequestSet(Generic[Req]):
    """
    A set of requests.
    """

    @property
    def all_requests(self) -> list[Req]:
        """
        All requests in the request set.
        """
        return self.__args

    @property
    def request_groups(self) -> list[list[Req]]:
        """
        Groups of requests in the request set.
        """
        return self.__groups

    def __init__(self, args: Optional[list[Req]] = None):
        self.__args: list[Req] = []
        self.__groups: list[list[Req]] = []

        self.__group_by_key: Optional[GroupByPredicate[Req]] = None
        self.__sort_by_key: Optional[SortByPredicate[Req]] = None

        self._replace_requests(args or [])

    def __iter__(self) -> Iterator[list[Req]]:
        return iter(self.__groups)

    def __len__(self) -> int:
        return len(self.__args)

    def __repr__(self) -> str:
        return self._repr(self.__class__)

    ##########################################################################
    # Protected methods
    ##########################################################################

    def _repr(self, cls: type[Self]) -> str:
        """
        Common representation of the request set across sync and async subclasses.
        """
        return (
            f"{cls.__name__}(requests={len(self.__args)}, groups={len(self.__groups)})"
        )

    def _replace_requests(self, args: list[Req]) -> Self:
        """
        Replace the entire request set with a new list of requests.

        Sorting and grouping are applied to the new list of requests if previously
        configured.
        """
        # shallow copy to avoid mutating the original list
        self.__args = copy(args)

        # sort before grouping to ensure ordering is preserved within groups
        if self.__sort_by_key:
            self.sort_by(key=self.__sort_by_key)

        if self.__group_by_key:
            self.group_by(key=self.__group_by_key)
        else:
            self.__groups = [list(b) for b in batched(self.__args, 1)]

        return self

    ##########################################################################
    # Public methods
    ##########################################################################

    def group_by(self, key: GroupByPredicate[Req]) -> Self:
        """
        Group requests by the given key.

        Args:
            key: A function that takes a request and returns a value to group by.
        """
        by_key: dict[Any, list[Req]] = {}

        for arg in self.__args:
            k = key(arg)
            by_key.setdefault(k, []).append(arg)

        self.__groups = list(by_key.values())

        # Hold onto the group key for in-place replacement
        self.__group_by_key = key

        return self

    def sort_by(self, key: SortByPredicate[Req], *, reverse: bool = False) -> Self:
        """
        Sort requests by the given key.

        Args:
            key: A function that takes a request and returns a value to sort by.
            reverse: Whether to sort in reverse order.
        """
        self.__args.sort(key=key, reverse=reverse)
        for b in self.__groups:
            b.sort(key=key, reverse=reverse)

        # Hold onto the sort key for in-place replacement
        self.__sort_by_key = key

        return self
