# Protocol Documentation
<a name="top"></a>

## Table of Contents

- [ar/v1/property.proto](#ar_v1_property-proto)
    - [Property](#ar-v1-Property)
  
    - [PropertyOrigin](#ar-v1-PropertyOrigin)
    - [PropertyType](#ar-v1-PropertyType)
  
- [ar/v1/action.proto](#ar_v1_action-proto)
    - [ActionMessage](#ar-v1-ActionMessage)
  
    - [ActionType](#ar-v1-ActionType)
  
- [ar/v1/events.proto](#ar_v1_events-proto)
    - [SupportedEventsMessage](#ar-v1-SupportedEventsMessage)
  
    - [EventType](#ar-v1-EventType)
  
- [ar/v1/action_info.proto](#ar_v1_action_info-proto)
    - [ActionInfoMessage](#ar-v1-ActionInfoMessage)
    - [ActionInfosMessage](#ar-v1-ActionInfosMessage)
  
- [geometry/v1/point.proto](#geometry_v1_point-proto)
    - [Point](#geometry-v1-Point)
  
- [geometry/v1/quad.proto](#geometry_v1_quad-proto)
    - [Quad](#geometry-v1-Quad)
  
- [geometry/v1/pose.proto](#geometry_v1_pose-proto)
    - [LocalizedPose](#geometry-v1-LocalizedPose)
    - [Pose](#geometry-v1-Pose)
  
    - [LocalizedState](#geometry-v1-LocalizedState)
  
- [ar/v1/agent.proto](#ar_v1_agent-proto)
    - [AgentMessage](#ar-v1-AgentMessage)
  
    - [AgentType](#ar-v1-AgentType)
    - [EndEffectorType](#ar-v1-EndEffectorType)
    - [OperatorPermission](#ar-v1-OperatorPermission)
    - [OperatorType](#ar-v1-OperatorType)
    - [RobotType](#ar-v1-RobotType)
  
- [ar/v1/feedback.proto](#ar_v1_feedback-proto)
    - [FeedbackMessage](#ar-v1-FeedbackMessage)
  
    - [FeedbackType](#ar-v1-FeedbackType)
  
- [ar/v1/helper.proto](#ar_v1_helper-proto)
    - [HelperMessage](#ar-v1-HelperMessage)
  
    - [HelperType](#ar-v1-HelperType)
  
- [ar/v1/ar_config.proto](#ar_v1_ar_config-proto)
    - [ARConfigInfoMessage](#ar-v1-ARConfigInfoMessage)
    - [ARConfigMessage](#ar-v1-ARConfigMessage)
  
- [ar/v1/authoring_action.proto](#ar_v1_authoring_action-proto)
    - [ActionDeleteMessage](#ar-v1-ActionDeleteMessage)
    - [ActionNewMessage](#ar-v1-ActionNewMessage)
    - [ActionUpdateMessage](#ar-v1-ActionUpdateMessage)
  
- [ar/v1/authoring_agent.proto](#ar_v1_authoring_agent-proto)
    - [AgentDeleteMessage](#ar-v1-AgentDeleteMessage)
    - [AgentNewMessage](#ar-v1-AgentNewMessage)
    - [AgentUpdateMessage](#ar-v1-AgentUpdateMessage)
  
- [ar/v1/authoring_ar_config.proto](#ar_v1_authoring_ar_config-proto)
    - [ARConfigDeleteMessage](#ar-v1-ARConfigDeleteMessage)
    - [ARConfigNewMessage](#ar-v1-ARConfigNewMessage)
    - [ARConfigUpdateMessage](#ar-v1-ARConfigUpdateMessage)
  
- [ar/v1/environment.proto](#ar_v1_environment-proto)
    - [AgentLocation](#ar-v1-AgentLocation)
    - [EnvironmentMessage](#ar-v1-EnvironmentMessage)
    - [EnvironmentsMessage](#ar-v1-EnvironmentsMessage)
    - [MarkerLocation](#ar-v1-MarkerLocation)
    - [PartLocation](#ar-v1-PartLocation)
    - [ToolLocation](#ar-v1-ToolLocation)
  
    - [EnvironmentType](#ar-v1-EnvironmentType)
  
- [ar/v1/authoring_environment.proto](#ar_v1_authoring_environment-proto)
    - [EnvironmentDeleteMessage](#ar-v1-EnvironmentDeleteMessage)
    - [EnvironmentNewMessage](#ar-v1-EnvironmentNewMessage)
    - [EnvironmentUpdateMessage](#ar-v1-EnvironmentUpdateMessage)
  
- [ar/v1/authoring_feedback.proto](#ar_v1_authoring_feedback-proto)
    - [FeedbackCloneMessage](#ar-v1-FeedbackCloneMessage)
    - [FeedbackDeleteMessage](#ar-v1-FeedbackDeleteMessage)
    - [FeedbackNewMessage](#ar-v1-FeedbackNewMessage)
    - [FeedbackUpdateMessage](#ar-v1-FeedbackUpdateMessage)
  
- [ar/v1/mapping.proto](#ar_v1_mapping-proto)
    - [ARPriority](#ar-v1-ARPriority)
    - [MappingMessage](#ar-v1-MappingMessage)
    - [MappingsMessage](#ar-v1-MappingsMessage)
  
- [ar/v1/authoring_mapping.proto](#ar_v1_authoring_mapping-proto)
    - [MappingDeleteMessage](#ar-v1-MappingDeleteMessage)
    - [MappingNewMessage](#ar-v1-MappingNewMessage)
    - [MappingUpdateMessage](#ar-v1-MappingUpdateMessage)
  
- [ar/v1/authoring_marker.proto](#ar_v1_authoring_marker-proto)
    - [MarkerDeleteMessage](#ar-v1-MarkerDeleteMessage)
    - [MarkerNewMessage](#ar-v1-MarkerNewMessage)
    - [MarkerUpdateMessage](#ar-v1-MarkerUpdateMessage)
  
- [ar/v1/config_load.proto](#ar_v1_config_load-proto)
    - [ConfigurationLoadMessage](#ar-v1-ConfigurationLoadMessage)
  
- [ar/v1/feedback_info.proto](#ar_v1_feedback_info-proto)
    - [FeedbackInfoMessage](#ar-v1-FeedbackInfoMessage)
    - [FeedbackInfosMessage](#ar-v1-FeedbackInfosMessage)
  
- [ar/v1/helper_info.proto](#ar_v1_helper_info-proto)
    - [HelperInfoMessage](#ar-v1-HelperInfoMessage)
    - [HelperInfosMessage](#ar-v1-HelperInfosMessage)
  
- [ar/v1/marker.proto](#ar_v1_marker-proto)
    - [MarkerMessage](#ar-v1-MarkerMessage)
    - [MarkersMessage](#ar-v1-MarkersMessage)
  
    - [MarkerType](#ar-v1-MarkerType)
  
- [ar/v1/template.proto](#ar_v1_template-proto)
    - [TemplateInfoMessage](#ar-v1-TemplateInfoMessage)
    - [TemplateInfoMessages](#ar-v1-TemplateInfoMessages)
    - [TemplateMessage](#ar-v1-TemplateMessage)
  
- [common/v1/color.proto](#common_v1_color-proto)
    - [Color](#common-v1-Color)
  
- [common/v1/delete.proto](#common_v1_delete-proto)
    - [DeleteMessage](#common-v1-DeleteMessage)
  
- [geometry/v1/anchor.proto](#geometry_v1_anchor-proto)
    - [Anchor](#geometry-v1-Anchor)
  
- [geometry/v1/vector3.proto](#geometry_v1_vector3-proto)
    - [Vector3](#geometry-v1-Vector3)
  
- [geometry/v1/wrench.proto](#geometry_v1_wrench-proto)
    - [Wrench](#geometry-v1-Wrench)
  
- [plm/v1/capability.proto](#plm_v1_capability-proto)
    - [Capabilities](#plm-v1-Capabilities)
    - [Capability](#plm-v1-Capability)
  
- [plm/v1/line.proto](#plm_v1_line-proto)
    - [LineMessage](#plm-v1-LineMessage)
  
    - [LineType](#plm-v1-LineType)
  
- [plm/v1/models.proto](#plm_v1_models-proto)
    - [ModelMessage](#plm-v1-ModelMessage)
    - [ModelMessages](#plm-v1-ModelMessages)
  
- [plm/v1/part.proto](#plm_v1_part-proto)
    - [DeletePartMessage](#plm-v1-DeletePartMessage)
    - [NewPartMessage](#plm-v1-NewPartMessage)
    - [PartMessage](#plm-v1-PartMessage)
    - [PartMessages](#plm-v1-PartMessages)
    - [UpdatePartMessage](#plm-v1-UpdatePartMessage)
  
    - [PartType](#plm-v1-PartType)
  
- [plm/v1/sequence.proto](#plm_v1_sequence-proto)
    - [SequenceMessage](#plm-v1-SequenceMessage)
    - [SequenceUpdatedMessage](#plm-v1-SequenceUpdatedMessage)
  
    - [SequenceState](#plm-v1-SequenceState)
  
- [plm/v1/task.proto](#plm_v1_task-proto)
    - [TaskMessage](#plm-v1-TaskMessage)
    - [TaskUpdatedMessage](#plm-v1-TaskUpdatedMessage)
  
    - [TaskAssignmentPreference](#plm-v1-TaskAssignmentPreference)
    - [TaskState](#plm-v1-TaskState)
    - [TaskType](#plm-v1-TaskType)
  
- [plm/v1/process.proto](#plm_v1_process-proto)
    - [ProcessMessage](#plm-v1-ProcessMessage)
    - [ProcessUpdatedMessage](#plm-v1-ProcessUpdatedMessage)
    - [ProcessesMessage](#plm-v1-ProcessesMessage)
  
    - [ProcessState](#plm-v1-ProcessState)
    - [ProcessType](#plm-v1-ProcessType)
  
- [plm/v1/process_abort.proto](#plm_v1_process_abort-proto)
    - [ProcessAbortMessage](#plm-v1-ProcessAbortMessage)
  
- [plm/v1/sequence_authoring.proto](#plm_v1_sequence_authoring-proto)
    - [DeleteSequenceMessage](#plm-v1-DeleteSequenceMessage)
    - [NewSequenceMessage](#plm-v1-NewSequenceMessage)
    - [StoredSequenceMessage](#plm-v1-StoredSequenceMessage)
    - [UpdateSequenceMessage](#plm-v1-UpdateSequenceMessage)
  
- [plm/v1/process_authoring.proto](#plm_v1_process_authoring-proto)
    - [DeleteProcessMessage](#plm-v1-DeleteProcessMessage)
    - [NewProcessMessage](#plm-v1-NewProcessMessage)
    - [StoredProcessMessage](#plm-v1-StoredProcessMessage)
    - [StoredProcessesMessage](#plm-v1-StoredProcessesMessage)
    - [UpdateProcessMessage](#plm-v1-UpdateProcessMessage)
  
- [plm/v1/process_load.proto](#plm_v1_process_load-proto)
    - [ProcessLoadMessage](#plm-v1-ProcessLoadMessage)
  
    - [AllocationStrategy](#plm-v1-AllocationStrategy)
  
- [plm/v1/requests.proto](#plm_v1_requests-proto)
    - [ProcessAtLocationMessage](#plm-v1-ProcessAtLocationMessage)
  
- [plm/v1/sequence_complete.proto](#plm_v1_sequence_complete-proto)
    - [SequenceBulkCompleteMessage](#plm-v1-SequenceBulkCompleteMessage)
  
- [plm/v1/sequence_reassign.proto](#plm_v1_sequence_reassign-proto)
    - [SequenceReassignMessage](#plm-v1-SequenceReassignMessage)
  
- [plm/v1/task_authoring.proto](#plm_v1_task_authoring-proto)
    - [DeleteTaskMessage](#plm-v1-DeleteTaskMessage)
    - [NewTaskMessage](#plm-v1-NewTaskMessage)
    - [StoredTaskMessage](#plm-v1-StoredTaskMessage)
    - [UpdateTaskMessage](#plm-v1-UpdateTaskMessage)
  
- [plm/v1/task_progress.proto](#plm_v1_task_progress-proto)
    - [TaskProgressMessage](#plm-v1-TaskProgressMessage)
  
- [plm/v1/task_reassign.proto](#plm_v1_task_reassign-proto)
    - [TaskReassignMessage](#plm-v1-TaskReassignMessage)
  
- [plm/v1/task_state_change.proto](#plm_v1_task_state_change-proto)
    - [TaskStateChangeMessage](#plm-v1-TaskStateChangeMessage)
  
    - [TaskStateRequest](#plm-v1-TaskStateRequest)
  
- [plm/v1/tasks_list.proto](#plm_v1_tasks_list-proto)
    - [TasksForAgentRequest](#plm-v1-TasksForAgentRequest)
    - [TasksForAgentResponse](#plm-v1-TasksForAgentResponse)
  
- [plm/v1/tool.proto](#plm_v1_tool-proto)
    - [DeleteToolMessage](#plm-v1-DeleteToolMessage)
    - [NewToolMessage](#plm-v1-NewToolMessage)
    - [ToolMessage](#plm-v1-ToolMessage)
    - [ToolMessages](#plm-v1-ToolMessages)
    - [UpdateToolMessage](#plm-v1-UpdateToolMessage)
  
- [robot/v1/end_effector.proto](#robot_v1_end_effector-proto)
    - [EndEffectorStateMessage](#robot-v1-EndEffectorStateMessage)
  
- [robot/v1/jointstate.proto](#robot_v1_jointstate-proto)
    - [JointStateMessage](#robot-v1-JointStateMessage)
  
- [robot/v1/path.proto](#robot_v1_path-proto)
    - [PathMessage](#robot-v1-PathMessage)
  
- [robot/v1/popup.proto](#robot_v1_popup-proto)
    - [RobotHidePopupRequest](#robot-v1-RobotHidePopupRequest)
    - [RobotShowPopupRequest](#robot-v1-RobotShowPopupRequest)
  
- [robot/v1/program_state.proto](#robot_v1_program_state-proto)
    - [ProgramStateMessage](#robot-v1-ProgramStateMessage)
  
    - [ProgramState](#robot-v1-ProgramState)
  
- [robot/v1/program_state_request.proto](#robot_v1_program_state_request-proto)
    - [ProgramStateRequest](#robot-v1-ProgramStateRequest)
  
- [robot/v1/robot_state.proto](#robot_v1_robot_state-proto)
    - [RobotStateMessage](#robot-v1-RobotStateMessage)
  
    - [RobotState](#robot-v1-RobotState)
  
- [robot/v1/robot_visibility.proto](#robot_v1_robot_visibility-proto)
    - [RobotVisibilityMessage](#robot-v1-RobotVisibilityMessage)
  
- [robot/v1/tcp.proto](#robot_v1_tcp-proto)
    - [TcpMessage](#robot-v1-TcpMessage)
  
- [robot/v1/waypoints.proto](#robot_v1_waypoints-proto)
    - [WaypointMessage](#robot-v1-WaypointMessage)
    - [WaypointsMessage](#robot-v1-WaypointsMessage)
  
- [robot/v1/zone.proto](#robot_v1_zone-proto)
    - [ZoneMessage](#robot-v1-ZoneMessage)
  
- [service/v1/ar_client.proto](#service_v1_ar_client-proto)
    - [ARClientMessage](#service-v1-ARClientMessage)
  
    - [ARClientRole](#service-v1-ARClientRole)
  
- [service/v1/response.proto](#service_v1_response-proto)
    - [Response](#service-v1-Response)
  
- [service/v1/robot_adapter.proto](#service_v1_robot_adapter-proto)
    - [RobotAdapterInfoMessage](#service-v1-RobotAdapterInfoMessage)
  
- [service/v1/status.proto](#service_v1_status-proto)
    - [ServiceStatus](#service-v1-ServiceStatus)
  
    - [Status](#service-v1-Status)
  
- [Scalar Value Types](#scalar-value-types)



<a name="ar_v1_property-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/property.proto



<a name="ar-v1-Property"></a>

### Property
Properties are used by various components to define them, such as: feedback, actions, and conditions.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [PropertyType](#ar-v1-PropertyType) |  |  |
| value | [string](#string) |  | the current value of the property (JSON encoded) |
| extras | [string](#string) |  | JSON encoded extra values, e.g. {min: -0.1, max: 0.5, step: 0.1} for a double property. |
| user_editable | [bool](#bool) |  | TODO: create different user permissions, this field should then set the &#34;minimum required permission&#34; |
| origin | [PropertyOrigin](#ar-v1-PropertyOrigin) |  |  |
| origins | [PropertyOrigin](#ar-v1-PropertyOrigin) | repeated |  |
| mirror_property_id | [string](#string) |  |  |
| group | [string](#string) |  |  |
| ordering | [int32](#int32) |  |  |
| hide_group | [bool](#bool) |  |  |





 


<a name="ar-v1-PropertyOrigin"></a>

### PropertyOrigin
Specifies where the value of a property originates from.

| Name | Number | Description |
| ---- | ------ | ----------- |
| PROPERTY_ORIGIN_UNSPECIFIED | 0 |  |
| PROPERTY_ORIGIN_FIXED | 1 | The value of the property is fixed and must be changed manually |
| PROPERTY_ORIGIN_MIRROR | 2 | The value of the property mirrors the value of another property |



<a name="ar-v1-PropertyType"></a>

### PropertyType
Used to specify the type of a property

| Name | Number | Description |
| ---- | ------ | ----------- |
| PROPERTY_TYPE_UNSPECIFIED | 0 |  |
| PROPERTY_TYPE_BOOL | 1 |  |
| PROPERTY_TYPE_INT | 2 |  |
| PROPERTY_TYPE_FLOAT | 3 |  |
| PROPERTY_TYPE_DOUBLE | 4 |  |
| PROPERTY_TYPE_STRING | 5 |  |
| PROPERTY_TYPE_VECTOR3 | 6 |  |
| PROPERTY_TYPE_POSE | 7 |  |
| PROPERTY_TYPE_ANCHOR | 8 |  |
| PROPERTY_TYPE_COLOR | 9 |  |
| PROPERTY_TYPE_AGENT | 10 |  |
| PROPERTY_TYPE_ENUM | 11 |  |
| PROPERTY_TYPE_ENUM_MULTI | 12 |  |


 

 

 



<a name="ar_v1_action-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/action.proto



<a name="ar-v1-ActionMessage"></a>

### ActionMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ActionType](#ar-v1-ActionType) |  |  |
| properties | [Property](#ar-v1-Property) | repeated |  |
| output_properties | [Property](#ar-v1-Property) | repeated |  |





 


<a name="ar-v1-ActionType"></a>

### ActionType


| Name | Number | Description |
| ---- | ------ | ----------- |
| ACTION_TYPE_UNSPECIFIED | 0 |  |
| ACTION_TYPE_TASK_COMPLETE | 10 |  |
| ACTION_TYPE_TASK_UNDO | 11 |  |
| ACTION_TYPE_TASK_ASSIGN | 12 |  |
| ACTION_TYPE_TASK_HIGHLIGHT | 13 |  |
| ACTION_TYPE_TASK_HELP | 14 |  |
| ACTION_TYPE_ROBOT_PLAY_PAUSE | 50 |  |
| ACTION_TYPE_ROBOT_ACKNOWLEDGE | 51 | ACTION_TYPE_ROBOT_FREE_DRIVE = 52; |


 

 

 



<a name="ar_v1_events-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/events.proto



<a name="ar-v1-SupportedEventsMessage"></a>

### SupportedEventsMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| events | [EventType](#ar-v1-EventType) | repeated |  |





 


<a name="ar-v1-EventType"></a>

### EventType


| Name | Number | Description |
| ---- | ------ | ----------- |
| EVENT_TYPE_UNSPECIFIED | 0 |  |
| EVENT_TYPE_TASK_COMPLETE | 10 |  |
| EVENT_TYPE_TASK_UNDO | 11 |  |
| EVENT_TYPE_TASK_ASSIGN | 12 |  |
| EVENT_TYPE_TASK_HIGHLIGHT | 13 |  |
| EVENT_TYPE_TASK_HELP | 14 |  |
| EVENT_TYPE_ROBOT_TCP | 100 |  |
| EVENT_TYPE_ROBOT_JOINT_ANGLES | 101 |  |
| EVENT_TYPE_ROBOT_FORCE_TORQUE | 102 |  |
| EVENT_TYPE_ROBOT_STATE | 110 |  |
| EVENT_TYPE_ROBOT_PATH | 120 |  |
| EVENT_TYPE_ROBOT_WAYPOINTS | 121 |  |


 

 

 



<a name="ar_v1_action_info-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/action_info.proto



<a name="ar-v1-ActionInfoMessage"></a>

### ActionInfoMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ActionType](#ar-v1-ActionType) |  |  |
| group | [string](#string) |  |  |
| require_agent | [bool](#bool) |  |  |
| required_events | [EventType](#ar-v1-EventType) | repeated |  |
| optional_events | [EventType](#ar-v1-EventType) | repeated |  |
| disabled | [bool](#bool) |  |  |






<a name="ar-v1-ActionInfosMessage"></a>

### ActionInfosMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| action_infos | [ActionInfoMessage](#ar-v1-ActionInfoMessage) | repeated |  |





 

 

 

 



<a name="geometry_v1_point-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## geometry/v1/point.proto



<a name="geometry-v1-Point"></a>

### Point



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| x | [double](#double) |  |  |
| y | [double](#double) |  |  |
| z | [double](#double) |  |  |





 

 

 

 



<a name="geometry_v1_quad-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## geometry/v1/quad.proto



<a name="geometry-v1-Quad"></a>

### Quad



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| x | [double](#double) |  |  |
| y | [double](#double) |  |  |
| z | [double](#double) |  |  |
| w | [double](#double) |  |  |





 

 

 

 



<a name="geometry_v1_pose-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## geometry/v1/pose.proto



<a name="geometry-v1-LocalizedPose"></a>

### LocalizedPose
A localized pose with reference to an anchorId. The state and last updated time of the pose can be specified.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| pose | [Pose](#geometry-v1-Pose) |  |  |
| anchor_id | [string](#string) |  |  |
| state | [LocalizedState](#geometry-v1-LocalizedState) |  |  |
| last_updated | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |






<a name="geometry-v1-Pose"></a>

### Pose
A simple pose consisting of a position and orientation


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| position | [Point](#geometry-v1-Point) |  |  |
| orientation | [Quad](#geometry-v1-Quad) |  |  |





 


<a name="geometry-v1-LocalizedState"></a>

### LocalizedState


| Name | Number | Description |
| ---- | ------ | ----------- |
| LOCALIZED_STATE_UNSPECIFIED | 0 |  |
| LOCALIZED_STATE_FOUND | 1 |  |
| LOCALIZED_STATE_LOST | 2 |  |
| LOCALIZED_STATE_STATIC | 3 |  |
| LOCALIZED_STATE_UNKNOWN | 4 |  |


 

 

 



<a name="ar_v1_agent-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/agent.proto



<a name="ar-v1-AgentMessage"></a>

### AgentMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| type | [AgentType](#ar-v1-AgentType) |  |  |
| operator_type | [OperatorType](#ar-v1-OperatorType) |  |  |
| robot_type | [RobotType](#ar-v1-RobotType) |  |  |
| end_effector_type | [EndEffectorType](#ar-v1-EndEffectorType) |  |  |
| location | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| properties | [Property](#ar-v1-Property) | repeated |  |





 


<a name="ar-v1-AgentType"></a>

### AgentType


| Name | Number | Description |
| ---- | ------ | ----------- |
| AGENT_TYPE_UNSPECIFIED | 0 |  |
| AGENT_TYPE_OPERATOR | 1 |  |
| AGENT_TYPE_ROBOT | 2 |  |



<a name="ar-v1-EndEffectorType"></a>

### EndEffectorType


| Name | Number | Description |
| ---- | ------ | ----------- |
| END_EFFECTOR_TYPE_UNSPECIFIED | 0 |  |
| END_EFFECTOR_TYPE_EMPTY | 1 |  |
| END_EFFECTOR_TYPE_ROBOTIQ_HAND_E | 10 |  |
| END_EFFECTOR_TYPE_CUSTOM_MOUNT | 20 |  |



<a name="ar-v1-OperatorPermission"></a>

### OperatorPermission


| Name | Number | Description |
| ---- | ------ | ----------- |
| OPERATOR_PERMISSION_UNSPECIFIED | 0 |  |
| OPERATOR_PERMISSION_NONE | 1 |  |
| OPERATOR_PERMISSION_COSMETIC | 2 |  |
| OPERATOR_PERMISSION_FULL | 3 |  |



<a name="ar-v1-OperatorType"></a>

### OperatorType


| Name | Number | Description |
| ---- | ------ | ----------- |
| OPERATOR_TYPE_UNSPECIFIED | 0 |  |
| OPERATOR_TYPE_NOVICE | 1 |  |
| OPERATOR_TYPE_INTERMEDIATE | 2 |  |
| OPERATOR_TYPE_EXPERT | 3 |  |



<a name="ar-v1-RobotType"></a>

### RobotType


| Name | Number | Description |
| ---- | ------ | ----------- |
| ROBOT_TYPE_UNSPECIFIED | 0 |  |
| ROBOT_TYPE_UR3E | 10 |  |
| ROBOT_TYPE_UR5E | 11 |  |
| ROBOT_TYPE_UR10E | 12 |  |
| ROBOT_TYPE_KUKA_IIWA | 20 |  |


 

 

 



<a name="ar_v1_feedback-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/feedback.proto



<a name="ar-v1-FeedbackMessage"></a>

### FeedbackMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [FeedbackType](#ar-v1-FeedbackType) |  |  |
| properties | [Property](#ar-v1-Property) | repeated |  |
| output_properties | [Property](#ar-v1-Property) | repeated |  |





 


<a name="ar-v1-FeedbackType"></a>

### FeedbackType


| Name | Number | Description |
| ---- | ------ | ----------- |
| FEEDBACK_TYPE_UNSPECIFIED | 0 |  |
| FEEDBACK_TYPE_TASK_HIGHLIGHT | 10 |  |
| FEEDBACK_TYPE_TASK_PART_HIGHLIGHT | 11 |  |
| FEEDBACK_TYPE_TASK_TOOL_HIGHLIGHT | 12 |  |
| FEEDBACK_TYPE_TASK_OVERVIEW | 13 |  |
| FEEDBACK_TYPE_ROBOT_PATH | 50 |  |
| FEEDBACK_TYPE_ROBOT_SILHOUETTE | 51 |  |
| FEEDBACK_TYPE_ROBOT_WAYPOINTS | 52 |  |
| FEEDBACK_TYPE_ROBOT_STATUS | 53 |  |
| FEEDBACK_TYPE_ROBOT_LIGHT | 54 |  |
| FEEDBACK_TYPE_MESSAGE | 100 |  |
| FEEDBACK_TYPE_ICON | 101 |  |
| FEEDBACK_TYPE_ZONE | 102 |  |
| FEEDBACK_TYPE_PLAY_SOUND | 103 |  |
| FEEDBACK_TYPE_RULER | 104 |  |


 

 

 



<a name="ar_v1_helper-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/helper.proto



<a name="ar-v1-HelperMessage"></a>

### HelperMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [HelperType](#ar-v1-HelperType) |  |  |
| properties | [Property](#ar-v1-Property) | repeated |  |
| output_properties | [Property](#ar-v1-Property) | repeated |  |





 


<a name="ar-v1-HelperType"></a>

### HelperType


| Name | Number | Description |
| ---- | ------ | ----------- |
| HELPER_TYPE_UNSPECIFIED | 0 |  |
| HELPER_TYPE_PROXIMITY | 10 |  |
| HELPER_TYPE_STATIONARY | 11 |  |
| HELPER_TYPE_TIMER | 21 |  |
| HELPER_TYPE_AND | 100 |  |
| HELPER_TYPE_OR | 101 |  |
| HELPER_TYPE_NOT | 102 |  |


 

 

 



<a name="ar_v1_ar_config-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/ar_config.proto



<a name="ar-v1-ARConfigInfoMessage"></a>

### ARConfigInfoMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |






<a name="ar-v1-ARConfigMessage"></a>

### ARConfigMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| feedback | [FeedbackMessage](#ar-v1-FeedbackMessage) | repeated |  |
| actions | [ActionMessage](#ar-v1-ActionMessage) | repeated |  |
| helpers | [HelperMessage](#ar-v1-HelperMessage) | repeated |  |
| properties | [Property](#ar-v1-Property) | repeated |  |
| ar_disappear_distance | [int64](#int64) |  | Threshold distance in cm all AR elements should disappear. |





 

 

 

 



<a name="ar_v1_authoring_action-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_action.proto



<a name="ar-v1-ActionDeleteMessage"></a>

### ActionDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |






<a name="ar-v1-ActionNewMessage"></a>

### ActionNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| parent_config_id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ActionType](#ar-v1-ActionType) |  |  |
| trigger_property_id | [string](#string) |  |  |
| agent_id | [string](#string) |  |  |






<a name="ar-v1-ActionUpdateMessage"></a>

### ActionUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |





 

 

 

 



<a name="ar_v1_authoring_agent-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_agent.proto



<a name="ar-v1-AgentDeleteMessage"></a>

### AgentDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Id of the marker to be deleted |






<a name="ar-v1-AgentNewMessage"></a>

### AgentNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| type | [AgentType](#ar-v1-AgentType) |  |  |
| operator_type | [OperatorType](#ar-v1-OperatorType) |  |  |
| robot_type | [RobotType](#ar-v1-RobotType) |  |  |
| end_effector_type | [EndEffectorType](#ar-v1-EndEffectorType) |  |  |






<a name="ar-v1-AgentUpdateMessage"></a>

### AgentUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Unique id of the maker (this won&#39;t be changed) |
| name | [string](#string) |  |  |
| operator_type | [OperatorType](#ar-v1-OperatorType) |  |  |
| robot_type | [RobotType](#ar-v1-RobotType) |  |  |
| end_effector_type | [EndEffectorType](#ar-v1-EndEffectorType) |  |  |





 

 

 

 



<a name="ar_v1_authoring_ar_config-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_ar_config.proto



<a name="ar-v1-ARConfigDeleteMessage"></a>

### ARConfigDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |






<a name="ar-v1-ARConfigNewMessage"></a>

### ARConfigNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| template_id | [string](#string) |  | Template id is used to pre-populate a configuration. Leave empty for a new fresh start. |






<a name="ar-v1-ARConfigUpdateMessage"></a>

### ARConfigUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| feedback | [FeedbackMessage](#ar-v1-FeedbackMessage) | repeated |  |
| actions | [ActionMessage](#ar-v1-ActionMessage) | repeated |  |
| helpers | [HelperMessage](#ar-v1-HelperMessage) | repeated |  |
| properties | [Property](#ar-v1-Property) | repeated |  |
| ar_disappear_distance | [int64](#int64) |  |  |





 

 

 

 



<a name="ar_v1_environment-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/environment.proto



<a name="ar-v1-AgentLocation"></a>

### AgentLocation



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| location | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |






<a name="ar-v1-EnvironmentMessage"></a>

### EnvironmentMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [EnvironmentType](#ar-v1-EnvironmentType) |  |  |
| markers | [MarkerLocation](#ar-v1-MarkerLocation) | repeated | Markers associated with this environment. |
| agents | [AgentLocation](#ar-v1-AgentLocation) | repeated |  |
| parts | [PartLocation](#ar-v1-PartLocation) | repeated |  |
| tools | [ToolLocation](#ar-v1-ToolLocation) | repeated |  |
| properties | [Property](#ar-v1-Property) | repeated | TODO: add change_type: add, update, delete, unspecified? |






<a name="ar-v1-EnvironmentsMessage"></a>

### EnvironmentsMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| environments | [EnvironmentMessage](#ar-v1-EnvironmentMessage) | repeated |  |






<a name="ar-v1-MarkerLocation"></a>

### MarkerLocation



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| location | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |






<a name="ar-v1-PartLocation"></a>

### PartLocation



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| location | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |






<a name="ar-v1-ToolLocation"></a>

### ToolLocation



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| location | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |





 


<a name="ar-v1-EnvironmentType"></a>

### EnvironmentType


| Name | Number | Description |
| ---- | ------ | ----------- |
| ENVIRONMENT_TYPE_UNSPECIFIED | 0 |  |
| ENVIRONMENT_TYPE_STORAGE | 1 |  |
| ENVIRONMENT_TYPE_MANUAL_STATION | 2 |  |
| ENVIRONMENT_TYPE_AUTOMATIC_STATION | 3 |  |
| ENVIRONMENT_TYPE_HYBRID_STATION | 4 |  |
| ENVIRONMENT_TYPE_MANUAL_LINE | 5 |  |
| ENVIRONMENT_TYPE_AUTOMATIC_LINE | 6 |  |
| ENVIRONMENT_TYPE_HYBRID_LINE | 7 |  |


 

 

 



<a name="ar_v1_authoring_environment-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_environment.proto



<a name="ar-v1-EnvironmentDeleteMessage"></a>

### EnvironmentDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Id of the marker to be deleted |






<a name="ar-v1-EnvironmentNewMessage"></a>

### EnvironmentNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [EnvironmentType](#ar-v1-EnvironmentType) |  |  |






<a name="ar-v1-EnvironmentUpdateMessage"></a>

### EnvironmentUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Unique id of the environment (this won&#39;t be changed) |
| name | [string](#string) |  | Name of the environment |
| icon | [string](#string) |  |  |
| description | [string](#string) |  | Description of the environment |
| type | [EnvironmentType](#ar-v1-EnvironmentType) |  |  |
| markers | [MarkerLocation](#ar-v1-MarkerLocation) | repeated |  |
| agents | [AgentLocation](#ar-v1-AgentLocation) | repeated |  |
| parts | [PartLocation](#ar-v1-PartLocation) | repeated |  |
| tools | [ToolLocation](#ar-v1-ToolLocation) | repeated |  |





 

 

 

 



<a name="ar_v1_authoring_feedback-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_feedback.proto



<a name="ar-v1-FeedbackCloneMessage"></a>

### FeedbackCloneMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| original_id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |






<a name="ar-v1-FeedbackDeleteMessage"></a>

### FeedbackDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |






<a name="ar-v1-FeedbackNewMessage"></a>

### FeedbackNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| parent_config_id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [FeedbackType](#ar-v1-FeedbackType) |  |  |
| frame_id | [string](#string) |  |  |
| agent_id | [string](#string) |  |  |






<a name="ar-v1-FeedbackUpdateMessage"></a>

### FeedbackUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |





 

 

 

 



<a name="ar_v1_mapping-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/mapping.proto



<a name="ar-v1-ARPriority"></a>

### ARPriority



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| ar_config_id | [string](#string) |  |  |
| active_property_id | [string](#string) |  |  |






<a name="ar-v1-MappingMessage"></a>

### MappingMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| environment_ids | [string](#string) | repeated |  |
| ar_config_priorities | [ARPriority](#ar-v1-ARPriority) | repeated |  |






<a name="ar-v1-MappingsMessage"></a>

### MappingsMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| mappings | [MappingMessage](#ar-v1-MappingMessage) | repeated |  |





 

 

 

 



<a name="ar_v1_authoring_mapping-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_mapping.proto



<a name="ar-v1-MappingDeleteMessage"></a>

### MappingDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Id of the marker to be deleted |






<a name="ar-v1-MappingNewMessage"></a>

### MappingNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |






<a name="ar-v1-MappingUpdateMessage"></a>

### MappingUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| environment_ids | [string](#string) | repeated |  |
| ar_config_priorities | [ARPriority](#ar-v1-ARPriority) | repeated |  |





 

 

 

 



<a name="ar_v1_authoring_marker-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/authoring_marker.proto



<a name="ar-v1-MarkerDeleteMessage"></a>

### MarkerDeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Id of the marker to be deleted |






<a name="ar-v1-MarkerNewMessage"></a>

### MarkerNewMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| marker_text | [string](#string) |  |  |






<a name="ar-v1-MarkerUpdateMessage"></a>

### MarkerUpdateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Unique id of the maker (this won&#39;t be changed) |
| name | [string](#string) |  | Name of the maker |
| description | [string](#string) |  | Description of the maker |
| marker_text | [string](#string) |  | Text on the physical marker (QR-code) |





 

 

 

 



<a name="ar_v1_config_load-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/config_load.proto



<a name="ar-v1-ConfigurationLoadMessage"></a>

### ConfigurationLoadMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| config_id | [string](#string) |  | Id of the configuration to be loaded |
| instance_id | [string](#string) |  | Instance id of the current loaded configuration - from the requestors perspective - used to avoid reloading a configuration. |





 

 

 

 



<a name="ar_v1_feedback_info-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/feedback_info.proto



<a name="ar-v1-FeedbackInfoMessage"></a>

### FeedbackInfoMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [FeedbackType](#ar-v1-FeedbackType) |  |  |
| group | [string](#string) |  |  |
| require_agent | [bool](#bool) |  |  |
| require_frame | [bool](#bool) |  |  |
| required_events | [EventType](#ar-v1-EventType) | repeated |  |
| optional_events | [EventType](#ar-v1-EventType) | repeated |  |
| disabled | [bool](#bool) |  |  |






<a name="ar-v1-FeedbackInfosMessage"></a>

### FeedbackInfosMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| feedback_infos | [FeedbackInfoMessage](#ar-v1-FeedbackInfoMessage) | repeated |  |





 

 

 

 



<a name="ar_v1_helper_info-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/helper_info.proto



<a name="ar-v1-HelperInfoMessage"></a>

### HelperInfoMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [HelperType](#ar-v1-HelperType) |  |  |
| group | [string](#string) |  |  |
| require_agent | [bool](#bool) |  |  |
| required_events | [EventType](#ar-v1-EventType) | repeated |  |
| optional_events | [EventType](#ar-v1-EventType) | repeated |  |
| disabled | [bool](#bool) |  |  |






<a name="ar-v1-HelperInfosMessage"></a>

### HelperInfosMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| helper_infos | [HelperInfoMessage](#ar-v1-HelperInfoMessage) | repeated |  |





 

 

 

 



<a name="ar_v1_marker-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/marker.proto



<a name="ar-v1-MarkerMessage"></a>

### MarkerMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| marker_text | [string](#string) |  | Text on the physical marker (QR-code) |
| type | [MarkerType](#ar-v1-MarkerType) |  |  |






<a name="ar-v1-MarkersMessage"></a>

### MarkersMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| markers | [MarkerMessage](#ar-v1-MarkerMessage) | repeated |  |





 


<a name="ar-v1-MarkerType"></a>

### MarkerType


| Name | Number | Description |
| ---- | ------ | ----------- |
| MARKER_TYPE_UNSPECIFIED | 0 |  |
| MARKER_TYPE_QR_CODE | 1 |  |


 

 

 



<a name="ar_v1_template-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## ar/v1/template.proto



<a name="ar-v1-TemplateInfoMessage"></a>

### TemplateInfoMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |






<a name="ar-v1-TemplateInfoMessages"></a>

### TemplateInfoMessages



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| templates | [TemplateInfoMessage](#ar-v1-TemplateInfoMessage) | repeated |  |






<a name="ar-v1-TemplateMessage"></a>

### TemplateMessage
TODO: consider this a bit more?


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| properties | [Property](#ar-v1-Property) | repeated | repeated ar.v1.Agent agents = 5;

Feedback Actions |





 

 

 

 



<a name="common_v1_color-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## common/v1/color.proto



<a name="common-v1-Color"></a>

### Color
Represents a color. Where (1, 1, 1, 1) is solid white, (1, 0, 0, 0.5) is half transparent red, and so on.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| red | [float](#float) |  | Ranging from [0:1] |
| green | [float](#float) |  | Ranging from [0:1] |
| blue | [float](#float) |  | Ranging from [0:1] |
| alpha | [float](#float) |  | Ranging from [0:1] --&gt; [transparent : opaque] |





 

 

 

 



<a name="common_v1_delete-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## common/v1/delete.proto



<a name="common-v1-DeleteMessage"></a>

### DeleteMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Id of the entity to be deleted |
| message | [string](#string) |  | Optional message |





 

 

 

 



<a name="geometry_v1_anchor-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## geometry/v1/anchor.proto



<a name="geometry-v1-Anchor"></a>

### Anchor



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| reference | [string](#string) |  | Reference point towards an object or a thing, e.g. the environment, a robot, the user, ... |
| frame | [string](#string) |  | Frame is something in relation to the reference, e.g. wrist, tcp, left-hand, ... |





 

 

 

 



<a name="geometry_v1_vector3-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## geometry/v1/vector3.proto



<a name="geometry-v1-Vector3"></a>

### Vector3



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| x | [float](#float) |  |  |
| y | [float](#float) |  |  |
| z | [float](#float) |  |  |





 

 

 

 



<a name="geometry_v1_wrench-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## geometry/v1/wrench.proto



<a name="geometry-v1-Wrench"></a>

### Wrench



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| force | [Vector3](#geometry-v1-Vector3) |  |  |
| torque | [Vector3](#geometry-v1-Vector3) |  |  |





 

 

 

 



<a name="plm_v1_capability-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/capability.proto



<a name="plm-v1-Capabilities"></a>

### Capabilities



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| capabilities | [Capability](#plm-v1-Capability) | repeated |  |






<a name="plm-v1-Capability"></a>

### Capability



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| agent_id | [string](#string) |  | Id of the agent (either an operator or robot) |
| part_id | [string](#string) |  | Id of the part that the agent can handle |
| estimated_time | [int64](#int64) |  | Estimated time to complete a task with that part |





 

 

 

 



<a name="plm_v1_line-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/line.proto



<a name="plm-v1-LineMessage"></a>

### LineMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [LineType](#plm-v1-LineType) |  | TODO: agents TODO: capabilities |





 


<a name="plm-v1-LineType"></a>

### LineType


| Name | Number | Description |
| ---- | ------ | ----------- |
| LINE_TYPE_UNSPECIFIED | 0 |  |
| LINE_TYPE_SUB_ASSEMBLY | 1 |  |
| LINE_TYPE_FASTENER | 2 |  |
| LINE_TYPE_PLATE | 3 |  |
| LINE_TYPE_LUBRICANT | 4 |  |


 

 

 



<a name="plm_v1_models-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/models.proto



<a name="plm-v1-ModelMessage"></a>

### ModelMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| url | [string](#string) |  |  |






<a name="plm-v1-ModelMessages"></a>

### ModelMessages



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| models | [ModelMessage](#plm-v1-ModelMessage) | repeated |  |





 

 

 

 



<a name="plm_v1_part-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/part.proto



<a name="plm-v1-DeletePartMessage"></a>

### DeletePartMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| part_id | [string](#string) |  |  |






<a name="plm-v1-NewPartMessage"></a>

### NewPartMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [PartType](#plm-v1-PartType) |  |  |






<a name="plm-v1-PartMessage"></a>

### PartMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [PartType](#plm-v1-PartType) |  |  |
| weight | [int64](#int64) |  |  |
| model_id | [string](#string) |  |  |
| tool_ids | [string](#string) | repeated |  |






<a name="plm-v1-PartMessages"></a>

### PartMessages



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| parts | [PartMessage](#plm-v1-PartMessage) | repeated |  |






<a name="plm-v1-UpdatePartMessage"></a>

### UpdatePartMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [PartType](#plm-v1-PartType) |  |  |
| weight | [int64](#int64) |  |  |
| model_id | [string](#string) |  |  |
| tool_ids | [string](#string) | repeated |  |





 


<a name="plm-v1-PartType"></a>

### PartType


| Name | Number | Description |
| ---- | ------ | ----------- |
| PART_TYPE_UNSPECIFIED | 0 |  |
| PART_TYPE_SUB_ASSEMBLY | 1 |  |
| PART_TYPE_FASTENER | 2 |  |
| PART_TYPE_PLATE | 3 |  |
| PART_TYPE_LUBRICANT | 4 |  |


 

 

 



<a name="plm_v1_sequence-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/sequence.proto



<a name="plm-v1-SequenceMessage"></a>

### SequenceMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| frame | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| parent_id | [string](#string) |  |  |
| sequence_ids | [string](#string) | repeated |  |
| task_ids | [string](#string) | repeated |  |
| assigned_to | [string](#string) | repeated |  |
| state | [SequenceState](#plm-v1-SequenceState) |  |  |
| completed_tasks | [int64](#int64) |  |  |
| can_bulk_complete | [bool](#bool) |  |  |






<a name="plm-v1-SequenceUpdatedMessage"></a>

### SequenceUpdatedMessage
Update published when the state of a sequence have changed


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| sequence_id | [string](#string) |  |  |
| assigned_to | [string](#string) | repeated |  |
| state | [SequenceState](#plm-v1-SequenceState) |  |  |
| completed_tasks | [int64](#int64) |  |  |





 


<a name="plm-v1-SequenceState"></a>

### SequenceState


| Name | Number | Description |
| ---- | ------ | ----------- |
| SEQUENCE_STATE_UNSPECIFIED | 0 |  |
| SEQUENCE_STATE_MISSING_PRECONDITION | 1 |  |
| SEQUENCE_STATE_WAITING | 2 |  |
| SEQUENCE_STATE_IN_PROGRESS | 3 |  |
| SEQUENCE_STATE_COMPLETED | 4 |  |


 

 

 



<a name="plm_v1_task-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/task.proto



<a name="plm-v1-TaskMessage"></a>

### TaskMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| part_id | [string](#string) |  |  |
| model_id | [string](#string) |  |  |
| task_type | [TaskType](#plm-v1-TaskType) |  |  |
| target | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| approach | [geometry.v1.Vector3](#geometry-v1-Vector3) |  |  |
| parent_id | [string](#string) |  |  |
| agents_ids | [string](#string) | repeated |  |
| assigned_to | [string](#string) |  |  |
| state | [TaskState](#plm-v1-TaskState) |  |  |
| preconditions | [string](#string) | repeated |  |
| dependants | [string](#string) | repeated |  |
| assignment_preference | [TaskAssignmentPreference](#plm-v1-TaskAssignmentPreference) |  |  |
| can_reassign | [bool](#bool) |  |  |
| can_do | [bool](#bool) |  |  |
| can_undo | [bool](#bool) |  | TODO: &#39;complete-importance&#39;: could be different levels of &#34;this must be explicitly completed&#34; or tie it together with user level, such that expertise level (expert, intermediate, novice) equal and above intermediate can {bulk, automatic, ... } complete and below must explicitly complete. This should potentially also be tied to the part and this field(s) can then be a custom override for this specific task. |






<a name="plm-v1-TaskUpdatedMessage"></a>

### TaskUpdatedMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| assigned_to | [string](#string) |  |  |
| state | [TaskState](#plm-v1-TaskState) |  |  |
| can_reassign | [bool](#bool) |  |  |
| can_do | [bool](#bool) |  |  |
| can_undo | [bool](#bool) |  |  |





 


<a name="plm-v1-TaskAssignmentPreference"></a>

### TaskAssignmentPreference


| Name | Number | Description |
| ---- | ------ | ----------- |
| TASK_ASSIGNMENT_PREFERENCE_UNSPECIFIED | 0 |  |
| TASK_ASSIGNMENT_PREFERENCE_PREFER_HUMAN | 1 |  |
| TASK_ASSIGNMENT_PREFERENCE_ONLY_HUMAN | 2 |  |
| TASK_ASSIGNMENT_PREFERENCE_PREFER_ROBOT | 3 |  |
| TASK_ASSIGNMENT_PREFERENCE_ONLY_ROBOT | 4 |  |



<a name="plm-v1-TaskState"></a>

### TaskState


| Name | Number | Description |
| ---- | ------ | ----------- |
| TASK_STATE_UNSPECIFIED | 0 |  |
| TASK_STATE_MISSING_PRECONDITION | 1 |  |
| TASK_STATE_WAITING | 2 |  |
| TASK_STATE_IN_PROGRESS | 3 |  |
| TASK_STATE_COMPLETED | 4 |  |
| TASK_STATE_ERROR | 6 |  |



<a name="plm-v1-TaskType"></a>

### TaskType


| Name | Number | Description |
| ---- | ------ | ----------- |
| TASK_TYPE_UNSPECIFIED | 0 |  |
| TASK_TYPE_INSPECT | 1 |  |
| TASK_TYPE_FASTEN | 2 |  |
| TASK_TYPE_UNFASTEN | 3 |  |
| TASK_TYPE_MOUNT | 4 |  |
| TASK_TYPE_UNMOUNT | 5 |  |
| TASK_TYPE_MOVE | 6 |  |
| TASK_TYPE_REMOVE | 7 |  |
| TASK_TYPE_APPLY | 8 |  |
| TASK_TYPE_WIPE | 9 |  |


 

 

 



<a name="plm_v1_process-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/process.proto



<a name="plm-v1-ProcessMessage"></a>

### ProcessMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| instance_id | [string](#string) |  |  |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ProcessType](#plm-v1-ProcessType) |  |  |
| frame | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| root_sequence_id | [string](#string) |  |  |
| sequences | [SequenceMessage](#plm-v1-SequenceMessage) | repeated |  |
| tasks | [TaskMessage](#plm-v1-TaskMessage) | repeated |  |
| state | [ProcessState](#plm-v1-ProcessState) |  |  |
| initiated | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |
| ended | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |
| order_id | [string](#string) |  |  |
| line_id | [string](#string) |  |  |






<a name="plm-v1-ProcessUpdatedMessage"></a>

### ProcessUpdatedMessage
Update published when the state of a process have changed


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| instance_id | [string](#string) |  |  |
| id | [string](#string) |  |  |
| state | [ProcessState](#plm-v1-ProcessState) |  |  |
| ended | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |






<a name="plm-v1-ProcessesMessage"></a>

### ProcessesMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| processes | [ProcessMessage](#plm-v1-ProcessMessage) | repeated |  |





 


<a name="plm-v1-ProcessState"></a>

### ProcessState


| Name | Number | Description |
| ---- | ------ | ----------- |
| PROCESS_STATE_UNSPECIFIED | 0 |  |
| PROCESS_STATE_WAITING | 1 |  |
| PROCESS_STATE_IN_PROGRESS | 2 |  |
| PROCESS_STATE_COMPLETED | 3 |  |
| PROCESS_STATE_ABORTED | 4 |  |



<a name="plm-v1-ProcessType"></a>

### ProcessType


| Name | Number | Description |
| ---- | ------ | ----------- |
| PROCESS_TYPE_UNSPECIFIED | 0 |  |
| PROCESS_TYPE_ASSEMBLY | 1 |  |
| PROCESS_TYPE_DISASSEMBLY | 2 |  |
| PROCESS_TYPE_INSPECTION | 3 |  |


 

 

 



<a name="plm_v1_process_abort-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/process_abort.proto



<a name="plm-v1-ProcessAbortMessage"></a>

### ProcessAbortMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| reason | [string](#string) |  |  |





 

 

 

 



<a name="plm_v1_sequence_authoring-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/sequence_authoring.proto



<a name="plm-v1-DeleteSequenceMessage"></a>

### DeleteSequenceMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| sequence_id | [string](#string) |  |  |






<a name="plm-v1-NewSequenceMessage"></a>

### NewSequenceMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| parent_id | [string](#string) |  |  |






<a name="plm-v1-StoredSequenceMessage"></a>

### StoredSequenceMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| frame | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| parent_id | [string](#string) |  |  |
| sequence_ids | [string](#string) | repeated |  |
| task_ids | [string](#string) | repeated |  |
| can_bulk_complete | [bool](#bool) |  |  |






<a name="plm-v1-UpdateSequenceMessage"></a>

### UpdateSequenceMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| frame | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| parent_id | [string](#string) |  |  |
| sequence_ids | [string](#string) | repeated |  |
| task_ids | [string](#string) | repeated |  |
| can_bulk_complete | [bool](#bool) |  |  |





 

 

 

 



<a name="plm_v1_process_authoring-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/process_authoring.proto



<a name="plm-v1-DeleteProcessMessage"></a>

### DeleteProcessMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| process_id | [string](#string) |  |  |






<a name="plm-v1-NewProcessMessage"></a>

### NewProcessMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ProcessType](#plm-v1-ProcessType) |  |  |






<a name="plm-v1-StoredProcessMessage"></a>

### StoredProcessMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ProcessType](#plm-v1-ProcessType) |  |  |
| frame | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| root_sequence_id | [string](#string) |  |  |
| sequences | [StoredSequenceMessage](#plm-v1-StoredSequenceMessage) | repeated |  |
| tasks | [TaskMessage](#plm-v1-TaskMessage) | repeated |  |






<a name="plm-v1-StoredProcessesMessage"></a>

### StoredProcessesMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| processes | [StoredProcessMessage](#plm-v1-StoredProcessMessage) | repeated |  |






<a name="plm-v1-UpdateProcessMessage"></a>

### UpdateProcessMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [ProcessType](#plm-v1-ProcessType) |  |  |
| frame | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| root_sequence_id | [string](#string) |  |  |





 

 

 

 



<a name="plm_v1_process_load-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/process_load.proto



<a name="plm-v1-ProcessLoadMessage"></a>

### ProcessLoadMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| process_id | [string](#string) |  |  |
| line_id | [string](#string) |  |  |
| order_id | [string](#string) |  |  |
| allocation_strategy | [AllocationStrategy](#plm-v1-AllocationStrategy) |  | TODO: list participating actors? |





 


<a name="plm-v1-AllocationStrategy"></a>

### AllocationStrategy


| Name | Number | Description |
| ---- | ------ | ----------- |
| ALLOCATION_STRATEGY_UNSPECIFIED | 0 |  |
| ALLOCATION_STRATEGY_STATIC | 1 |  |


 

 

 



<a name="plm_v1_requests-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/requests.proto



<a name="plm-v1-ProcessAtLocationMessage"></a>

### ProcessAtLocationMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| location_id | [string](#string) |  |  |





 

 

 

 



<a name="plm_v1_sequence_complete-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/sequence_complete.proto



<a name="plm-v1-SequenceBulkCompleteMessage"></a>

### SequenceBulkCompleteMessage
Complete all tasks or or sub-sequences (TODO: should that be possible?)


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| sequence_id | [string](#string) |  |  |
| agent_id | [string](#string) |  |  |





 

 

 

 



<a name="plm_v1_sequence_reassign-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/sequence_reassign.proto



<a name="plm-v1-SequenceReassignMessage"></a>

### SequenceReassignMessage
Reassign all sub-tasks to the assignee (if possible)


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| sequence_id | [string](#string) |  |  |
| assignee | [string](#string) |  |  |





 

 

 

 



<a name="plm_v1_task_authoring-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/task_authoring.proto



<a name="plm-v1-DeleteTaskMessage"></a>

### DeleteTaskMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| task_id | [string](#string) |  |  |






<a name="plm-v1-NewTaskMessage"></a>

### NewTaskMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| parent_sequence_id | [string](#string) |  |  |






<a name="plm-v1-StoredTaskMessage"></a>

### StoredTaskMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| part_id | [string](#string) |  |  |
| model_id | [string](#string) |  |  |
| task_type | [TaskType](#plm-v1-TaskType) |  |  |
| target | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| approach | [geometry.v1.Vector3](#geometry-v1-Vector3) |  |  |
| assignment_preference | [TaskAssignmentPreference](#plm-v1-TaskAssignmentPreference) |  |  |






<a name="plm-v1-UpdateTaskMessage"></a>

### UpdateTaskMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| sequence_number | [int64](#int64) |  |  |
| part_id | [string](#string) |  |  |
| model_id | [string](#string) |  |  |
| task_type | [TaskType](#plm-v1-TaskType) |  |  |
| target | [geometry.v1.LocalizedPose](#geometry-v1-LocalizedPose) |  |  |
| approach | [geometry.v1.Vector3](#geometry-v1-Vector3) |  |  |
| assignment_preference | [TaskAssignmentPreference](#plm-v1-TaskAssignmentPreference) |  |  |





 

 

 

 



<a name="plm_v1_task_progress-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/task_progress.proto



<a name="plm-v1-TaskProgressMessage"></a>

### TaskProgressMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| task_id | [string](#string) |  |  |
| agent_id | [string](#string) |  |  |
| message | [string](#string) |  |  |
| elapsed_time | [int64](#int64) |  |  |
| estimated_time_left | [int64](#int64) |  |  |





 

 

 

 



<a name="plm_v1_task_reassign-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/task_reassign.proto



<a name="plm-v1-TaskReassignMessage"></a>

### TaskReassignMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| task_id | [string](#string) |  |  |
| assignee | [string](#string) |  |  |





 

 

 

 



<a name="plm_v1_task_state_change-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/task_state_change.proto



<a name="plm-v1-TaskStateChangeMessage"></a>

### TaskStateChangeMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| task_id | [string](#string) |  |  |
| state | [TaskStateRequest](#plm-v1-TaskStateRequest) |  |  |





 


<a name="plm-v1-TaskStateRequest"></a>

### TaskStateRequest


| Name | Number | Description |
| ---- | ------ | ----------- |
| TASK_STATE_REQUEST_UNSPECIFIED | 0 |  |
| TASK_STATE_REQUEST_IN_PROGRESS | 3 |  |
| TASK_STATE_REQUEST_COMPLETED | 4 |  |
| TASK_STATE_REQUEST_UNDO | 5 |  |
| TASK_STATE_REQUEST_ERROR | 6 |  |


 

 

 



<a name="plm_v1_tasks_list-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/tasks_list.proto



<a name="plm-v1-TasksForAgentRequest"></a>

### TasksForAgentRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| agent_id | [string](#string) |  |  |
| state | [TaskState](#plm-v1-TaskState) |  | Filter based on state. 0 (unspecified) returns all |






<a name="plm-v1-TasksForAgentResponse"></a>

### TasksForAgentResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| instance_id | [string](#string) |  |  |
| agent_id | [string](#string) |  |  |
| task_ids | [string](#string) | repeated |  |





 

 

 

 



<a name="plm_v1_tool-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## plm/v1/tool.proto



<a name="plm-v1-DeleteToolMessage"></a>

### DeleteToolMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tool_id | [string](#string) |  |  |






<a name="plm-v1-NewToolMessage"></a>

### NewToolMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |






<a name="plm-v1-ToolMessage"></a>

### ToolMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| model_id | [string](#string) |  |  |






<a name="plm-v1-ToolMessages"></a>

### ToolMessages



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tools | [ToolMessage](#plm-v1-ToolMessage) | repeated |  |






<a name="plm-v1-UpdateToolMessage"></a>

### UpdateToolMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| icon | [string](#string) |  |  |
| description | [string](#string) |  |  |
| model_id | [string](#string) |  |  |





 

 

 

 



<a name="robot_v1_end_effector-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/end_effector.proto



<a name="robot-v1-EndEffectorStateMessage"></a>

### EndEffectorStateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| live | [bool](#bool) |  |  |
| state | [string](#string) |  |  |





 

 

 

 



<a name="robot_v1_jointstate-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/jointstate.proto



<a name="robot-v1-JointStateMessage"></a>

### JointStateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| live | [bool](#bool) |  |  |
| position | [double](#double) | repeated |  |
| velocity | [double](#double) | repeated |  |





 

 

 

 



<a name="robot_v1_path-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/path.proto



<a name="robot-v1-PathMessage"></a>

### PathMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| robot_id | [string](#string) |  |  |
| points | [geometry.v1.Point](#geometry-v1-Point) | repeated |  |





 

 

 

 



<a name="robot_v1_popup-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/popup.proto



<a name="robot-v1-RobotHidePopupRequest"></a>

### RobotHidePopupRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| robot_id | [string](#string) |  |  |






<a name="robot-v1-RobotShowPopupRequest"></a>

### RobotShowPopupRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| robot_id | [string](#string) |  |  |
| text | [string](#string) |  |  |





 

 

 

 



<a name="robot_v1_program_state-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/program_state.proto



<a name="robot-v1-ProgramStateMessage"></a>

### ProgramStateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| state_code | [ProgramState](#robot-v1-ProgramState) |  |  |
| state | [string](#string) |  |  |
| program_file | [string](#string) |  |  |





 


<a name="robot-v1-ProgramState"></a>

### ProgramState


| Name | Number | Description |
| ---- | ------ | ----------- |
| PROGRAM_STATE_UNSPECIFIED | 0 |  |
| PROGRAM_STATE_PLAY | 1 |  |
| PROGRAM_STATE_PAUSE | 2 |  |
| PROGRAM_STATE_STOP | 3 |  |


 

 

 



<a name="robot_v1_program_state_request-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/program_state_request.proto



<a name="robot-v1-ProgramStateRequest"></a>

### ProgramStateRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| robot_id | [string](#string) |  |  |
| state | [ProgramState](#robot-v1-ProgramState) |  |  |





 

 

 

 



<a name="robot_v1_robot_state-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/robot_state.proto



<a name="robot-v1-RobotStateMessage"></a>

### RobotStateMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| state_code | [RobotState](#robot-v1-RobotState) |  |  |
| state | [string](#string) |  |  |
| target_speed | [double](#double) |  |  |
| actual_speed | [double](#double) |  |  |





 


<a name="robot-v1-RobotState"></a>

### RobotState


| Name | Number | Description |
| ---- | ------ | ----------- |
| ROBOT_STATE_UNSPECIFIED | 0 |  |
| ROBOT_STATE_STOPPING | 1 |  |
| ROBOT_STATE_STOPPED | 2 |  |
| ROBOT_STATE_PLAYING | 3 |  |
| ROBOT_STATE_PAUSING | 4 |  |
| ROBOT_STATE_PAUSED | 5 |  |
| ROBOT_STATE_RESUMING | 6 |  |


 

 

 



<a name="robot_v1_robot_visibility-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/robot_visibility.proto



<a name="robot-v1-RobotVisibilityMessage"></a>

### RobotVisibilityMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| base_visible | [bool](#bool) |  |  |
| upper_arm_visible | [bool](#bool) |  |  |
| forearm_visible | [bool](#bool) |  |  |
| wrist_visible | [bool](#bool) |  |  |
| end_effector_visible | [bool](#bool) |  |  |
| tcp_visible | [bool](#bool) |  |  |





 

 

 

 



<a name="robot_v1_tcp-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/tcp.proto



<a name="robot-v1-TcpMessage"></a>

### TcpMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| position | [geometry.v1.Point](#geometry-v1-Point) |  |  |
| orientation | [geometry.v1.Quad](#geometry-v1-Quad) |  |  |





 

 

 

 



<a name="robot_v1_waypoints-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/waypoints.proto



<a name="robot-v1-WaypointMessage"></a>

### WaypointMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| point | [geometry.v1.Point](#geometry-v1-Point) |  |  |






<a name="robot-v1-WaypointsMessage"></a>

### WaypointsMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| robot_id | [string](#string) |  |  |
| frame_id | [string](#string) |  |  |
| highlight_idx | [int32](#int32) |  |  |
| waypoints | [WaypointMessage](#robot-v1-WaypointMessage) | repeated |  |





 

 

 

 



<a name="robot_v1_zone-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## robot/v1/zone.proto



<a name="robot-v1-ZoneMessage"></a>

### ZoneMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| frame_id | [string](#string) |  |  |
| points | [geometry.v1.Point](#geometry-v1-Point) | repeated |  |





 

 

 

 



<a name="service_v1_ar_client-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## service/v1/ar_client.proto



<a name="service-v1-ARClientMessage"></a>

### ARClientMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| role | [ARClientRole](#service-v1-ARClientRole) |  |  |
| operator_id | [string](#string) |  |  |





 


<a name="service-v1-ARClientRole"></a>

### ARClientRole


| Name | Number | Description |
| ---- | ------ | ----------- |
| AR_CLIENT_ROLE_UNSPECIFIED | 0 |  |
| AR_CLIENT_ROLE_MAIN | 1 |  |
| AR_CLIENT_ROLE_SPECTATOR | 2 |  |


 

 

 



<a name="service_v1_response-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## service/v1/response.proto



<a name="service-v1-Response"></a>

### Response



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| request_id | [string](#string) |  |  |
| success | [bool](#bool) |  | True if the request was carried out |
| message | [string](#string) |  | Either a status/response message or an error message if the request wasn&#39;t a success |





 

 

 

 



<a name="service_v1_robot_adapter-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## service/v1/robot_adapter.proto



<a name="service-v1-RobotAdapterInfoMessage"></a>

### RobotAdapterInfoMessage



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| robot_id | [string](#string) |  |  |
| robot_type | [string](#string) |  | TODO: use type enum? |
| identifier | [string](#string) |  |  |





 

 

 

 



<a name="service_v1_status-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## service/v1/status.proto



<a name="service-v1-ServiceStatus"></a>

### ServiceStatus



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  |  |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| type | [string](#string) |  |  |
| ip | [string](#string) |  |  |
| status | [Status](#service-v1-Status) |  |  |





 


<a name="service-v1-Status"></a>

### Status


| Name | Number | Description |
| ---- | ------ | ----------- |
| STATUS_UNSPECIFIED | 0 |  |
| STATUS_OFFLINE | 1 |  |
| STATUS_ONLINE | 2 |  |


 

 

 



## Scalar Value Types

| .proto Type | Notes | C++ | Java | Python | Go | C# | PHP | Ruby |
| ----------- | ----- | --- | ---- | ------ | -- | -- | --- | ---- |
| <a name="double" /> double |  | double | double | float | float64 | double | float | Float |
| <a name="float" /> float |  | float | float | float | float32 | float | float | Float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="bool" /> bool |  | bool | boolean | boolean | bool | bool | boolean | TrueClass/FalseClass |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode | string | string | string | String (UTF-8) |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str | []byte | ByteString | string | String (ASCII-8BIT) |

