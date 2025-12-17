from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[Status]
    UNSPECIFIC_ERROR: _ClassVar[Status]
    UNKNOWN_COMMAND: _ClassVar[Status]
    NOT_IMPLEMENTED: _ClassVar[Status]
    WRONG_CLIENT: _ClassVar[Status]
    INVALID_PARAMETER: _ClassVar[Status]
    HW_FAULT: _ClassVar[Status]
    STREAM_ALREADY_STARTED: _ClassVar[Status]
    STREAM_ALREADY_STOPPED: _ClassVar[Status]
    STREAM_START_FAILED: _ClassVar[Status]
    TEMPORARILY_UNAVAILABLE: _ClassVar[Status]
OK: Status
UNSPECIFIC_ERROR: Status
UNKNOWN_COMMAND: Status
NOT_IMPLEMENTED: Status
WRONG_CLIENT: Status
INVALID_PARAMETER: Status
HW_FAULT: Status
STREAM_ALREADY_STARTED: Status
STREAM_ALREADY_STOPPED: Status
STREAM_START_FAILED: Status
TEMPORARILY_UNAVAILABLE: Status

class Context(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("context", "Configuration", "functionControl", "streamControl")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONCONTROL_FIELD_NUMBER: _ClassVar[int]
    STREAMCONTROL_FIELD_NUMBER: _ClassVar[int]
    context: Context
    Configuration: Configuration
    functionControl: FunctionControl
    streamControl: StreamControl
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ..., Configuration: _Optional[_Union[Configuration, _Mapping]] = ..., functionControl: _Optional[_Union[FunctionControl, _Mapping]] = ..., streamControl: _Optional[_Union[StreamControl, _Mapping]] = ...) -> None: ...

class Configuration(_message.Message):
    __slots__ = ("functionSpecificConfigurationSet", "functionSpecificConfigurationGet", "functionSpecificConfigurationDescribe")
    FUNCTIONSPECIFICCONFIGURATIONSET_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICCONFIGURATIONGET_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICCONFIGURATIONDESCRIBE_FIELD_NUMBER: _ClassVar[int]
    functionSpecificConfigurationSet: _any_pb2.Any
    functionSpecificConfigurationGet: _any_pb2.Any
    functionSpecificConfigurationDescribe: _any_pb2.Any
    def __init__(self, functionSpecificConfigurationSet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., functionSpecificConfigurationGet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., functionSpecificConfigurationDescribe: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class FunctionControl(_message.Message):
    __slots__ = ("functionSpecificFunctionControlSet", "functionSpecificFunctionControlGet")
    FUNCTIONSPECIFICFUNCTIONCONTROLSET_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICFUNCTIONCONTROLGET_FIELD_NUMBER: _ClassVar[int]
    functionSpecificFunctionControlSet: _any_pb2.Any
    functionSpecificFunctionControlGet: _any_pb2.Any
    def __init__(self, functionSpecificFunctionControlSet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., functionSpecificFunctionControlGet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("bucketSamples", "keepaliveInterval", "bufferedSamples", "functionSpecificStreamControlStart", "low_latency_mode")
    BUCKETSAMPLES_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVEINTERVAL_FIELD_NUMBER: _ClassVar[int]
    BUFFEREDSAMPLES_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICSTREAMCONTROLSTART_FIELD_NUMBER: _ClassVar[int]
    LOW_LATENCY_MODE_FIELD_NUMBER: _ClassVar[int]
    bucketSamples: int
    keepaliveInterval: int
    bufferedSamples: int
    functionSpecificStreamControlStart: _any_pb2.Any
    low_latency_mode: bool
    def __init__(self, bucketSamples: _Optional[int] = ..., keepaliveInterval: _Optional[int] = ..., bufferedSamples: _Optional[int] = ..., functionSpecificStreamControlStart: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., low_latency_mode: _Optional[bool] = ...) -> None: ...

class StreamControlStop(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControl(_message.Message):
    __slots__ = ("start", "stop")
    START_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    start: StreamControlStart
    stop: StreamControlStop
    def __init__(self, start: _Optional[_Union[StreamControlStart, _Mapping]] = ..., stop: _Optional[_Union[StreamControlStop, _Mapping]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class ConfigurationResponse(_message.Message):
    __slots__ = ("functionSpecificConfigurationSet", "functionSpecificConfigurationGet", "functionSpecificConfigurationDescribe")
    FUNCTIONSPECIFICCONFIGURATIONSET_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICCONFIGURATIONGET_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICCONFIGURATIONDESCRIBE_FIELD_NUMBER: _ClassVar[int]
    functionSpecificConfigurationSet: _any_pb2.Any
    functionSpecificConfigurationGet: _any_pb2.Any
    functionSpecificConfigurationDescribe: _any_pb2.Any
    def __init__(self, functionSpecificConfigurationSet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., functionSpecificConfigurationGet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., functionSpecificConfigurationDescribe: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class FunctionControlResponse(_message.Message):
    __slots__ = ("functionSpecificFunctionControlSet", "functionSpecificFunctionControlGet")
    FUNCTIONSPECIFICFUNCTIONCONTROLSET_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICFUNCTIONCONTROLGET_FIELD_NUMBER: _ClassVar[int]
    functionSpecificFunctionControlSet: _any_pb2.Any
    functionSpecificFunctionControlGet: _any_pb2.Any
    def __init__(self, functionSpecificFunctionControlSet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., functionSpecificFunctionControlGet: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class StreamControlResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("deliveryTimestampUs", "sequence", "functionSpecificStreamData")
    DELIVERYTIMESTAMPUS_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONSPECIFICSTREAMDATA_FIELD_NUMBER: _ClassVar[int]
    deliveryTimestampUs: int
    sequence: int
    functionSpecificStreamData: _any_pb2.Any
    def __init__(self, deliveryTimestampUs: _Optional[int] = ..., sequence: _Optional[int] = ..., functionSpecificStreamData: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("context", "status", "error", "Configuration", "functionControl", "streamControl", "stream")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONCONTROL_FIELD_NUMBER: _ClassVar[int]
    STREAMCONTROL_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    context: Context
    status: Status
    error: Error
    Configuration: ConfigurationResponse
    functionControl: FunctionControlResponse
    streamControl: StreamControlResponse
    stream: StreamData
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ..., status: _Optional[_Union[Status, str]] = ..., error: _Optional[_Union[Error, _Mapping]] = ..., Configuration: _Optional[_Union[ConfigurationResponse, _Mapping]] = ..., functionControl: _Optional[_Union[FunctionControlResponse, _Mapping]] = ..., streamControl: _Optional[_Union[StreamControlResponse, _Mapping]] = ..., stream: _Optional[_Union[StreamData, _Mapping]] = ...) -> None: ...
