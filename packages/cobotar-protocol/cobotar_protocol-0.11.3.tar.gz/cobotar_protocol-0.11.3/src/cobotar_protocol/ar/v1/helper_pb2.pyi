from ar.v1 import property_pb2 as _property_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HelperType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HELPER_TYPE_UNSPECIFIED: _ClassVar[HelperType]
    HELPER_TYPE_PROXIMITY: _ClassVar[HelperType]
    HELPER_TYPE_STATIONARY: _ClassVar[HelperType]
    HELPER_TYPE_TIMER: _ClassVar[HelperType]
    HELPER_TYPE_AND: _ClassVar[HelperType]
    HELPER_TYPE_OR: _ClassVar[HelperType]
    HELPER_TYPE_NOT: _ClassVar[HelperType]
HELPER_TYPE_UNSPECIFIED: HelperType
HELPER_TYPE_PROXIMITY: HelperType
HELPER_TYPE_STATIONARY: HelperType
HELPER_TYPE_TIMER: HelperType
HELPER_TYPE_AND: HelperType
HELPER_TYPE_OR: HelperType
HELPER_TYPE_NOT: HelperType

class HelperMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "properties", "output_properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: HelperType
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    output_properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[HelperType, str]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ..., output_properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ...) -> None: ...
