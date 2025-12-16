
from typing import List
from typing import NewType

from dataclasses import dataclass

from pyorthogonalrouting.Point import NO_POINT
from pyorthogonalrouting.Point import Point


@dataclass
class Line:
    """
    A line between two points.
    """
    a: Point = NO_POINT
    b: Point = NO_POINT


Lines = NewType('Lines', List[Line])


def linesFactory() -> Lines:
    return Lines([])
