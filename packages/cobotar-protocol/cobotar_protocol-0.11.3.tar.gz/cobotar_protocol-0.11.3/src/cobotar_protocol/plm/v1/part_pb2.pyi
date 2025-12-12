from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PartType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PART_TYPE_UNSPECIFIED: _ClassVar[PartType]
    PART_TYPE_SUB_ASSEMBLY: _ClassVar[PartType]
    PART_TYPE_FASTENER: _ClassVar[PartType]
    PART_TYPE_PLATE: _ClassVar[PartType]
    PART_TYPE_LUBRICANT: _ClassVar[PartType]
PART_TYPE_UNSPECIFIED: PartType
PART_TYPE_SUB_ASSEMBLY: PartType
PART_TYPE_FASTENER: PartType
PART_TYPE_PLATE: PartType
PART_TYPE_LUBRICANT: PartType

class PartMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "weight", "model_id", "tool_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: PartType
    weight: int
    model_id: str
    tool_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[PartType, str]] = ..., weight: _Optional[int] = ..., model_id: _Optional[str] = ..., tool_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class PartMessages(_message.Message):
    __slots__ = ("parts",)
    PARTS_FIELD_NUMBER: _ClassVar[int]
    parts: _containers.RepeatedCompositeFieldContainer[PartMessage]
    def __init__(self, parts: _Optional[_Iterable[_Union[PartMessage, _Mapping]]] = ...) -> None: ...

class NewPartMessage(_message.Message):
    __slots__ = ("name", "description", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    type: PartType
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[PartType, str]] = ...) -> None: ...

class UpdatePartMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "weight", "model_id", "tool_ids")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: PartType
    weight: int
    model_id: str
    tool_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[PartType, str]] = ..., weight: _Optional[int] = ..., model_id: _Optional[str] = ..., tool_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeletePartMessage(_message.Message):
    __slots__ = ("part_id",)
    PART_ID_FIELD_NUMBER: _ClassVar[int]
    part_id: str
    def __init__(self, part_id: _Optional[str] = ...) -> None: ...
