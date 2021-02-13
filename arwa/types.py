import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(eq=True, frozen=True)
class SlackUser:
    id: str
    name: str
    is_bot: bool = False
    is_deleted: bool = False
    email: Optional[str] = None


@dataclass
class SlackMessage:
    """
    Type representing a slack message. This has sufficient information to
    derive actions from it if needed.
    """

    message: str
    channel: str
    thread_ts: Optional[str] = None


@dataclass
class CalendarEvent:
    """
    A time blocked calendar event.
    """

    name: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    response_status: Optional[str] = None


@dataclass
class SlackMessageAction:
    """
    An action to be taken by sending a message on slack.
    """

    scheduled: datetime.datetime
    message: str
    channel: str
    thread_ts: Optional[str] = None
