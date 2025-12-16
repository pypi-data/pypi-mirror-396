
from dataclasses import dataclass

from pyorthogonalrouting.Rect import Rect
from pyorthogonalrouting.Rect import NO_RECT

from pyorthogonalrouting.ConnectorPoint import ConnectorPoint
from pyorthogonalrouting.ConnectorPoint import NO_CONNECTOR_POINT


@dataclass
class OrthogonalConnectorOptions:

    pointA:             ConnectorPoint = NO_CONNECTOR_POINT
    pointB:             ConnectorPoint = NO_CONNECTOR_POINT
    shapeMargin:        int            = 20
    globalBoundsMargin: int            = 50
    globalBounds:       Rect           = NO_RECT
