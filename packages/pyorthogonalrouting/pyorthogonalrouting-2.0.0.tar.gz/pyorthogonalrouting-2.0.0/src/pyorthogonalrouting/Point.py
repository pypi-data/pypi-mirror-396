
from typing import List
from typing import NewType

from dataclasses import dataclass
from typing import Tuple
from typing import cast

from pyorthogonalrouting.Common import NOT_SET_INT


@dataclass(eq=True)
class Point:
    """
    A point in space.
    """
    x: int = NOT_SET_INT
    y: int = NOT_SET_INT

    def toTuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))


Points = NewType('Points', List[Point])


def pointsFactory() -> Points:
    return Points([])


NO_POINT: Point = cast(Point, None)
