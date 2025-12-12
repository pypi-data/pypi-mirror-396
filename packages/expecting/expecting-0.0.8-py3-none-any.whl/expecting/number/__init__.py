import operator
import sys
from decimal import Decimal
from typing import Callable, Literal, Union, Any

from expecting.core import Expecting, LambdaExpecting

SupportedOperation = Union[
    Literal['>=']
  , Literal['<=']
  , Literal['>']
  , Literal['<']
  , Literal['==']
  , Literal['!=']
]

KnownNumberType = Union[int, float, Decimal]


class ExpectingNumber(Expecting):
    def __init__(self, op: SupportedOperation, right_side: KnownNumberType):
        self.op = op
        self.right_side = right_side

    def resolve_op(self) -> Callable[[KnownNumberType, KnownNumberType], bool]:
        if self.op == '>=':
            return operator.ge
        elif self.op == '<=':
            return operator.le
        elif self.op == '>':
            return operator.gt
        elif self.op == '<':
            return operator.lt
        elif self.op == '==':
            return operator.eq
        elif self.op == '!=':
            return operator.ne

    def __eq__(self, other):
        if not isinstance(other, KnownNumberType if sys.version_info[:2] > (3, 9) else (int, float, Decimal)):
            return False

        return self.resolve_op()(other, self.right_side)

    def __repr__(self) -> str:
        return f'~= <number {self.op} {self.right_side}>'


def any() -> Expecting:
    def is_float(target: Any) -> bool:
        try:
            float(target)
            return True
        except (ValueError, TypeError):
            return False
    return LambdaExpecting(
        eqcheck=is_float,
        repr=lambda: '~= <a valid number representation>',
    )


def ge(right: KnownNumberType) -> ExpectingNumber:
    return ExpectingNumber('>=', right)


def le(right: KnownNumberType) -> ExpectingNumber:
    return ExpectingNumber('<=', right)


def gt(right: KnownNumberType) -> ExpectingNumber:
    return ExpectingNumber('>', right)


def lt(right: KnownNumberType) -> ExpectingNumber:
    return ExpectingNumber('<', right)


def eq(right: KnownNumberType) -> ExpectingNumber:
    return ExpectingNumber('==', right)


def ne(right: KnownNumberType) -> ExpectingNumber:
    return ExpectingNumber('!=', right)


__all__ = [
    'ge',
    'le',
    'gt',
    'lt',
    'eq',
    'ne',
]
