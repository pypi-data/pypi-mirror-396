
from typing import Dict
from typing import NewType
from typing import Set
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass
from dataclasses import field
from pyorthogonalrouting.Common import INT_MAX
from pyorthogonalrouting.Common import Integers
from pyorthogonalrouting.Line import Line
from pyorthogonalrouting.Line import Lines
from pyorthogonalrouting.Functions import distance
from pyorthogonalrouting.Line import linesFactory

from pyorthogonalrouting.Point import Point
from pyorthogonalrouting.Point import Points

from pyorthogonalrouting.PointNode import NO_POINT_NODE
from pyorthogonalrouting.PointNode import PointNode
from pyorthogonalrouting.PointNode import PointNodes

from pyorthogonalrouting.enumerations.Direction import Direction

XStr = NewType('XStr', str)
YStr = NewType('YStr', str)

YToPointNodeDict = NewType('YToPointNodeDict', Dict[YStr, PointNode])
XToYDict         = NewType('XToYDict',         Dict[XStr, YToPointNodeDict])

PointNodeSet     = Set[PointNode]
PointNodeDict    = NewType('PointNodeDict', Dict[Point, PointNode])


@dataclass
class GraphAndConnections:
    graph:       'PointGraph' = cast('PointGraph', None)
    connections: Lines        = field(default_factory=linesFactory)


class PointNotFoundException(Exception):
    pass


class PointNodeNotFoundException(Exception):
    pass


class PointGraph:
    """
    Represents a Graph of Point nodes
    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._index: XToYDict = XToYDict({})

    @classmethod
    def createGraph(cls, spots: Points) -> GraphAndConnections:
        """
        Creates a graph connecting the specified points orthogonally

        Args:
            spots:

        Returns:
        """
        hotXs:       Integers   = Integers([])
        hotYs:       Integers   = Integers([])
        graph:       PointGraph = PointGraph()
        connections: Lines      = linesFactory()

        for point in spots:
            p: Point = cast(Point, point)
            x, y = p.toTuple()

            if x not in hotXs:
                hotXs.append(x)
            if y not in hotYs:
                hotYs.append(y)
            graph.add(p=p)

        # graph._debugIndex()
        hotXs.sort()
        hotYs.sort()

        def inHotIndex(pt: Point) -> bool:
            return graph.has(pt)

        # TODO:
        # Yeah, yeah, I know the following code is not "Pythonic";  I am doing
        # a blind TypeScript port;  Once I getting converted and appropriately
        # unit test it I can rewrite it;
        #
        for i in range(len(hotYs)):
            for j in range(len(hotXs)):
                b: Point = Point(x=hotXs[j], y=hotYs[i])

                if inHotIndex(b) is False:
                    continue
                if j > 0:
                    a: Point = Point(x=hotXs[j - 1], y=hotYs[i])
                    if inHotIndex(a) is True:
                        graph.connect(a, b)
                        graph.connect(b, a)
                        connections.append(Line(a=a, b=b))
                if i > 0:
                    a = Point(x=hotXs[j], y=hotYs[i - 1])
                    if inHotIndex(a) is True:
                        graph.connect(a, b)
                        graph.connect(b, a)
                        connections.append(Line(a=a, b=b))

        # graph._debugIndex()
        # graph.logger.info(f'{connections}')

        return GraphAndConnections(graph=graph, connections=connections)

    @classmethod
    def shortestPath(cls, graph: 'PointGraph', origin: Point, destination: Point) -> Points:
        """
        TODO: Not unit tested, yet.

        Args:
            graph:
            origin:
            destination:

        Returns:
        """

        originNode:      PointNode = graph.get(origin)
        destinationNode: PointNode = graph.get(destination)

        if originNode is None:
            raise PointNodeNotFoundException(f'Origin Node {origin} not found')
        if destinationNode is None:
            raise PointNodeNotFoundException(f'Destination Node {destination} not found')

        graph.calculateShortestPathFromSource(graph=graph, source=originNode)

        pointNodes: PointNodes = destinationNode.shortestPath
        points:     Points = Points([pointNode.data for pointNode in pointNodes])

        return points

    def add(self, p: Point):

        xs, ys = self._pointToString(p=p)

        if xs not in self._index.keys():
            self._index[xs] = YToPointNodeDict({})

        yToPointNodeDict: YToPointNodeDict = self._index[xs]
        if ys not in yToPointNodeDict.keys():
            yToPointNodeDict[ys] = PointNode(data=p)

        self.logger.debug(f'Add of {p=} complete {self._index=}')

    def has(self, p: Point) -> bool:

        xs, ys = self._pointToString(p=p)

        return xs in self._index and ys in self._index[xs]

    def connect(self, a: Point, b: Point):
        """

        Args:
            a:
            b:
        """
        nodeA: PointNode = self.get(p=a)
        nodeB: PointNode = self.get(p=b)
        if nodeA == NO_POINT_NODE:
            raise PointNotFoundException(f'No Point a: {a=}')
        if nodeB == NO_POINT_NODE:
            raise PointNotFoundException(f'No Point b: {b=}')

        nodeA.adjacentNodes[nodeB] = distance(a=a, b=b)

    def get(self, p: Point) -> PointNode:
        """
        Retrieve the PointNode associated with the Point

        Args:
            p:

        Returns:  May return None
        """
        xs, ys = self._pointToString(p=p)
        if self.has(p) is True:
            return self._index[xs][ys]

        return NO_POINT_NODE

    def calculateShortestPathFromSource(self, graph: 'PointGraph', source: PointNode) -> 'PointGraph':

        source.distance = 0
        settledNodes:   PointNodeSet  = set()
        #
        # TODO:
        # Yeah, had to use a dictionary here to track unsettled nodes;  Seems like a bug in
        # how the set object was removing an incorrect node, which resulted in an error
        # Need to look at this sometime in the future
        #
        unSettledNodes: PointNodeDict = PointNodeDict({})

        unSettledNodes[source.data] = source

        while len(unSettledNodes) != 0:
            currentNode: PointNode = self._getLowestDistanceNode(unSettledNodes)
            # self.logger.info(f'{currentNode=}')
            # unSettledNodes.remove(currentNode)
            del unSettledNodes[currentNode.data]
            # unSettledNodes.discard(currentNode)

            for adjacentNode, edgeWeight in currentNode.adjacentNodes.items():
                if adjacentNode not in settledNodes:
                    self._calculateMinimumDistance(evaluationNode=adjacentNode, edgeWeight=edgeWeight, sourceNode=currentNode)
                    unSettledNodes[adjacentNode.data] = adjacentNode
            settledNodes.add(currentNode)

        return graph

    def _inferPathDirection(self, node: PointNode) -> Direction:
        if len(node.shortestPath) == 0:
            return Direction.UNKNOWN

        return self._directionOfNodes(a=node.shortestPath[len(node.shortestPath) - 1], b=node)

    def _directionOfNodes(self, a: PointNode, b: PointNode) -> Direction:
        return self._directionOf(a=a.data, b=b.data)

    def _directionOf(self, a: Point, b: Point) -> Direction:
        """
        In the original JS version this method return None
        Args:
            a:
            b:

        Returns: Vertical or Horizontal;  May return unknown

        """
        if a.x == b.x:
            return Direction.HORIZONTAL
        elif a.y == b.y:
            return Direction.VERTICAL
        else:
            return Direction.UNKNOWN

    def _getLowestDistanceNode(self, unSettledNodes: PointNodeDict) -> PointNode:

        lowestDistanceNode: PointNode = cast(PointNode, None)
        lowestDistance:     int       = INT_MAX
        for n in unSettledNodes.values():
            node:         PointNode = cast(PointNode, n)
            nodeDistance: int       = node.distance
            if nodeDistance < lowestDistance:
                lowestDistance     = nodeDistance
                lowestDistanceNode = node

        self.logger.debug(f'{lowestDistanceNode=}')
        return lowestDistanceNode

    def _calculateMinimumDistance(self, evaluationNode: PointNode, edgeWeight: int, sourceNode: PointNode):

        sourceDistance:    int       = sourceNode.distance
        comingDirection:   Direction = self._inferPathDirection(sourceNode)
        goingDirection:    Direction = self._directionOfNodes(sourceNode, evaluationNode)
        #
        # Rewrite the following in a simpler to understand mechanism
        # const changingDirection = comingDirection && goingDirection && comingDirection != goingDirection;
        # extraWeigh = changingDirection ? Math.pow(edgeWeigh + 1, 2) : 0;
        if comingDirection == Direction.UNKNOWN or goingDirection == Direction.UNKNOWN:
            changingDirection: bool = False
        else:
            if comingDirection == goingDirection:
                changingDirection = False
            else:
                changingDirection = True
        if changingDirection is True:
            extraWeight: int = pow(edgeWeight + 1, 2)
        else:
            extraWeight = 0

        if sourceDistance + edgeWeight + extraWeight < evaluationNode.distance:

            evaluationNode.distance  = sourceDistance + edgeWeight + extraWeight
            # shortestPath: PointNode[] = [...sourceNode.shortestPath]
            # shortestPath: PointNodes = deepcopy(sourceNode.shortestPath)
            # shortestPath: PointNodes = copy(sourceNode.shortestPath)
            shortestPath: PointNodes = self._typeScriptSpread(sourceNode.shortestPath)

            sourceDoppleGanger: PointNode = PointNode.typeScriptCopy(sourceNode)
            # shortestPath.append(sourceNode)
            shortestPath.append(sourceDoppleGanger)
            evaluationNode.shortestPath = shortestPath

    def _pointToString(self, p: Point) -> Tuple[XStr, YStr]:

        xs: XStr = XStr(str(p.x))
        ys: YStr = YStr(str(p.y))

        return xs, ys

    def _debugIndex(self):

        lc: str = '{'   # left curly
        rc: str = '}'   # right curly

        index: XToYDict = self._index

        prettyIndex: str = f'index: {lc}'
        for xKey in index.keys():
            ytoPointNode: YToPointNodeDict = index[xKey]
            prettyIndex = f'{prettyIndex}\n\t{xKey}: {lc}'

            for yKey in ytoPointNode.keys():
                pointNode: PointNode = ytoPointNode[yKey]
                prettyIndex = f'{prettyIndex}\n\t\t{yKey:>4}: {pointNode}'

            prettyIndex = f'{prettyIndex}\n\t{rc},'

        prettyIndex = f'{prettyIndex}\n{rc}'
        self.logger.info(f'{prettyIndex}')

    def _typeScriptSpread(self, pointNodes: PointNodes) -> PointNodes:
        """
        See:
            https://stackoverflow.com/questions/50051149/does-spreading-create-shallow-copy

        Args:
            pointNodes:

        Returns:
        """

        doppleGanger: PointNodes = PointNodes([])

        for pt in pointNodes:
            duplicate: PointNode = PointNode.typeScriptCopy(pt)
            doppleGanger.append(duplicate)

        return doppleGanger
