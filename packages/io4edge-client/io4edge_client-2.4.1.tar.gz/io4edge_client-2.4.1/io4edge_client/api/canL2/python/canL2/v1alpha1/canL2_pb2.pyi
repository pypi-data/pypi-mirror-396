from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ControllerState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_OK: _ClassVar[ControllerState]
    CAN_ERROR_PASSIVE: _ClassVar[ControllerState]
    CAN_BUS_OFF: _ClassVar[ControllerState]

class ErrorEvent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_NO_ERROR: _ClassVar[ErrorEvent]
    CAN_TX_FAILED: _ClassVar[ErrorEvent]
    CAN_RX_QUEUE_FULL: _ClassVar[ErrorEvent]
    CAN_ARB_LOST: _ClassVar[ErrorEvent]
    CAN_BUS_ERROR: _ClassVar[ErrorEvent]
CAN_OK: ControllerState
CAN_ERROR_PASSIVE: ControllerState
CAN_BUS_OFF: ControllerState
CAN_NO_ERROR: ErrorEvent
CAN_TX_FAILED: ErrorEvent
CAN_RX_QUEUE_FULL: ErrorEvent
CAN_ARB_LOST: ErrorEvent
CAN_BUS_ERROR: ErrorEvent

class ConfigurationSet(_message.Message):
    __slots__ = ("baud", "samplePoint", "sjw", "listenOnly")
    BAUD_FIELD_NUMBER: _ClassVar[int]
    SAMPLEPOINT_FIELD_NUMBER: _ClassVar[int]
    SJW_FIELD_NUMBER: _ClassVar[int]
    LISTENONLY_FIELD_NUMBER: _ClassVar[int]
    baud: int
    samplePoint: int
    sjw: int
    listenOnly: bool
    def __init__(self, baud: _Optional[int] = ..., samplePoint: _Optional[int] = ..., sjw: _Optional[int] = ..., listenOnly: _Optional[bool] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("baud", "samplePoint", "sjw", "listenOnly")
    BAUD_FIELD_NUMBER: _ClassVar[int]
    SAMPLEPOINT_FIELD_NUMBER: _ClassVar[int]
    SJW_FIELD_NUMBER: _ClassVar[int]
    LISTENONLY_FIELD_NUMBER: _ClassVar[int]
    baud: int
    samplePoint: int
    sjw: int
    listenOnly: bool
    def __init__(self, baud: _Optional[int] = ..., samplePoint: _Optional[int] = ..., sjw: _Optional[int] = ..., listenOnly: _Optional[bool] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationResponse(_message.Message):
    __slots__ = ("get", "set", "describe")
    GET_FIELD_NUMBER: _ClassVar[int]
    SET_FIELD_NUMBER: _ClassVar[int]
    DESCRIBE_FIELD_NUMBER: _ClassVar[int]
    get: ConfigurationGetResponse
    set: ConfigurationSetResponse
    describe: ConfigurationDescribeResponse
    def __init__(self, get: _Optional[_Union[ConfigurationGetResponse, _Mapping]] = ..., set: _Optional[_Union[ConfigurationSetResponse, _Mapping]] = ..., describe: _Optional[_Union[ConfigurationDescribeResponse, _Mapping]] = ...) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Frame(_message.Message):
    __slots__ = ("extendedFrameFormat", "remoteFrame", "messageId", "data")
    EXTENDEDFRAMEFORMAT_FIELD_NUMBER: _ClassVar[int]
    REMOTEFRAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    extendedFrameFormat: bool
    remoteFrame: bool
    messageId: int
    data: bytes
    def __init__(self, extendedFrameFormat: _Optional[bool] = ..., remoteFrame: _Optional[bool] = ..., messageId: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("frame",)
    FRAME_FIELD_NUMBER: _ClassVar[int]
    frame: _containers.RepeatedCompositeFieldContainer[Frame]
    def __init__(self, frame: _Optional[_Iterable[_Union[Frame, _Mapping]]] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("controllerState",)
    CONTROLLERSTATE_FIELD_NUMBER: _ClassVar[int]
    controllerState: ControllerState
    def __init__(self, controllerState: _Optional[_Union[ControllerState, str]] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("acceptanceCode", "acceptanceMask")
    ACCEPTANCECODE_FIELD_NUMBER: _ClassVar[int]
    ACCEPTANCEMASK_FIELD_NUMBER: _ClassVar[int]
    acceptanceCode: int
    acceptanceMask: int
    def __init__(self, acceptanceCode: _Optional[int] = ..., acceptanceMask: _Optional[int] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "frame", "controllerState", "error", "isDataFrame")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    CONTROLLERSTATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ISDATAFRAME_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    frame: Frame
    controllerState: ControllerState
    error: ErrorEvent
    isDataFrame: bool
    def __init__(self, timestamp: _Optional[int] = ..., frame: _Optional[_Union[Frame, _Mapping]] = ..., controllerState: _Optional[_Union[ControllerState, str]] = ..., error: _Optional[_Union[ErrorEvent, str]] = ..., isDataFrame: _Optional[bool] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
