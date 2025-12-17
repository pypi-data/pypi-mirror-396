import denkproto.geometry_pb2 as _geometry_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FocusAreaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FOCUS_AREA_TYPE_UNSPECIFIED: _ClassVar[FocusAreaType]
    FOCUS_AREA_TYPE_NEGATIVE: _ClassVar[FocusAreaType]
    FOCUS_AREA_TYPE_IGNORE: _ClassVar[FocusAreaType]
    FOCUS_AREA_TYPE_ROI: _ClassVar[FocusAreaType]
FOCUS_AREA_TYPE_UNSPECIFIED: FocusAreaType
FOCUS_AREA_TYPE_NEGATIVE: FocusAreaType
FOCUS_AREA_TYPE_IGNORE: FocusAreaType
FOCUS_AREA_TYPE_ROI: FocusAreaType

class ClassificationAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    value: float
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class InstanceSegmentationAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "instance_segmentation_mask")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_SEGMENTATION_MASK_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    instance_segmentation_mask: _geometry_pb2.InstanceSegmentationMask
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., instance_segmentation_mask: _Optional[_Union[_geometry_pb2.InstanceSegmentationMask, _Mapping]] = ...) -> None: ...

class ObjectDetectionAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "bounding_box")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    bounding_box: _geometry_pb2.BoundingBox
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ...) -> None: ...

class OcrAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "text", "bounding_box", "polygon")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    text: str
    bounding_box: _geometry_pb2.BoundingBox
    polygon: _geometry_pb2.Polygon
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., text: _Optional[str] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., polygon: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ...) -> None: ...

class FocusArea(_message.Message):
    __slots__ = ("id", "type", "bounding_box", "polygon")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: FocusAreaType
    bounding_box: _geometry_pb2.BoundingBox
    polygon: _geometry_pb2.Polygon
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[FocusAreaType, str]] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., polygon: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ...) -> None: ...

class MaterializedMarkup(_message.Message):
    __slots__ = ("height", "width", "classification_annotations", "instance_segmentation_annotations", "object_detection_annotations", "ocr_annotations", "focus_areas")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_SEGMENTATION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    OCR_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    FOCUS_AREAS_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    classification_annotations: _containers.RepeatedCompositeFieldContainer[ClassificationAnnotation]
    instance_segmentation_annotations: _containers.RepeatedCompositeFieldContainer[InstanceSegmentationAnnotation]
    object_detection_annotations: _containers.RepeatedCompositeFieldContainer[ObjectDetectionAnnotation]
    ocr_annotations: _containers.RepeatedCompositeFieldContainer[OcrAnnotation]
    focus_areas: _containers.RepeatedCompositeFieldContainer[FocusArea]
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., classification_annotations: _Optional[_Iterable[_Union[ClassificationAnnotation, _Mapping]]] = ..., instance_segmentation_annotations: _Optional[_Iterable[_Union[InstanceSegmentationAnnotation, _Mapping]]] = ..., object_detection_annotations: _Optional[_Iterable[_Union[ObjectDetectionAnnotation, _Mapping]]] = ..., ocr_annotations: _Optional[_Iterable[_Union[OcrAnnotation, _Mapping]]] = ..., focus_areas: _Optional[_Iterable[_Union[FocusArea, _Mapping]]] = ...) -> None: ...
