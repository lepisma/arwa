"""
Utilities for interacting with online calendars.
"""

import calendar
import datetime
import operator as op
from functools import reduce
from typing import List, Optional

import portion as P
from gcsa.google_calendar import GoogleCalendar
from pydash import py_

from arwa.types import CalendarEvent


def get_last_sunday(dt=None) -> datetime.datetime:
    """
    Get last sunday for given datetime. If the current dt is Sunday, then
    return that.
    """

    dt = dt or datetime.datetime.now()
    day = dt.isoweekday()

    def _date_to_dt(d: datetime.date):
        return datetime.datetime.combine(d, datetime.datetime.min.time())

    delta = datetime.timedelta(days=day % 7)
    return _date_to_dt(dt - delta)


def get_last_day_of_month(dt=None) -> datetime.datetime:
    """
    Return last day of month for given datetime `dt`.
    """

    dt = dt or datetime.datetime.now()
    day = calendar.monthrange(dt.year, dt.month)[1]

    return dt.replace(day=day)


def parse_google_calendar(email_id: str, start_time: datetime.datetime, end_time: datetime.datetime) -> List[CalendarEvent]:
    """
    Parse google calendar and return events. End time is not inclusive.
    """

    cal = GoogleCalendar(email_id)

    events = []
    for ev in cal[start_time:end_time]:
        name = ev.summary
        start_time = ev.start
        end_time = ev.end

        if not ev.attendees:
            # This is likely a personal event
            response_status: Optional[str] = "accepted"
            attendees = [email_id]
        else:
            attendee = py_.find(ev.attendees, lambda at: at.email == email_id)
            try:
                if attendee.response_status == "needsAction":
                    response_status = None
                else:
                    response_status = attendee.response_status
            except AttributeError:
                response_status = None
            attendees = [a.email for a in ev.attendees]

        events.append(CalendarEvent(
            name=name,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            response_status=response_status
        ))

    return events


def calculate_time_spent(events: List[CalendarEvent]) -> float:
    """
    Return total time spent (minutes) in given events taking only accepted
    events in consideration.
    """

    total: float = 0

    for ev in events:
        if ev.response_status and ev.response_status == "accepted":
            total += ((ev.end_time - ev.start_time).total_seconds() / 60)

    return total


def is_overlapping(event_a: CalendarEvent, event_b: CalendarEvent) -> bool:
    """
    Tell if two events (with datetime) are overlapping.
    """

    interval_a = P.closedopen(event_a.start_time, event_a.end_time)
    interval_b = P.closedopen(event_b.start_time, event_b.end_time)

    return not (interval_a & interval_b).empty


def find_interstices(events: List[CalendarEvent]) -> List[CalendarEvent]:
    """
    Return gaps where there are no events.
    """

    # TODO: Assert for events in the same date.

    date = events[0].start_time.date()

    def _time_to_mins(t: datetime.time) -> int:
        # TODO: Handle border case
        return t.hour * 60 + t.minute

    def _mins_to_time(mins: int) -> datetime.time:
        return datetime.time(mins // 60, mins % 60)

    intervals = []
    for ev in events:
        start_time = ev.start_time.time()
        end_time = ev.end_time.time()
        intervals.append(P.closed(_time_to_mins(start_time), _time_to_mins(end_time)))

    gaps = reduce(op.or_, intervals).complement()
    gaps = [g for g in gaps if (g.lower > -P.inf) and (g.upper < P.inf)]

    return [
        CalendarEvent(
            str(i),
            start_time=datetime.datetime.combine(date, _mins_to_time(interval.lower)),
            end_time=datetime.datetime.combine(date, _mins_to_time(interval.upper)),
            attendees=[]
        )
        for i, interval in enumerate(gaps)
    ]
