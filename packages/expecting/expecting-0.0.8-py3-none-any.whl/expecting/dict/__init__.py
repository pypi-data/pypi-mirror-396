from typing import Dict, Any, Union

from expecting.core import Expecting


class ExpectingDictContaining(Expecting):
    def __init__(self, expected: Dict[Any, Union[Any, Expecting]]) -> None:
        self.expected = expected

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, dict):
            return False

        for key, value in self.expected.items():
            if key not in other:
                return False

            if other[key] != value:
                return False

        return True

    def __repr__(self) -> str:
        return f"~= <{self.expected!r}>"


def containing(expected: Dict[Any, Union[Any, Expecting]]) -> Expecting:
    return ExpectingDictContaining(expected)


__all__ = [
    'containing',
]
