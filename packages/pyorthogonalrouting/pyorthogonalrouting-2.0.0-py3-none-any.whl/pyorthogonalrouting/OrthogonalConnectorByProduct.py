
from typing import cast
from typing import List
from typing import NewType

from dataclasses import dataclass
from dataclasses import field

from pyorthogonalrouting.Common import Integers
from pyorthogonalrouting.Common import integerListFactory

from pyorthogonalrouting.Line import Lines
from pyorthogonalrouting.Line import linesFactory

from pyorthogonalrouting.Point import Points
from pyorthogonalrouting.Point import pointsFactory
from pyorthogonalrouting.Rectangle import Rectangle

from pyorthogonalrouting.Rectangle import Rectangles
from pyorthogonalrouting.Rectangle import rectanglesFactory


@dataclass
class OrthogonalConnectorByProduct:

    hRulers:       Integers   = field(default_factory=integerListFactory)
    vRulers:       Integers   = field(default_factory=integerListFactory)
    spots:         Points     = field(default_factory=pointsFactory)
    grid:          Rectangles = field(default_factory=rectanglesFactory)
    connections:   Lines      = field(default_factory=linesFactory)
    diagramBounds: Rectangle  = cast(Rectangle, None)


OrthogonalConnectorByProducts = NewType('OrthogonalConnectorByProducts', List[OrthogonalConnectorByProduct])
