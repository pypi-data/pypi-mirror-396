from typing import Any, Sequence

from expecting.core import Expecting

VISITED = object()


class ExpectingListUnordered(Expecting):

    def __init__(self, expected: Sequence[Any], strict: bool = True):
        self.strict = strict
        self.expected = expected

    def __repr__(self) -> str:
        return f'~= <{self.expected!r}>'

    def __eq__(self, current: Any) -> bool:
        if not isinstance(current, (list, tuple)):
            return False

        expected = [e for e in self.expected]
        current = [e for e in current]

        for i, element in enumerate(expected):
            if element is VISITED:
                continue

            count_expected = 1
            count_other = 0

            for j, other_element in enumerate(expected[i+1:]):
                if other_element is VISITED:
                    continue

                if element == other_element:
                    count_expected += 1
                    expected[j] = VISITED

            for j, other_element in enumerate(current):
                if other_element is VISITED:
                    continue

                if element == other_element:
                    count_other += 1
                    current[j] = VISITED

            if self.strict and count_expected != count_other:
                return False

            if count_other == 0:
                return False

        if self.strict:
            for element in current:
                if element is not VISITED:
                    return False

        return True


def containing(elements: Sequence[Any]) -> Expecting:
    return ExpectingListUnordered(elements, strict=False)


def unordered(elements: Sequence[Any]) -> Expecting:
    return ExpectingListUnordered(elements, strict=True)


__all__ = [
    'containing',
    'unordered',
]
