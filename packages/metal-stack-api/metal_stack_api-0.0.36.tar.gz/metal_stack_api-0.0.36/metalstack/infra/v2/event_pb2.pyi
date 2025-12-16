import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProvisioningEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROVISIONING_EVENT_TYPE_UNSPECIFIED: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_ALIVE: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_CRASHED: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_PXE_BOOTING: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_PLANNED_REBOOT: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_PREPARING: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_REGISTERING: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_WAITING: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_INSTALLING: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_BOOTING_NEW_KERNEL: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_PHONED_HOME: _ClassVar[ProvisioningEventType]
    PROVISIONING_EVENT_TYPE_MACHINE_RECLAIM: _ClassVar[ProvisioningEventType]
PROVISIONING_EVENT_TYPE_UNSPECIFIED: ProvisioningEventType
PROVISIONING_EVENT_TYPE_ALIVE: ProvisioningEventType
PROVISIONING_EVENT_TYPE_CRASHED: ProvisioningEventType
PROVISIONING_EVENT_TYPE_PXE_BOOTING: ProvisioningEventType
PROVISIONING_EVENT_TYPE_PLANNED_REBOOT: ProvisioningEventType
PROVISIONING_EVENT_TYPE_PREPARING: ProvisioningEventType
PROVISIONING_EVENT_TYPE_REGISTERING: ProvisioningEventType
PROVISIONING_EVENT_TYPE_WAITING: ProvisioningEventType
PROVISIONING_EVENT_TYPE_INSTALLING: ProvisioningEventType
PROVISIONING_EVENT_TYPE_BOOTING_NEW_KERNEL: ProvisioningEventType
PROVISIONING_EVENT_TYPE_PHONED_HOME: ProvisioningEventType
PROVISIONING_EVENT_TYPE_MACHINE_RECLAIM: ProvisioningEventType

class EventServiceSendRequest(_message.Message):
    __slots__ = ("events",)
    class EventsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MachineProvisioningEvent
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MachineProvisioningEvent, _Mapping]] = ...) -> None: ...
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.MessageMap[str, MachineProvisioningEvent]
    def __init__(self, events: _Optional[_Mapping[str, MachineProvisioningEvent]] = ...) -> None: ...

class EventServiceSendResponse(_message.Message):
    __slots__ = ("events", "failed")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    events: int
    failed: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, events: _Optional[int] = ..., failed: _Optional[_Iterable[str]] = ...) -> None: ...

class MachineProvisioningEvent(_message.Message):
    __slots__ = ("time", "event", "message")
    TIME_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    event: ProvisioningEventType
    message: str
    def __init__(self, time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[ProvisioningEventType, str]] = ..., message: _Optional[str] = ...) -> None: ...
