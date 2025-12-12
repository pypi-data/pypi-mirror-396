import pathlib
from typing import Any, Union, List, Tuple, Callable, Literal, Sequence
import numpy
import pandas
from enum import Enum

from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from .Tagger import Tagger
    from .apply_tagger import TargetTagger, TargetTaggerCollection
    from .TaggerCollection import TaggerCollection

    TaggerList = Union[List[Tagger], List[TargetTagger], TaggerCollection, TargetTaggerCollection]
    AnyTaggerCollection = Union[TaggerCollection, TargetTaggerCollection]
else:
    TaggerList = Any
    AnyTaggerCollection = Any

ArrayLike = Union[numpy.ndarray, pandas.Series]
NPMatrix = List[ArrayLike]  # Numpy does not implement this as a type
NPArrayOrScalar = Union[numpy.ndarray, pandas.Series, float]

AnyList = Union[numpy.ndarray, pandas.Series, List]
PathStr = Union[pathlib.PosixPath, str]

StrOptionOrSettingsList = Union[str, Union[List, Tuple]]
TransformFunc = Callable[[float], float]
ScaleType = Union[
    Literal["asinh", "linear", "log", "logit", "symlog"],
    Tuple[TransformFunc, TransformFunc]
]

class CalibrationMode(Enum):
    Bd = "Bd"
    Bu = "Bu"
    Bs = "Bs"
    TRUEID = "TRUEID"

    @property
    def oscillation(self) -> bool:
        return self in (CalibrationMode.Bd, CalibrationMode.Bs)

    def __eq__(self, other) -> bool:
        if isinstance(other, CalibrationMode):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False
    
    def __str__(self) -> str:
        return self.value
