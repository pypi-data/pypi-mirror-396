
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from pyorthogonalrouting.Point import Point
from pyorthogonalrouting.Point import Points
from pyorthogonalrouting.Rect import Rect
from pyorthogonalrouting.Size import Size


class Rectangle:
    """
    Abstracts a Rectangle and adds geometric utilities
    """
    def __init__(self, left: int, top: int, width: int, height: int):

        self.logger: Logger = getLogger(__name__)

        self._left:   int = left
        self._top:    int  = top
        self._width:  int = width
        self._height: int = height

    @classmethod
    def empty(cls) -> 'Rectangle':
        return Rectangle(0, 0, 0, 0)

    @classmethod
    def fromRect(cls, r: Rect) -> 'Rectangle':
        return Rectangle(left=r.left, top=r.top, width=r.width, height=r.height)

    @classmethod
    def fromLTRB(cls, left: int, top: int, right: int, bottom: int) -> 'Rectangle':
        return Rectangle(left=left, top=top, width=right-left, height=bottom-top)

    @classmethod
    def getNotColliding(cls, points: Points, rectangles: 'Rectangles') -> Points:

        notColliding = [pt for pt in points if Rectangle.obstacleCollision(pt, rectangles) is False]

        return Points(notColliding)

    @classmethod
    def obstacleCollision(cls, point: Point, rectangles: 'Rectangles') -> bool:
        """
        Determine if the point is in any of the rectangles

        Args:
            point:
            rectangles:

        Returns:  'True' if the point in one of the rectangles, otherwise 'False'
        """
        ans: bool = False

        for r in rectangles:
            rectangle: Rectangle = cast(Rectangle, r)
            if rectangle.contains(p=point):
                ans = True
                break

        return ans

    @property
    def left(self) -> int:
        return self._left

    @property
    def top(self) -> int:
        return self._top

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def right(self) -> int:
        return self._left + self._width

    @property
    def bottom(self) -> int:
        return self._top + self._height

    @property
    def center(self) -> Point:
        return Point(x=self.left + self.width // 2, y=self.top + self.height // 2)

    @property
    def location(self) -> Point:
        return Point(x=self.left, y=self.top)

    @property
    def northEast(self) -> Point:
        return Point(x=self.right, y=self.top)

    @property
    def southEast(self) -> Point:
        return Point(x=self.right, y=self.bottom)

    @property
    def southWest(self) -> Point:
        return Point(x=self.left, y=self.bottom)

    @property
    def northWest(self) -> Point:
        return Point(x=self.left, y=self.top)

    @property
    def east(self) -> Point:
        return Point(x=self.right, y=self.center.y)

    @property
    def north(self) -> Point:
        return Point(x=self.center.x, y=self.top)

    @property
    def south(self) -> Point:
        return Point(x=self.center.x, y=self.bottom)

    @property
    def west(self) -> Point:
        return Point(x=self.left, y=self.center.y)

    @property
    def size(self) -> Size:
        return Size(width=self.width, height=self.height)

    # noinspection PyChainedComparisons
    def contains(self, p: Point) -> bool:
        return p.x >= self._left and p.x <= self.right and p.y >= self._top and p.y <= self.bottom

    def inflate(self, horizontal: int, vertical: int) -> 'Rectangle':

        return Rectangle.fromLTRB(left=self._left - horizontal,
                                  top=self._top - vertical,
                                  right=self.right + horizontal,
                                  bottom=self.bottom + vertical)

    def intersects(self, rectangle: 'Rectangle') -> bool:

        thisX: int = self._left
        thisY: int = self._top
        thisW: int = self._width
        thisH: int = self._height
        rectX: int = rectangle.left
        rectY: int = rectangle.top
        rectW: int = rectangle.width
        rectH: int = rectangle.height

        return (rectX < thisX + thisW) and (thisX < (rectX + rectW)) and (rectY < thisY + thisH) and (thisY < rectY + rectH)

    def union(self, r: 'Rectangle') -> 'Rectangle':

        x = [self.left, self.right,  r.left, r.right]
        y = [self.top,  self.bottom, r.top,  r.bottom]

        return Rectangle.fromLTRB(left=min(x), top=min(y), right=max(x), bottom=max(y))

    def __eq__(self, other) -> bool:
        """

        Args:
            other:

        Returns:  True if the defined rectangles are 'functionally' equal
        """
        ans: bool = False

        if isinstance(other, Rectangle) is False:
            pass
        else:
            if self.left == other.left and self.top == other.top and self.width == other.width and self.height == other.height:
                ans = True

        return ans

    def __str__(self) -> str:
        return f'left: {self.left}, top: {self.top}, width: {self.width}, height: {self.height}'

    def __repr__(self) -> str:
        return self.__str__()


Rectangles = NewType('Rectangles', List[Rectangle])

NO_RECTANGLE = cast(Rectangle, None)


def rectanglesFactory() -> Rectangles:
    return Rectangles([])
