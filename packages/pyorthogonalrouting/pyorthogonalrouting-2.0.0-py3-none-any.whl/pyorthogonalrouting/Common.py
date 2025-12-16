
from typing import List
from typing import NewType
from typing import cast

from sys import maxsize
from sys import float_info

X_SENTINEL: int = -666
Y_SENTINEL: int = -666

WIDTH_SENTINEL:  int = -777
HEIGHT_SENTINEL: int = -777

NOT_SET_SENTINEL: int = 0xDEADBEEF

NOT_SET_BOOLEAN: bool  = cast(bool, None)
NOT_SET_INT:     int   = cast(int, None)
NOT_SET_FLOAT:   float = cast(float, None)

NO_STRING:       str  = cast(str, None)

INT_MAX:    int   = maxsize
FLOAT_MAX:  float = float_info.max

Integers = NewType('Integers', List[int])


def integerListFactory() -> Integers:
    return Integers([])
