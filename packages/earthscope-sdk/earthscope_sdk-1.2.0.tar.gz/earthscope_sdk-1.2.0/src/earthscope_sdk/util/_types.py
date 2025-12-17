from typing import TypeVar, Union

T = TypeVar("T")

ListOrItem = Union[list[T], T]
