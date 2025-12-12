from datetime import datetime
from typing import Any

from ..core import Expecting


class ExpectingDateTimeFormat(Expecting):

    def __init__(self, expected: str) -> None:
        self.expected = expected

    def __repr__(self):
        return f'~= <datetime as "{self.expected}">'

    def __eq__(self, other: Any) -> bool:
        try:
            datetime.strptime(other, self.expected)
            return True
        except (ValueError, TypeError):
            return False


def iso8601_full() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m-%dT%H:%M:%S.%f%z')


def iso8601_millisecond() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m-%dT%H:%M:%S.%f')


def iso8601_second() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m-%dT%H:%M:%S')


def iso8601_minute() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m-%dT%H:%M')


def iso8601_hour() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m-%dT%H')


def iso8601_day() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m-%d')


def iso8601_month() -> Expecting:
    return ExpectingDateTimeFormat('%Y-%m')


def iso8601_year() -> Expecting:
    return ExpectingDateTimeFormat('%Y')
