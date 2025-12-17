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

class CircleAnnotation(_message.Message):
    __slots__ = ("center_x", "center_y", "radius")
    CENTER_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_Y_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    center_x: int
    center_y: int
    radius: int
    def __init__(self, center_x: _Optional[int] = ..., center_y: _Optional[int] = ..., radius: _Optional[int] = ...) -> None: ...

class MagicwandAnnotation(_message.Message):
    __slots__ = ("top_left_x", "top_left_y", "width", "height", "center_x", "center_y", "points", "threshold")
    TOP_LEFT_X_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CENTER_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_Y_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    top_left_x: int
    top_left_y: int
    width: int
    height: int
    center_x: int
    center_y: int
    points: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.Point2D]
    threshold: int
    def __init__(self, top_left_x: _Optional[int] = ..., top_left_y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., center_x: _Optional[int] = ..., center_y: _Optional[int] = ..., points: _Optional[_Iterable[_Union[_geometry_pb2.Point2D, _Mapping]]] = ..., threshold: _Optional[int] = ...) -> None: ...

class PenAnnotation(_message.Message):
    __slots__ = ("top_left_x", "top_left_y", "width", "height", "points", "thickness")
    TOP_LEFT_X_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_FIELD_NUMBER: _ClassVar[int]
    top_left_x: int
    top_left_y: int
    width: int
    height: int
    points: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.Point2D]
    thickness: int
    def __init__(self, top_left_x: _Optional[int] = ..., top_left_y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., points: _Optional[_Iterable[_Union[_geometry_pb2.Point2D, _Mapping]]] = ..., thickness: _Optional[int] = ...) -> None: ...

class PixelAnnotation(_message.Message):
    __slots__ = ("data", "top_left_x", "top_left_y", "width", "height")
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_X_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    data: _geometry_pb2.BinaryMaskData
    top_left_x: int
    top_left_y: int
    width: int
    height: int
    def __init__(self, data: _Optional[_Union[_geometry_pb2.BinaryMaskData, _Mapping]] = ..., top_left_x: _Optional[int] = ..., top_left_y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class SausageAnnotation(_message.Message):
    __slots__ = ("top_left_x", "top_left_y", "width", "height", "points", "radius")
    TOP_LEFT_X_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    top_left_x: int
    top_left_y: int
    width: int
    height: int
    points: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.Point2D]
    radius: int
    def __init__(self, top_left_x: _Optional[int] = ..., top_left_y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., points: _Optional[_Iterable[_Union[_geometry_pb2.Point2D, _Mapping]]] = ..., radius: _Optional[int] = ...) -> None: ...

class ClassificationAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    value: float
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class SegmentationAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "circle_annotation", "magicwand_annotation", "pen_annotation", "pixel_annotation", "polygon_annotation", "rectangle_annotation", "sausage_annotation")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    MAGICWAND_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    PEN_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    PIXEL_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    POLYGON_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    RECTANGLE_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    SAUSAGE_ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    circle_annotation: CircleAnnotation
    magicwand_annotation: MagicwandAnnotation
    pen_annotation: PenAnnotation
    pixel_annotation: PixelAnnotation
    polygon_annotation: _geometry_pb2.Polygon
    rectangle_annotation: _geometry_pb2.BoundingBox
    sausage_annotation: SausageAnnotation
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., circle_annotation: _Optional[_Union[CircleAnnotation, _Mapping]] = ..., magicwand_annotation: _Optional[_Union[MagicwandAnnotation, _Mapping]] = ..., pen_annotation: _Optional[_Union[PenAnnotation, _Mapping]] = ..., pixel_annotation: _Optional[_Union[PixelAnnotation, _Mapping]] = ..., polygon_annotation: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ..., rectangle_annotation: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., sausage_annotation: _Optional[_Union[SausageAnnotation, _Mapping]] = ...) -> None: ...

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

class Markup(_message.Message):
    __slots__ = ("height", "width", "classification_annotations", "segmentation_annotations", "object_detection_annotations", "ocr_annotations", "focus_areas")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    SEGMENTATION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    OCR_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    FOCUS_AREAS_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    classification_annotations: _containers.RepeatedCompositeFieldContainer[ClassificationAnnotation]
    segmentation_annotations: _containers.RepeatedCompositeFieldContainer[SegmentationAnnotation]
    object_detection_annotations: _containers.RepeatedCompositeFieldContainer[ObjectDetectionAnnotation]
    ocr_annotations: _containers.RepeatedCompositeFieldContainer[OcrAnnotation]
    focus_areas: _containers.RepeatedCompositeFieldContainer[FocusArea]
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., classification_annotations: _Optional[_Iterable[_Union[ClassificationAnnotation, _Mapping]]] = ..., segmentation_annotations: _Optional[_Iterable[_Union[SegmentationAnnotation, _Mapping]]] = ..., object_detection_annotations: _Optional[_Iterable[_Union[ObjectDetectionAnnotation, _Mapping]]] = ..., ocr_annotations: _Optional[_Iterable[_Union[OcrAnnotation, _Mapping]]] = ..., focus_areas: _Optional[_Iterable[_Union[FocusArea, _Mapping]]] = ...) -> None: ...
