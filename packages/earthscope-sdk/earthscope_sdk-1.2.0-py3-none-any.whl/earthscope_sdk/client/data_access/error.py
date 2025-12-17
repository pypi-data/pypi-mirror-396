from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import pyarrow as pa


class MemoryLimitExceededError(MemoryError):
    """
    Raised when a query exceeds the specified memory limit.

    Attributes:
        memory_limit_bytes: The memory limit in bytes.
        successful_request_count: The number of requests that were successful.
        total_request_count: The total number of requests that were attempted.
        partial_table: Arrow table containing partial results collected
                      before the limit was exceeded. None if no results
                      were collected.
    """

    def __init__(
        self,
        *,
        memory_limit_bytes: int,
        successful_request_count: int,
        total_request_count: int,
        partial_table: Optional["pa.Table"] = None,
    ):
        super().__init__("Memory limit exceeded")
        self.memory_limit_bytes = memory_limit_bytes
        self.successful_request_count = successful_request_count
        self.total_request_count = total_request_count
        self.partial_table = partial_table


class TimeoutExceededError(TimeoutError):
    """
    Raised when a query exceeds the specified timeout.

    Attributes:
        timeout_seconds: The timeout in seconds.
        successful_request_count: The number of requests that were successful.
        total_request_count: The total number of requests that were attempted.
        partial_table: Arrow table containing partial results collected
                      before the timeout was exceeded. None if no results
                      were collected.
    """

    def __init__(
        self,
        *,
        timeout_seconds: float,
        successful_request_count: int,
        total_request_count: int,
        partial_table: Optional["pa.Table"] = None,
    ):
        super().__init__("Query timeout exceeded")
        self.timeout_seconds = timeout_seconds
        self.successful_request_count = successful_request_count
        self.total_request_count = total_request_count
        self.partial_table = partial_table
