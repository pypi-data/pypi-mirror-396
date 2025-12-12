from abc import ABC
from typing import Any, Callable, Optional


class Expecting(ABC):

    def __eq__(self, other: Any) -> bool:
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class LambdaExpecting(Expecting):
    def __init__(
        self,
        eqcheck: Callable[[Any], bool],
        repr: Callable[[], str],
    ) -> None:
        self.eqcheck = eqcheck
        self.repr = repr

    def __eq__(self, other) -> bool:
        return self.eqcheck(other)

    def __repr__(self):
        return self.repr()


__all__ = [
    'Expecting',
]
