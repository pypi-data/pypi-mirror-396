from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelBlob(_message.Message):
    __slots__ = ("owned_by_group_id", "blob_id", "url")
    OWNED_BY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    BLOB_ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    owned_by_group_id: str
    blob_id: str
    url: str
    def __init__(self, owned_by_group_id: _Optional[str] = ..., blob_id: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class Snapshot(_message.Message):
    __slots__ = ("id", "onnx", "pytorch")
    ID_FIELD_NUMBER: _ClassVar[int]
    ONNX_FIELD_NUMBER: _ClassVar[int]
    PYTORCH_FIELD_NUMBER: _ClassVar[int]
    id: str
    onnx: ModelBlob
    pytorch: ModelBlob
    def __init__(self, id: _Optional[str] = ..., onnx: _Optional[_Union[ModelBlob, _Mapping]] = ..., pytorch: _Optional[_Union[ModelBlob, _Mapping]] = ...) -> None: ...

class NetworkConfig(_message.Message):
    __slots__ = ("uses_validation_tiling", "metadata")
    USES_VALIDATION_TILING_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    uses_validation_tiling: bool
    metadata: str
    def __init__(self, uses_validation_tiling: bool = ..., metadata: _Optional[str] = ...) -> None: ...

class OcrCharacterRestrictionPreset(_message.Message):
    __slots__ = ("value", "characters")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CHARACTERS_FIELD_NUMBER: _ClassVar[int]
    value: str
    characters: str
    def __init__(self, value: _Optional[str] = ..., characters: _Optional[str] = ...) -> None: ...

class OcrCharacterRestriction(_message.Message):
    __slots__ = ("index", "allowed_characters", "number_of_characters", "ocr_character_restriction_preset")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_CHARACTERS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_CHARACTERS_FIELD_NUMBER: _ClassVar[int]
    OCR_CHARACTER_RESTRICTION_PRESET_FIELD_NUMBER: _ClassVar[int]
    index: int
    allowed_characters: str
    number_of_characters: int
    ocr_character_restriction_preset: OcrCharacterRestrictionPreset
    def __init__(self, index: _Optional[int] = ..., allowed_characters: _Optional[str] = ..., number_of_characters: _Optional[int] = ..., ocr_character_restriction_preset: _Optional[_Union[OcrCharacterRestrictionPreset, _Mapping]] = ...) -> None: ...

class NetworkExperiment(_message.Message):
    __slots__ = ("id", "network_typename", "flavor", "class_labels", "config", "snapshot", "ocr_character_restrictions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NETWORK_TYPENAME_FIELD_NUMBER: _ClassVar[int]
    FLAVOR_FIELD_NUMBER: _ClassVar[int]
    CLASS_LABELS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    OCR_CHARACTER_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    network_typename: str
    flavor: str
    class_labels: _containers.RepeatedCompositeFieldContainer[ClassLabel]
    config: NetworkConfig
    snapshot: Snapshot
    ocr_character_restrictions: _containers.RepeatedCompositeFieldContainer[OcrCharacterRestriction]
    def __init__(self, id: _Optional[str] = ..., network_typename: _Optional[str] = ..., flavor: _Optional[str] = ..., class_labels: _Optional[_Iterable[_Union[ClassLabel, _Mapping]]] = ..., config: _Optional[_Union[NetworkConfig, _Mapping]] = ..., snapshot: _Optional[_Union[Snapshot, _Mapping]] = ..., ocr_character_restrictions: _Optional[_Iterable[_Union[OcrCharacterRestriction, _Mapping]]] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ("file_id", "height", "width", "owned_by_group_id", "blob_id", "url")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    OWNED_BY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    BLOB_ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    height: int
    width: int
    owned_by_group_id: str
    blob_id: str
    url: str
    def __init__(self, file_id: _Optional[str] = ..., height: _Optional[int] = ..., width: _Optional[int] = ..., owned_by_group_id: _Optional[str] = ..., blob_id: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class ClassLabel(_message.Message):
    __slots__ = ("id", "idx")
    ID_FIELD_NUMBER: _ClassVar[int]
    IDX_FIELD_NUMBER: _ClassVar[int]
    id: str
    idx: int
    def __init__(self, id: _Optional[str] = ..., idx: _Optional[int] = ...) -> None: ...
