from typing import List, Generic, TypeVar

T = TypeVar("T")


class PaginationResult(Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
