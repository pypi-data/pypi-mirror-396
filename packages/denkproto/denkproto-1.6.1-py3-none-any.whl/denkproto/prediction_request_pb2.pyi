import denkproto.geometry_pb2 as _geometry_pb2
import denkproto.request_pb2 as _request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RequestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REQUEST_TYPE_UNSPECIFIED: _ClassVar[RequestType]
    STANDARD: _ClassVar[RequestType]
    OCR: _ClassVar[RequestType]
REQUEST_TYPE_UNSPECIFIED: RequestType
STANDARD: RequestType
OCR: RequestType

class OcrObject(_message.Message):
    __slots__ = ("id", "label_id", "average_width", "bounding_box", "polygon")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    average_width: float
    bounding_box: _geometry_pb2.BoundingBox
    polygon: _geometry_pb2.Polygon
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., average_width: _Optional[float] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., polygon: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ...) -> None: ...

class PredictionRequest(_message.Message):
    __slots__ = ("request_type", "id", "owned_by_group_id", "hasura_url", "created_by_user_id", "prediction_priority", "network_experiment", "image", "request_classification_interpretation", "objects")
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    OWNED_BY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    HASURA_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    PREDICTION_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    NETWORK_EXPERIMENT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_CLASSIFICATION_INTERPRETATION_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    request_type: RequestType
    id: str
    owned_by_group_id: str
    hasura_url: str
    created_by_user_id: str
    prediction_priority: int
    network_experiment: _request_pb2.NetworkExperiment
    image: _request_pb2.Image
    request_classification_interpretation: bool
    objects: _containers.RepeatedCompositeFieldContainer[OcrObject]
    def __init__(self, request_type: _Optional[_Union[RequestType, str]] = ..., id: _Optional[str] = ..., owned_by_group_id: _Optional[str] = ..., hasura_url: _Optional[str] = ..., created_by_user_id: _Optional[str] = ..., prediction_priority: _Optional[int] = ..., network_experiment: _Optional[_Union[_request_pb2.NetworkExperiment, _Mapping]] = ..., image: _Optional[_Union[_request_pb2.Image, _Mapping]] = ..., request_classification_interpretation: bool = ..., objects: _Optional[_Iterable[_Union[OcrObject, _Mapping]]] = ...) -> None: ...
