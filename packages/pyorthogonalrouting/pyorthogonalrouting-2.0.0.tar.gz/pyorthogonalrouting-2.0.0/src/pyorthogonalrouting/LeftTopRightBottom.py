
from dataclasses import dataclass

from pyorthogonalrouting.Common import NOT_SET_INT


@dataclass
class LeftTopRightBottom:

    left:   int = NOT_SET_INT
    top:    int = NOT_SET_INT
    right:  int = NOT_SET_INT
    bottom: int = NOT_SET_INT
