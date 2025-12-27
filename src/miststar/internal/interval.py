# create by lesomras on 2025-12-27
# from typing import TypeVar, Generic
from typing import Union

from .int32 import Int32

class Interval32(object):
    def __init__(self, _min: Union[Int32, int] = -2147483648, _max: Union[Int32, int] = 2147483647) -> None:
        if isinstance(_min, int):
            _min = Int32(_min)
        if isinstance(_max, int):
            _max = Int32(_max)
        self._min = _min
        self._max = _max

    def __contains__(self, _value: Union[Int32, int]) -> bool:
        return self._min <= _value <= self._max


def interval32(x: Union[Int32, int] = -2147483648, y: Union[Int32, int] = 2147483647) -> Interval32:
    return Interval32(x, y)

def checking32(value: Union[Int32, int]) -> bool:
    if isinstance(value, Int32):
        return True
    return -2147483648 <= value <= 2147483647