from ar.v1 import property_pb2 as _property_pb2
from geometry.v1 import pose_pb2 as _pose_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_TYPE_UNSPECIFIED: _ClassVar[AgentType]
    AGENT_TYPE_OPERATOR: _ClassVar[AgentType]
    AGENT_TYPE_ROBOT: _ClassVar[AgentType]

class OperatorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATOR_TYPE_UNSPECIFIED: _ClassVar[OperatorType]
    OPERATOR_TYPE_NOVICE: _ClassVar[OperatorType]
    OPERATOR_TYPE_INTERMEDIATE: _ClassVar[OperatorType]
    OPERATOR_TYPE_EXPERT: _ClassVar[OperatorType]

class OperatorPermission(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATOR_PERMISSION_UNSPECIFIED: _ClassVar[OperatorPermission]
    OPERATOR_PERMISSION_NONE: _ClassVar[OperatorPermission]
    OPERATOR_PERMISSION_COSMETIC: _ClassVar[OperatorPermission]
    OPERATOR_PERMISSION_FULL: _ClassVar[OperatorPermission]

class RobotType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROBOT_TYPE_UNSPECIFIED: _ClassVar[RobotType]
    ROBOT_TYPE_UR3E: _ClassVar[RobotType]
    ROBOT_TYPE_UR5E: _ClassVar[RobotType]
    ROBOT_TYPE_UR10E: _ClassVar[RobotType]
    ROBOT_TYPE_KUKA_IIWA: _ClassVar[RobotType]

class EndEffectorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    END_EFFECTOR_TYPE_UNSPECIFIED: _ClassVar[EndEffectorType]
    END_EFFECTOR_TYPE_EMPTY: _ClassVar[EndEffectorType]
    END_EFFECTOR_TYPE_ROBOTIQ_HAND_E: _ClassVar[EndEffectorType]
    END_EFFECTOR_TYPE_CUSTOM_MOUNT: _ClassVar[EndEffectorType]
AGENT_TYPE_UNSPECIFIED: AgentType
AGENT_TYPE_OPERATOR: AgentType
AGENT_TYPE_ROBOT: AgentType
OPERATOR_TYPE_UNSPECIFIED: OperatorType
OPERATOR_TYPE_NOVICE: OperatorType
OPERATOR_TYPE_INTERMEDIATE: OperatorType
OPERATOR_TYPE_EXPERT: OperatorType
OPERATOR_PERMISSION_UNSPECIFIED: OperatorPermission
OPERATOR_PERMISSION_NONE: OperatorPermission
OPERATOR_PERMISSION_COSMETIC: OperatorPermission
OPERATOR_PERMISSION_FULL: OperatorPermission
ROBOT_TYPE_UNSPECIFIED: RobotType
ROBOT_TYPE_UR3E: RobotType
ROBOT_TYPE_UR5E: RobotType
ROBOT_TYPE_UR10E: RobotType
ROBOT_TYPE_KUKA_IIWA: RobotType
END_EFFECTOR_TYPE_UNSPECIFIED: EndEffectorType
END_EFFECTOR_TYPE_EMPTY: EndEffectorType
END_EFFECTOR_TYPE_ROBOTIQ_HAND_E: EndEffectorType
END_EFFECTOR_TYPE_CUSTOM_MOUNT: EndEffectorType

class AgentMessage(_message.Message):
    __slots__ = ("id", "name", "type", "operator_type", "robot_type", "end_effector_type", "location", "properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROBOT_TYPE_FIELD_NUMBER: _ClassVar[int]
    END_EFFECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    type: AgentType
    operator_type: OperatorType
    robot_type: RobotType
    end_effector_type: EndEffectorType
    location: _pose_pb2.LocalizedPose
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[AgentType, str]] = ..., operator_type: _Optional[_Union[OperatorType, str]] = ..., robot_type: _Optional[_Union[RobotType, str]] = ..., end_effector_type: _Optional[_Union[EndEffectorType, str]] = ..., location: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ...) -> None: ...
