from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ARPriority(_message.Message):
    __slots__ = ("ar_config_id", "active_property_id")
    AR_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_PROPERTY_ID_FIELD_NUMBER: _ClassVar[int]
    ar_config_id: str
    active_property_id: str
    def __init__(self, ar_config_id: _Optional[str] = ..., active_property_id: _Optional[str] = ...) -> None: ...

class MappingMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "environment_ids", "ar_config_priorities")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    AR_CONFIG_PRIORITIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    environment_ids: _containers.RepeatedScalarFieldContainer[str]
    ar_config_priorities: _containers.RepeatedCompositeFieldContainer[ARPriority]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., environment_ids: _Optional[_Iterable[str]] = ..., ar_config_priorities: _Optional[_Iterable[_Union[ARPriority, _Mapping]]] = ...) -> None: ...

class MappingsMessage(_message.Message):
    __slots__ = ("mappings",)
    MAPPINGS_FIELD_NUMBER: _ClassVar[int]
    mappings: _containers.RepeatedCompositeFieldContainer[MappingMessage]
    def __init__(self, mappings: _Optional[_Iterable[_Union[MappingMessage, _Mapping]]] = ...) -> None: ...
