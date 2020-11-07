"""
Utilities for interacting with online calendars.
"""

import datetime
from typing import List

import icalendar
from gcsa.google_calendar import GoogleCalendar
from pydash import py_

from arwa.types import CalendarEvent


def parse_icalendar_event(ev) -> CalendarEvent:
    return CalendarEvent(
        name=str(ev["SUMMARY"]),
        start_time=ev["DTSTART"].dt,
        end_time=ev["DTEND"].dt
    )


def parse_google_calendar(email_id: str, start_time: datetime.datetime, end_time: datetime.datetime) -> List[CalendarEvent]:
    """
    Parse google calendar and return events.
    """

    cal = GoogleCalendar(email_id)

    events = []
    for ev in cal[start_time:end_time]:
        name = ev.summary
        start_time = ev.start
        end_time = ev.end

        if not ev.attendees:
            # This is likely a personal event
            response_status = "accepted"
        else:
            attendee = py_.find(ev.attendees, lambda at: at.email == email_id)
            if attendee.response_status == "needsAction":
                response_status = None
            else:
                response_status = attendee.response_status

        events.append(CalendarEvent(
            name=name,
            start_time=start_time,
            end_time=end_time,
            response_status=response_status
        ))

    return events


def parse_ics(ics_file: str) -> List[CalendarEvent]:
    """
    Parse calendar events from an ics file. Only events with start and end
    times are parsed.
    """

    with open(ics_file) as fp:
        cal = icalendar.Calendar.from_ical(fp.read())

    events = []
    for it in cal.subcomponents:
        if isinstance(it, icalendar.Event) and "DTEND" in it:
            events.append(parse_icalendar_event(it))

    return events


def calculate_time_spent(events: List[CalendarEvent]) -> float:
    """
    Return total time spent (minutes) in given events taking only accepted
    events in consideration.
    """

    total = 0

    for ev in events:
        if ev.response_status and ev.response_status == "accepted":
            total += ((ev.end_time - ev.start_time).total_seconds() / 60)

    return total
