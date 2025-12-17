from itertools import islice
from typing import Generator, Iterable, TypeVar, Union

T = TypeVar("T")


def batched(
    iterable: Iterable[T],
    n: int = 10,
) -> Generator[tuple[T, ...], None, None]:
    """Process an iterable as batches of size `n`

    Args:
        iterable (Iterable[T]): anything iterable
        n (Optional[int]): the size of tuples to yield

    Yields (tuple[T, ...]) tuple of size `n` elements from `iterable`

    Example:

    ```py
    my_list = [1,2,3,4,5]
    print(list(batched(my_list, 3))) # prints [(1,2,3), (4,5)]
    ```
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch


def to_list(maybe_list: Union[T, list[T], set[T]]) -> list[T]:
    """
    Coerce the argument into a list if it is not already
    """
    if isinstance(maybe_list, list):
        return maybe_list

    if isinstance(maybe_list, set):
        return list(maybe_list)

    return [maybe_list]


def to_set(maybe_set: Union[T, list[T], set[T]]) -> set[T]:
    """
    Coerce the argument into a set if it is not already
    """
    if isinstance(maybe_set, set):
        return maybe_set

    if isinstance(maybe_set, list):
        return set(maybe_set)

    return {maybe_set}
