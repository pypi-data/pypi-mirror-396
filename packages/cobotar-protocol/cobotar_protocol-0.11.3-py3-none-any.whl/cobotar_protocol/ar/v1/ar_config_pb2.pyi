from ar.v1 import action_pb2 as _action_pb2
from ar.v1 import feedback_pb2 as _feedback_pb2
from ar.v1 import helper_pb2 as _helper_pb2
from ar.v1 import property_pb2 as _property_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ARConfigInfoMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ARConfigMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "feedback", "actions", "helpers", "properties", "ar_disappear_distance")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    HELPERS_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    AR_DISAPPEAR_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    feedback: _containers.RepeatedCompositeFieldContainer[_feedback_pb2.FeedbackMessage]
    actions: _containers.RepeatedCompositeFieldContainer[_action_pb2.ActionMessage]
    helpers: _containers.RepeatedCompositeFieldContainer[_helper_pb2.HelperMessage]
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    ar_disappear_distance: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., feedback: _Optional[_Iterable[_Union[_feedback_pb2.FeedbackMessage, _Mapping]]] = ..., actions: _Optional[_Iterable[_Union[_action_pb2.ActionMessage, _Mapping]]] = ..., helpers: _Optional[_Iterable[_Union[_helper_pb2.HelperMessage, _Mapping]]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ..., ar_disappear_distance: _Optional[int] = ...) -> None: ...
