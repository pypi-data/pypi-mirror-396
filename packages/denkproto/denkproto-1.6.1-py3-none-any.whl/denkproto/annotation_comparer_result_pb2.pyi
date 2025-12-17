from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ScoreType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCORE_TYPE_UNSPECIFIED: _ClassVar[ScoreType]
    CLASSIFICATION_CORRECT: _ClassVar[ScoreType]
    DICE_SCORE: _ClassVar[ScoreType]
    AVERAGE_IOU: _ClassVar[ScoreType]
    TEXT_ACCURACY: _ClassVar[ScoreType]
SCORE_TYPE_UNSPECIFIED: ScoreType
CLASSIFICATION_CORRECT: ScoreType
DICE_SCORE: ScoreType
AVERAGE_IOU: ScoreType
TEXT_ACCURACY: ScoreType

class AnnotationComparerResult(_message.Message):
    __slots__ = ("score", "score_type")
    SCORE_FIELD_NUMBER: _ClassVar[int]
    SCORE_TYPE_FIELD_NUMBER: _ClassVar[int]
    score: float
    score_type: ScoreType
    def __init__(self, score: _Optional[float] = ..., score_type: _Optional[_Union[ScoreType, str]] = ...) -> None: ...
