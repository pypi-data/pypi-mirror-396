
from logging import Logger
from logging import getLogger

from pyorthogonalrouting.Common import Integers
from pyorthogonalrouting.Common import integerListFactory

from pyorthogonalrouting.Functions import computePt
from pyorthogonalrouting.Functions import extrudeConnectorPoint
from pyorthogonalrouting.Functions import isVerticalSide
from pyorthogonalrouting.Functions import makePt

from pyorthogonalrouting.ConnectorPoint import ConnectorPoint
from pyorthogonalrouting.Functions import simplifyPaths
from pyorthogonalrouting.Line import Lines
from pyorthogonalrouting.OrthogonalConnectorByProduct import OrthogonalConnectorByProduct

from pyorthogonalrouting.OrthogonalConnectorOptions import OrthogonalConnectorOptions

from pyorthogonalrouting.Grid import Grid
from pyorthogonalrouting.Point import Point
from pyorthogonalrouting.Point import Points
from pyorthogonalrouting.Point import pointsFactory
from pyorthogonalrouting.PointGraph import GraphAndConnections
from pyorthogonalrouting.PointGraph import PointGraph

from pyorthogonalrouting.Rectangle import Rectangle
from pyorthogonalrouting.Rectangle import Rectangles
from pyorthogonalrouting.enumerations.Side import Side


class OrthogonalConnector:
    """
    https://medium.com/swlh/routing-orthogonal-diagram-connectors-in-javascript-191dc2c5ff70
    https://gist.github.com/jose-mdz/4a8894c152383b9d7a870c24a04447e4

    """

    byProduct: OrthogonalConnectorByProduct = OrthogonalConnectorByProduct()

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    # noinspection PyTypeChecker
    @classmethod
    def route(cls, options: OrthogonalConnectorOptions) -> Points:
        """

        Args:
            options:   How to run me

        Returns:  An empty list if not path is found
        """

        pointA:             ConnectorPoint = options.pointA
        pointB:             ConnectorPoint = options.pointB
        globalBoundsMargin: int            = options.globalBoundsMargin

        spots:       Points   = pointsFactory()
        verticals:   Integers = integerListFactory()
        horizontals: Integers = integerListFactory()

        sideA: Side = pointA.side
        sideB: Side = pointB.side

        sideAVertical: bool = isVerticalSide(sideA)
        sideBVertical: bool = isVerticalSide(sideB)

        originA: Point = computePt(pointA)
        originB: Point = computePt(pointB)

        shapeA:    Rectangle = Rectangle.fromRect(r=pointA.shape)
        shapeB:    Rectangle = Rectangle.fromRect(r=pointB.shape)
        bigBounds: Rectangle = Rectangle.fromRect(r=options.globalBounds)

        shapeMargin: int = options.shapeMargin

        inflatedA: Rectangle = shapeA.inflate(horizontal=shapeMargin, vertical=shapeMargin)
        inflatedB: Rectangle = shapeB.inflate(horizontal=shapeMargin, vertical=shapeMargin)

        # Check bounding boxes collision

        if inflatedA.intersects(rectangle=inflatedB):
            shapeMargin = 0
            inflatedA = shapeA
            inflatedB = shapeB

        inflatedBounds = inflatedA.union(inflatedB).inflate(globalBoundsMargin, globalBoundsMargin)

        # Curated bounds to stick to
        bounds: Rectangle = Rectangle.fromLTRB(
            left=max(inflatedBounds.left, bigBounds.left),
            top=max(inflatedBounds.top, bigBounds.top),
            right=min(inflatedBounds.right, bigBounds.right),
            bottom=min(inflatedBounds.bottom, bigBounds.bottom)
        )

        # Add edges to rulers
        for b in [inflatedA, inflatedB]:
            verticals.append(b.left)
            verticals.append(b.right)
            horizontals.append(b.top)
            horizontals.append(b.bottom)

        # Rulers at origins of shapes
        # (sideAVertical ? verticals : horizontals).push(sideAVertical ? originA.x : originA.y);
        # (sideBVertical ? verticals : horizontals).push(sideBVertical ? originB.x : originB.y);
        # Typescript is too cute

        if sideAVertical is True:
            verticals.append(originA.x)
        else:
            horizontals.append(originA.y)
        if sideBVertical is True:
            verticals.append(originB.x)
        else:
            horizontals.append(originB.y)

        # const add = (dx: number, dy: number) => spots.push(makePt(p.x + dx, p.y + dy));
        def add(pt: Point, dx: int, dy: int):
            spots.append(makePt(pt.x + dx, pt.y + dy))

        # Points of shape antennas
        for connectorPt in [pointA, pointB]:
            p: Point = computePt(p=connectorPt)
            match connectorPt.side:
                case Side.TOP:
                    add(p, dx=0, dy=-shapeMargin)
                case Side.RIGHT:
                    add(p, dx=shapeMargin, dy=0)
                case Side.BOTTOM:
                    add(p, dx=0, dy=shapeMargin)
                case Side.LEFT:
                    add(p, dx=-shapeMargin, dy=0)
                case _:
                    assert False, f'I do not understand that side {connectorPt.side=}'

        # Sort rulers
        verticals.sort()
        horizontals.sort()

        # Create grid
        grid:       Grid   = Grid.rulersToGrid(verticals=verticals, horizontals=horizontals, bounds=bounds)
        gridPoints: Points = Grid.gridToSpots(grid=grid, obstacles=Rectangles([inflatedA, inflatedB]))

        # Add to spots
        spots = Points(spots + gridPoints)

        # Create graph
        graphAndConnections: GraphAndConnections = PointGraph.createGraph(spots)
        graph:       PointGraph = graphAndConnections.graph
        connections: Lines      = graphAndConnections.connections

        # Origin and destination by extruding antennas
        origin:      Point = extrudeConnectorPoint(pointA, shapeMargin)
        destination: Point = extrudeConnectorPoint(pointB, shapeMargin)

        start: Point = computePt(pointA)
        end:   Point = computePt(pointB)

        OrthogonalConnector.byProduct.spots        = spots
        OrthogonalConnector.byProduct.vRulers      = verticals
        OrthogonalConnector.byProduct.hRulers      = horizontals
        OrthogonalConnector.byProduct.grid         = grid.rectangles
        OrthogonalConnector.byProduct.connections  = connections
        OrthogonalConnector.byProduct.diagramBounds = bigBounds

        path: Points = PointGraph.shortestPath(graph, origin, destination)

        if len(path) > 0:
            pathToSimplify: Points = Points(Points([start]) + path + Points([end]))
            return simplifyPaths(points=pathToSimplify)
        else:
            return Points([])
