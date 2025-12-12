from typing import Any, Optional
from uuid import UUID

from expecting.core import Expecting


class ExpectingUuidHex(Expecting):

    def __init__(self, expected_version: Optional[int]):
        self.expected_version = expected_version

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, str):
            return False

        try:
            val = UUID(other)
            return self.expected_version is None or val.version == self.expected_version
        except ValueError:
            return False

    def __repr__(self) -> str:
        if self.expected_version is None:
            return '~= <UUID hex as string>'
        return f'~= <UUIDv{self.expected_version} hex as string>'


def v1() -> Expecting:
    return ExpectingUuidHex(expected_version=1)


def v3() -> Expecting:
    return ExpectingUuidHex(expected_version=3)


def v4() -> Expecting:
    return ExpectingUuidHex(expected_version=4)


def v5() -> Expecting:
    return ExpectingUuidHex(expected_version=5)


def hex() -> Expecting:
    return ExpectingUuidHex(expected_version=None)
