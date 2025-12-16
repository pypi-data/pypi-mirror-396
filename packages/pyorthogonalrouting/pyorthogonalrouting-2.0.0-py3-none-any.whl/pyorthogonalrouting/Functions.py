
from math import sqrt

from pyorthogonalrouting.ConnectorPoint import ConnectorPoint

from pyorthogonalrouting.Point import Point
from pyorthogonalrouting.Point import Points
from pyorthogonalrouting.PointNode import Distance

from pyorthogonalrouting.Rectangle import Rectangle
from pyorthogonalrouting.enumerations.BendDirection import BendDirection

from pyorthogonalrouting.enumerations.Side import Side


def distance(a: Point, b: Point) -> Distance:

    intDistance: int = round(sqrt(pow(b.x - a.x, 2) + pow(b.y - a.y, 2)))

    return Distance(intDistance)


def isVerticalSide(side: Side) -> bool:
    """

    Args:
        side:

    Returns: 'True' if the side belongs on the vertical axis, else it returns 'False'
    """
    return side == Side.TOP or side == Side.BOTTOM


def makePt(x: int, y: int) -> Point:
    """
    Utility Point creator

    Args:
        x:
        y:

    Returns:

    """
    return Point(x=x, y=y)


def computePt(p: ConnectorPoint) -> Point:
    """
    TODO: rename to toPoint
    Args:
        p:  Gets the actual point of the connector based on the distance parameter

    Returns:

    """
    b: Rectangle = Rectangle.fromRect(p.shape)

    match p.side:
        case Side.BOTTOM:
            return makePt(b.left + round (b.width * p.distance), b.bottom)
        case Side.TOP:
            return makePt(b.left + round(b.width * p.distance), b.top)
        case Side.LEFT:
            return makePt(b.left, b.top + round(b.height * p.distance))
        case Side.RIGHT:
            return makePt(b.right, b.top + round(b.height * p.distance))
        case _:
            assert False, f'Unknown side {p.side}'


def reducePoints(points: Points) -> Points:
    """

    Args:
        points:

    Returns: Returns a list without repeated points
    """

    result: Points = Points(list(dict.fromkeys(points)))

    return result


def extrudeConnectorPoint(cp: ConnectorPoint, margin: int) -> Point:

    x, y = computePt(p=cp).toTuple()

    match cp.side:
        case Side.TOP:
            return makePt(x, y - margin)
        case Side.RIGHT:
            return makePt(x + margin, y)
        case Side.BOTTOM:
            return makePt(x, y + margin)
        case Side.LEFT:
            return makePt(x - margin, y)
        case _:
            assert False, f'Unknown side {cp.side}'


def getBendDirection(a: Point, b: Point, c: Point) -> BendDirection:

    equalX: bool = a.x == b.x and b.x == c.x
    equalY: bool = a.y == b.y and b.y == c.y

    segment1Horizontal: bool = a.y == b.y
    segment1Vertical:   bool = a.x == b.x
    segment2Horizontal: bool = b.y == c.y
    segment2Vertical:   bool = b.x == c.x

    if equalX is True or equalY is True:
        return BendDirection.NONE

    if not (segment1Vertical or segment1Horizontal) or not (segment2Vertical or segment2Horizontal):
        return BendDirection.NONE

    # Hope this is correct:
    # a if condition else b

    if segment1Horizontal and segment2Vertical:
        # return c.y > b.y ? 's' : 'n';
        return BendDirection.SOUTH if c.y > b.y else BendDirection.NORTH
    if segment1Vertical and segment2Horizontal:
        #  return c.x > b.x ? 'e' : 'w';
        return BendDirection.EAST if c.x > b.x else BendDirection.WEST

    raise ValueError('Nope')


def simplifyPaths(points: Points) -> Points:
    if len(points) <= 2:
        return points

    r: Points = Points([points[0]])
    # TODO:
    # Yeah, yeah, I know the following code is not "Pythonic";  I am doing
    # a blind TypeScript port;  Once I getting converted and appropriately
    # unit test it I can rewrite it;
    #
    for i in range(len(points)):
        cur: Point = points[i]

        if i == len(points) - 1:
            r.append(cur)
            break

        prev: Point = points[i - 1]
        nxt:  Point = points[i + 1]

        bendDirection: BendDirection = getBendDirection(prev, cur, nxt)
        if bendDirection != BendDirection.NONE:
            r.append(cur)

    return r
