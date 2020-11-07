"""
Utilities for interacting with online calendars.
"""

from typing import List

import icalendar

from arwa.types import CalendarEvent


def parse_icalendar_event(ev) -> CalendarEvent:
    return CalendarEvent(
        name=str(ev["SUMMARY"]),
        organizer=ev.get("ORGANIZER"),
        start_time=ev["DTSTART"].dt,
        end_time=ev["DTEND"].dt
    )


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
