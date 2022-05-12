"""
Utilities for interacting with online calendars, mostly Google's.
"""

import calendar
import datetime
import operator as op
from functools import reduce
from typing import Dict, List, Optional

import portion as P
from gcsa.google_calendar import GoogleCalendar
import gcsa.event
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


def register_event(cal: GoogleCalendar, ev: CalendarEvent):
    """
    Push the event on Google Calendar.

    APIs don't allow creating OOO and FocusTime event type on calendar at the
    moment.
    """

    gev = gcsa.event.Event(ev.name, start=ev.start_time, end=ev.end_time, attendees=ev.attendees)
    return cal.add_event(gev)


def is_event_personal(ev: CalendarEvent) -> bool:
    return len(ev.attendees) == 1


def is_day_long_event(ev: CalendarEvent) -> bool:
    # HACK: Approximation
    return ((ev.end_time - ev.start_time).total_seconds() / 3600) >= 24


def is_event_external(ev: CalendarEvent) -> bool:
    return len({email.split("@")[1] for email in ev.attendees}) > 1


def is_event_one_on_one(ev: CalendarEvent) -> bool:
    return len(ev.attendees) == 2


def is_event_focus_time(ev: CalendarEvent) -> bool:
    return ev.other["eventType"] == "focusTime"


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


def report_events_summary(events: List[CalendarEvent]) -> Dict[str, float]:
    # Don't count day long events
    events = [ev for ev in events if not is_day_long_event(ev)]
    total_hours = calculate_time_spent(events) / 60

    external_events, internal_events = py_.partition(events, is_event_external)
    external_hours = calculate_time_spent(external_events) / 60
    personal_events, rest_events = py_.partition(internal_events, is_event_personal)
    personal_hours = calculate_time_spent(personal_events) / 60

    return {
        "total": total_hours,
        "external": external_hours,
        "personal": personal_hours,
        "1:1": calculate_time_spent([ev for ev in rest_events if is_event_one_on_one(ev)]) / 60,
        "rest": calculate_time_spent([ev for ev in rest_events if not is_event_one_on_one(ev)]) / 60
    }


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
