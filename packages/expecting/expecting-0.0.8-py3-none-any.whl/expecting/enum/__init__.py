from enum import Enum
from typing import Type

from expecting.core import Expecting, LambdaExpecting


def any_value_of(enum: Type[Enum]) -> Expecting:
    return LambdaExpecting(
        eqcheck=lambda value: value in [v.value for v in enum],
        repr=lambda value: f'~= <any value of {enum}>',
    )


__all__ = [
    'any_value_of',
]
