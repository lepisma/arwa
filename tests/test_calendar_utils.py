import datetime as dt
from typing import Tuple

import pytest
from arwa.calendar_utils import is_overlapping
from arwa.types import CalendarEvent

TimeRange = Tuple[dt.datetime, dt.datetime]


@pytest.mark.parametrize("range_a, range_b, overlap", [
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     True),
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 4, 16, 19), dt.datetime(2021, 4, 16, 20)),
     False),
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 4, 16, 17), dt.datetime(2021, 4, 16, 18)),
     False),
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 2, 16, 18), dt.datetime(2021, 2, 16, 19)),
     False),
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 4, 16, 18, 40), dt.datetime(2021, 4, 16, 20)),
     True),
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 4, 16, 17, 40), dt.datetime(2021, 4, 16, 18, 30)),
     True),
    ((dt.datetime(2021, 4, 16, 18), dt.datetime(2021, 4, 16, 19)),
     (dt.datetime(2021, 4, 16, 18, 40), dt.datetime(2021, 4, 16, 18, 50)),
     True)
])
def test_is_overlapping(range_a: TimeRange, range_b: TimeRange, overlap: bool):
    assert is_overlapping(
        CalendarEvent("", range_a[0], range_a[1], []),
        CalendarEvent("", range_b[0], range_b[1], [])
    ) == overlap
