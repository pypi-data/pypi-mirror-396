
from logging import Logger
from logging import getLogger

from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions

from codeallybasic.SecureConversions import SecureConversions

from codeallybasic.SingletonV3 import SingletonV3

from pyorthogonalrouting.Rect import Rect

DEFAULT_SHAPE_MARGIN:              str  = '20'
DEFAULT_GLOBAL_BOUNDS_MARGIN:      str  = '50'
DEFAULT_SOURCE_EDGE_DISTANCE:      str  = '0.5'
DEFAULT_DESTINATION_EDGE_DISTANCE: str  = '0.5'
DEFAULT_GLOBAL_BOUNDS:             str  = Rect(left=0, top=0, width=500, height=500).__str__()

#         ConfigurationNameValue(name=PropertyName('destinationEdgeDistance'), defaultValue=DEFAULT_DESTINATION_EDGE_DISTANCE),

sectionMain: ValueDescriptions = ValueDescriptions(
    {
        KeyName('shapeMargin'):             ValueDescription(defaultValue=DEFAULT_SHAPE_MARGIN,              deserializer=SecureConversions.secureInteger),
        KeyName('globalBoundsMargin'):      ValueDescription(defaultValue=DEFAULT_GLOBAL_BOUNDS_MARGIN,      deserializer=SecureConversions.secureInteger),
        KeyName('globalBounds'):            ValueDescription(defaultValue=DEFAULT_GLOBAL_BOUNDS,             deserializer=Rect.deSerialize),
        KeyName('sourceEdgeDistance'):      ValueDescription(defaultValue=DEFAULT_SOURCE_EDGE_DISTANCE,      deserializer=SecureConversions.secureFloat),
        KeyName('destinationEdgeDistance'): ValueDescription(defaultValue=DEFAULT_DESTINATION_EDGE_DISTANCE, deserializer=SecureConversions.secureFloat),
    }
)

PY_ORTHOGONAL_ROUTING_SECTIONS: Sections = Sections(
    {
        SectionName('Main'): sectionMain,
    }
)


class Configuration(DynamicConfiguration, metaclass=SingletonV3):

    def __init__(self):
        """
        Make the logger protected to avoid infinite access loop in Dynamic Configuration
        """
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName='pyorthogonalrouting.ini', moduleName='pyorthogonalrouting', sections=PY_ORTHOGONAL_ROUTING_SECTIONS)
