import datetime as dt
from datetime import timezone
from typing import NamedTuple, TypeVar

T = TypeVar("T")


class TimePeriod(NamedTuple):
    """
    A time period.

    Attributes:
        start (datetime): Start datetime.
        end (datetime): End datetime.
    """

    start: dt.datetime
    end: dt.datetime

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"[{self.start}, {self.end})"

    @property
    def duration(self) -> dt.timedelta:
        return self.end - self.start


def time_range_periods(start: dt.datetime, end: dt.datetime, period: dt.timedelta):
    """
    Generate time ranges between start and end broken into periods of size 'period'.

    Args:
        start (datetime): Start datetime.
        end (datetime): End datetime.
        period (timedelta): Size of each time period.

    Yields:
        TimePeriod: Start and end of each period.
    """
    current = start
    while current < end:
        next_time = min(current + period, end)
        yield TimePeriod(start=current, end=next_time)
        current = next_time


def to_utc_dt(dt: dt.datetime) -> dt.datetime:
    """
    Convert a datetime to an aware datetime in the UTC timezone.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)
