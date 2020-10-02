import datetime
from dataclasses import dataclass


@dataclass
class SlackUser:
    id: str
    name: str


@dataclass
class SlackMessage:
    """
    Type representing a slack message. This has sufficient information to
    derive actions from it if needed.
    """

    message: str
    channel: str
    thread_ts: str = None


@dataclass
class CalendarEvent:
    """
    A Google calendar event.
    """

    pass


@dataclass
class SlackMessageAction:
    """
    An action to be taken by sending a message on slack.
    """

    scheduled: datetime.datetime
    message: str
    channel: str
    thread_ts: str = None
