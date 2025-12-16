
from typing import cast
from typing import List
from typing import NewType

from dataclasses import dataclass

from pyorthogonalrouting.Common import NOT_SET_FLOAT
from pyorthogonalrouting.Rect import NO_RECT
from pyorthogonalrouting.Rect import Rect
from pyorthogonalrouting.enumerations.Side import Side


@dataclass
class ConnectorPoint:
    """
    Represents a connection point on a routing request
    """
    shape:    Rect  = NO_RECT
    side:     Side  = Side.NOT_SET
    distance: float = NOT_SET_FLOAT


ConnectorPoints = NewType('ConnectorPoints', List[ConnectorPoint])

NO_CONNECTOR_POINT: ConnectorPoint = cast(ConnectorPoint, None)
