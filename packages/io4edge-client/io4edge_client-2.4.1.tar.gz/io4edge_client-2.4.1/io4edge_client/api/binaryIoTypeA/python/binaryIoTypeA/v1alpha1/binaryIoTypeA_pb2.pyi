from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationSet(_message.Message):
    __slots__ = ("outputFrittingMask", "outputWatchdogMask", "outputWatchdogTimeout")
    OUTPUTFRITTINGMASK_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGMASK_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    outputFrittingMask: int
    outputWatchdogMask: int
    outputWatchdogTimeout: int
    def __init__(self, outputFrittingMask: _Optional[int] = ..., outputWatchdogMask: _Optional[int] = ..., outputWatchdogTimeout: _Optional[int] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("outputFrittingMask", "outputWatchdogMask", "outputWatchdogTimeout")
    OUTPUTFRITTINGMASK_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGMASK_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    outputFrittingMask: int
    outputWatchdogMask: int
    outputWatchdogTimeout: int
    def __init__(self, outputFrittingMask: _Optional[int] = ..., outputWatchdogMask: _Optional[int] = ..., outputWatchdogTimeout: _Optional[int] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("numberOfChannels",)
    NUMBEROFCHANNELS_FIELD_NUMBER: _ClassVar[int]
    numberOfChannels: int
    def __init__(self, numberOfChannels: _Optional[int] = ...) -> None: ...

class SetSingle(_message.Message):
    __slots__ = ("channel", "state")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    state: bool
    def __init__(self, channel: _Optional[int] = ..., state: _Optional[bool] = ...) -> None: ...

class SetAll(_message.Message):
    __slots__ = ("values", "mask")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    MASK_FIELD_NUMBER: _ClassVar[int]
    values: int
    mask: int
    def __init__(self, values: _Optional[int] = ..., mask: _Optional[int] = ...) -> None: ...

class SetExitError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("single", "all", "exit_error")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    EXIT_ERROR_FIELD_NUMBER: _ClassVar[int]
    single: SetSingle
    all: SetAll
    exit_error: SetExitError
    def __init__(self, single: _Optional[_Union[SetSingle, _Mapping]] = ..., all: _Optional[_Union[SetAll, _Mapping]] = ..., exit_error: _Optional[_Union[SetExitError, _Mapping]] = ...) -> None: ...

class GetSingle(_message.Message):
    __slots__ = ("channel",)
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    channel: int
    def __init__(self, channel: _Optional[int] = ...) -> None: ...

class GetAll(_message.Message):
    __slots__ = ("mask",)
    MASK_FIELD_NUMBER: _ClassVar[int]
    mask: int
    def __init__(self, mask: _Optional[int] = ...) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ("single", "all")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    single: GetSingle
    all: GetAll
    def __init__(self, single: _Optional[_Union[GetSingle, _Mapping]] = ..., all: _Optional[_Union[GetAll, _Mapping]] = ...) -> None: ...

class GetAllResponse(_message.Message):
    __slots__ = ("inputs",)
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    inputs: int
    def __init__(self, inputs: _Optional[int] = ...) -> None: ...

class GetSingleResponse(_message.Message):
    __slots__ = ("channel", "state")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    state: bool
    def __init__(self, channel: _Optional[int] = ..., state: _Optional[bool] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("single", "all")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    single: GetSingleResponse
    all: GetAllResponse
    def __init__(self, single: _Optional[_Union[GetSingleResponse, _Mapping]] = ..., all: _Optional[_Union[GetAllResponse, _Mapping]] = ...) -> None: ...

class SetAllResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetSingleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ("single", "all")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    single: SetSingleResponse
    all: SetAllResponse
    def __init__(self, single: _Optional[_Union[SetSingleResponse, _Mapping]] = ..., all: _Optional[_Union[SetAllResponse, _Mapping]] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("channelFilterMask",)
    CHANNELFILTERMASK_FIELD_NUMBER: _ClassVar[int]
    channelFilterMask: int
    def __init__(self, channelFilterMask: _Optional[int] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "channel", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    channel: int
    value: bool
    def __init__(self, timestamp: _Optional[int] = ..., channel: _Optional[int] = ..., value: _Optional[bool] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
