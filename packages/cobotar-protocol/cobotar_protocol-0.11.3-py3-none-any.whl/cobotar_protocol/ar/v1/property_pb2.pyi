from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PropertyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROPERTY_TYPE_UNSPECIFIED: _ClassVar[PropertyType]
    PROPERTY_TYPE_BOOL: _ClassVar[PropertyType]
    PROPERTY_TYPE_INT: _ClassVar[PropertyType]
    PROPERTY_TYPE_FLOAT: _ClassVar[PropertyType]
    PROPERTY_TYPE_DOUBLE: _ClassVar[PropertyType]
    PROPERTY_TYPE_STRING: _ClassVar[PropertyType]
    PROPERTY_TYPE_VECTOR3: _ClassVar[PropertyType]
    PROPERTY_TYPE_POSE: _ClassVar[PropertyType]
    PROPERTY_TYPE_ANCHOR: _ClassVar[PropertyType]
    PROPERTY_TYPE_COLOR: _ClassVar[PropertyType]
    PROPERTY_TYPE_AGENT: _ClassVar[PropertyType]
    PROPERTY_TYPE_ENUM: _ClassVar[PropertyType]
    PROPERTY_TYPE_ENUM_MULTI: _ClassVar[PropertyType]

class PropertyOrigin(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROPERTY_ORIGIN_UNSPECIFIED: _ClassVar[PropertyOrigin]
    PROPERTY_ORIGIN_FIXED: _ClassVar[PropertyOrigin]
    PROPERTY_ORIGIN_MIRROR: _ClassVar[PropertyOrigin]
PROPERTY_TYPE_UNSPECIFIED: PropertyType
PROPERTY_TYPE_BOOL: PropertyType
PROPERTY_TYPE_INT: PropertyType
PROPERTY_TYPE_FLOAT: PropertyType
PROPERTY_TYPE_DOUBLE: PropertyType
PROPERTY_TYPE_STRING: PropertyType
PROPERTY_TYPE_VECTOR3: PropertyType
PROPERTY_TYPE_POSE: PropertyType
PROPERTY_TYPE_ANCHOR: PropertyType
PROPERTY_TYPE_COLOR: PropertyType
PROPERTY_TYPE_AGENT: PropertyType
PROPERTY_TYPE_ENUM: PropertyType
PROPERTY_TYPE_ENUM_MULTI: PropertyType
PROPERTY_ORIGIN_UNSPECIFIED: PropertyOrigin
PROPERTY_ORIGIN_FIXED: PropertyOrigin
PROPERTY_ORIGIN_MIRROR: PropertyOrigin

class Property(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "value", "extras", "user_editable", "origin", "origins", "mirror_property_id", "group", "ordering", "hide_group")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    EXTRAS_FIELD_NUMBER: _ClassVar[int]
    USER_EDITABLE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    ORIGINS_FIELD_NUMBER: _ClassVar[int]
    MIRROR_PROPERTY_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    ORDERING_FIELD_NUMBER: _ClassVar[int]
    HIDE_GROUP_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: PropertyType
    value: str
    extras: str
    user_editable: bool
    origin: PropertyOrigin
    origins: _containers.RepeatedScalarFieldContainer[PropertyOrigin]
    mirror_property_id: str
    group: str
    ordering: int
    hide_group: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[PropertyType, str]] = ..., value: _Optional[str] = ..., extras: _Optional[str] = ..., user_editable: bool = ..., origin: _Optional[_Union[PropertyOrigin, str]] = ..., origins: _Optional[_Iterable[_Union[PropertyOrigin, str]]] = ..., mirror_property_id: _Optional[str] = ..., group: _Optional[str] = ..., ordering: _Optional[int] = ..., hide_group: bool = ...) -> None: ...
