import denkproto.geometry_pb2 as _geometry_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UInt8Map(_message.Message):
    __slots__ = ("width", "height", "data")
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    width: int
    height: int
    data: bytes
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class ClassificationPrediction(_message.Message):
    __slots__ = ("label_id", "probability", "interpretation_map")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    INTERPRETATION_MAP_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    probability: float
    interpretation_map: UInt8Map
    def __init__(self, label_id: _Optional[str] = ..., probability: _Optional[float] = ..., interpretation_map: _Optional[_Union[UInt8Map, _Mapping]] = ...) -> None: ...

class ObjectDetectionPrediction(_message.Message):
    __slots__ = ("label_id", "bounding_box", "probability")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    bounding_box: _geometry_pb2.BoundingBox
    probability: float
    def __init__(self, label_id: _Optional[str] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., probability: _Optional[float] = ...) -> None: ...

class InstanceSegmentationPrediction(_message.Message):
    __slots__ = ("label_id", "mask", "probability")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    MASK_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    mask: _geometry_pb2.InstanceSegmentationMask
    probability: float
    def __init__(self, label_id: _Optional[str] = ..., mask: _Optional[_Union[_geometry_pb2.InstanceSegmentationMask, _Mapping]] = ..., probability: _Optional[float] = ...) -> None: ...

class CharacterPrediction(_message.Message):
    __slots__ = ("character", "probability")
    CHARACTER_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    character: str
    probability: float
    def __init__(self, character: _Optional[str] = ..., probability: _Optional[float] = ...) -> None: ...

class OcrPrediction(_message.Message):
    __slots__ = ("label_id", "text", "character_predictions", "bounding_box", "polygon")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    text: str
    character_predictions: _containers.RepeatedCompositeFieldContainer[CharacterPrediction]
    bounding_box: _geometry_pb2.BoundingBox
    polygon: _geometry_pb2.Polygon
    def __init__(self, label_id: _Optional[str] = ..., text: _Optional[str] = ..., character_predictions: _Optional[_Iterable[_Union[CharacterPrediction, _Mapping]]] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., polygon: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ...) -> None: ...

class BarcodePrediction(_message.Message):
    __slots__ = ("label_id", "data", "points")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    data: bytes
    points: _containers.RepeatedCompositeFieldContainer[_geometry_pb2.Point2D]
    def __init__(self, label_id: _Optional[str] = ..., data: _Optional[bytes] = ..., points: _Optional[_Iterable[_Union[_geometry_pb2.Point2D, _Mapping]]] = ...) -> None: ...

class AnomalyPrediction(_message.Message):
    __slots__ = ("anomaly_map", "anomaly_score")
    ANOMALY_MAP_FIELD_NUMBER: _ClassVar[int]
    ANOMALY_SCORE_FIELD_NUMBER: _ClassVar[int]
    anomaly_map: UInt8Map
    anomaly_score: float
    def __init__(self, anomaly_map: _Optional[_Union[UInt8Map, _Mapping]] = ..., anomaly_score: _Optional[float] = ...) -> None: ...

class Prediction(_message.Message):
    __slots__ = ("height", "width", "classification_predictions", "object_detection_predictions", "instance_segmentation_predictions", "ocr_predictions", "barcode_predictions", "anomaly_predictions")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_SEGMENTATION_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    OCR_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    BARCODE_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    ANOMALY_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    classification_predictions: _containers.RepeatedCompositeFieldContainer[ClassificationPrediction]
    object_detection_predictions: _containers.RepeatedCompositeFieldContainer[ObjectDetectionPrediction]
    instance_segmentation_predictions: _containers.RepeatedCompositeFieldContainer[InstanceSegmentationPrediction]
    ocr_predictions: _containers.RepeatedCompositeFieldContainer[OcrPrediction]
    barcode_predictions: _containers.RepeatedCompositeFieldContainer[BarcodePrediction]
    anomaly_predictions: _containers.RepeatedCompositeFieldContainer[AnomalyPrediction]
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., classification_predictions: _Optional[_Iterable[_Union[ClassificationPrediction, _Mapping]]] = ..., object_detection_predictions: _Optional[_Iterable[_Union[ObjectDetectionPrediction, _Mapping]]] = ..., instance_segmentation_predictions: _Optional[_Iterable[_Union[InstanceSegmentationPrediction, _Mapping]]] = ..., ocr_predictions: _Optional[_Iterable[_Union[OcrPrediction, _Mapping]]] = ..., barcode_predictions: _Optional[_Iterable[_Union[BarcodePrediction, _Mapping]]] = ..., anomaly_predictions: _Optional[_Iterable[_Union[AnomalyPrediction, _Mapping]]] = ...) -> None: ...
