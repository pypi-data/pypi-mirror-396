from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllocationStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALLOCATION_STRATEGY_UNSPECIFIED: _ClassVar[AllocationStrategy]
    ALLOCATION_STRATEGY_STATIC: _ClassVar[AllocationStrategy]
ALLOCATION_STRATEGY_UNSPECIFIED: AllocationStrategy
ALLOCATION_STRATEGY_STATIC: AllocationStrategy

class ProcessLoadMessage(_message.Message):
    __slots__ = ("request_id", "process_id", "line_id", "order_id", "allocation_strategy")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    LINE_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    process_id: str
    line_id: str
    order_id: str
    allocation_strategy: AllocationStrategy
    def __init__(self, request_id: _Optional[str] = ..., process_id: _Optional[str] = ..., line_id: _Optional[str] = ..., order_id: _Optional[str] = ..., allocation_strategy: _Optional[_Union[AllocationStrategy, str]] = ...) -> None: ...
