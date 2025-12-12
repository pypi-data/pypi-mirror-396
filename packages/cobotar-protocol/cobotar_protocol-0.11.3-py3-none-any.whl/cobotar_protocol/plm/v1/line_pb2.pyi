from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LINE_TYPE_UNSPECIFIED: _ClassVar[LineType]
    LINE_TYPE_SUB_ASSEMBLY: _ClassVar[LineType]
    LINE_TYPE_FASTENER: _ClassVar[LineType]
    LINE_TYPE_PLATE: _ClassVar[LineType]
    LINE_TYPE_LUBRICANT: _ClassVar[LineType]
LINE_TYPE_UNSPECIFIED: LineType
LINE_TYPE_SUB_ASSEMBLY: LineType
LINE_TYPE_FASTENER: LineType
LINE_TYPE_PLATE: LineType
LINE_TYPE_LUBRICANT: LineType

class LineMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: LineType
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[LineType, str]] = ...) -> None: ...
