from ar.v1 import agent_pb2 as _agent_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentNewMessage(_message.Message):
    __slots__ = ("name", "type", "operator_type", "robot_type", "end_effector_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_TYPE_FIELD_NUMBER: _ClassVar[int]
    END_EFFECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: _agent_pb2.AgentType
    operator_type: _agent_pb2.OperatorType
    robot_type: _agent_pb2.RobotType
    end_effector_type: _agent_pb2.EndEffectorType
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[_agent_pb2.AgentType, str]] = ..., operator_type: _Optional[_Union[_agent_pb2.OperatorType, str]] = ..., robot_type: _Optional[_Union[_agent_pb2.RobotType, str]] = ..., end_effector_type: _Optional[_Union[_agent_pb2.EndEffectorType, str]] = ...) -> None: ...

class AgentUpdateMessage(_message.Message):
    __slots__ = ("id", "name", "operator_type", "robot_type", "end_effector_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_TYPE_FIELD_NUMBER: _ClassVar[int]
    END_EFFECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    operator_type: _agent_pb2.OperatorType
    robot_type: _agent_pb2.RobotType
    end_effector_type: _agent_pb2.EndEffectorType
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., operator_type: _Optional[_Union[_agent_pb2.OperatorType, str]] = ..., robot_type: _Optional[_Union[_agent_pb2.RobotType, str]] = ..., end_effector_type: _Optional[_Union[_agent_pb2.EndEffectorType, str]] = ...) -> None: ...

class AgentDeleteMessage(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
