
from typing import List
from typing import NewType
from typing import cast

from dataclasses import dataclass

from pyorthogonalrouting.Common import NOT_SET_INT
from pyorthogonalrouting.Size import Size

DELIMITER: str = ','


@dataclass
class Rect(Size):
    """
    Represents a Rectangle by location and size
    """
    left: int = NOT_SET_INT
    top:  int = NOT_SET_INT

    @classmethod
    def deSerialize(cls, value: str) -> 'Rect':

        values: List[str] = value.split(sep=DELIMITER)

        assert len(values) == 4, 'Incorrectly formatted `Rect` values'

        rect: Rect = Rect()
        rect.top    = int(values[0])
        rect.left   = int(values[1])
        rect.width  = int(values[2])
        rect.height = int(values[3])

        return rect

    def __str__(self):

        sizeStr: str = super().__str__()
        return f'{self.left}{DELIMITER}{self.top}{DELIMITER}{sizeStr}'

    def __repr__(self):
        return self.__str__()


Rects = NewType('Rects', List[Rect])


NO_RECT: Rect = cast(Rect, None)
