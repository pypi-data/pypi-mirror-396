import denkproto.request_pb2 as _request_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SourceTarget(_message.Message):
    __slots__ = ("materialized_markup_url", "prediction_url")
    MATERIALIZED_MARKUP_URL_FIELD_NUMBER: _ClassVar[int]
    PREDICTION_URL_FIELD_NUMBER: _ClassVar[int]
    materialized_markup_url: str
    prediction_url: str
    def __init__(self, materialized_markup_url: _Optional[str] = ..., prediction_url: _Optional[str] = ...) -> None: ...

class AnnotationComparerRequest(_message.Message):
    __slots__ = ("id", "owned_by_group_id", "hasura_url", "created_by_user_id", "network_experiment", "image", "source", "target")
    ID_FIELD_NUMBER: _ClassVar[int]
    OWNED_BY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    HASURA_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    NETWORK_EXPERIMENT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    id: str
    owned_by_group_id: str
    hasura_url: str
    created_by_user_id: str
    network_experiment: _request_pb2.NetworkExperiment
    image: _request_pb2.Image
    source: SourceTarget
    target: SourceTarget
    def __init__(self, id: _Optional[str] = ..., owned_by_group_id: _Optional[str] = ..., hasura_url: _Optional[str] = ..., created_by_user_id: _Optional[str] = ..., network_experiment: _Optional[_Union[_request_pb2.NetworkExperiment, _Mapping]] = ..., image: _Optional[_Union[_request_pb2.Image, _Mapping]] = ..., source: _Optional[_Union[SourceTarget, _Mapping]] = ..., target: _Optional[_Union[SourceTarget, _Mapping]] = ...) -> None: ...
