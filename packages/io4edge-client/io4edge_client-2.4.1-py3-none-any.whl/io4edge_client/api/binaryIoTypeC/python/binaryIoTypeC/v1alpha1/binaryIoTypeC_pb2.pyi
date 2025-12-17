from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BINARYIOTYPEC_INPUT_TYPE_1_3: _ClassVar[ChannelMode]
    BINARYIOTYPEC_OUTPUT_PUSH_PULL: _ClassVar[ChannelMode]

class ChannelDiag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NoDiag: _ClassVar[ChannelDiag]
    NoSupplyVoltage: _ClassVar[ChannelDiag]
    CurrentLimit: _ClassVar[ChannelDiag]
    Overload: _ClassVar[ChannelDiag]
    SupplyUndervoltage: _ClassVar[ChannelDiag]
    SupplyOvervoltage: _ClassVar[ChannelDiag]
BINARYIOTYPEC_INPUT_TYPE_1_3: ChannelMode
BINARYIOTYPEC_OUTPUT_PUSH_PULL: ChannelMode
NoDiag: ChannelDiag
NoSupplyVoltage: ChannelDiag
CurrentLimit: ChannelDiag
Overload: ChannelDiag
SupplyUndervoltage: ChannelDiag
SupplyOvervoltage: ChannelDiag

class ChannelConfig(_message.Message):
    __slots__ = ("channel", "mode", "initialValue")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    INITIALVALUE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    mode: ChannelMode
    initialValue: bool
    def __init__(self, channel: _Optional[int] = ..., mode: _Optional[_Union[ChannelMode, str]] = ..., initialValue: _Optional[bool] = ...) -> None: ...

class ConfigurationSet(_message.Message):
    __slots__ = ("channelConfig", "changeOutputWatchdog", "outputWatchdogMask", "outputWatchdogTimeout")
    CHANNELCONFIG_FIELD_NUMBER: _ClassVar[int]
    CHANGEOUTPUTWATCHDOG_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGMASK_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    channelConfig: _containers.RepeatedCompositeFieldContainer[ChannelConfig]
    changeOutputWatchdog: bool
    outputWatchdogMask: int
    outputWatchdogTimeout: int
    def __init__(self, channelConfig: _Optional[_Iterable[_Union[ChannelConfig, _Mapping]]] = ..., changeOutputWatchdog: _Optional[bool] = ..., outputWatchdogMask: _Optional[int] = ..., outputWatchdogTimeout: _Optional[int] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("channelConfig", "outputWatchdogMask", "outputWatchdogTimeout")
    CHANNELCONFIG_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGMASK_FIELD_NUMBER: _ClassVar[int]
    OUTPUTWATCHDOGTIMEOUT_FIELD_NUMBER: _ClassVar[int]
    channelConfig: _containers.RepeatedCompositeFieldContainer[ChannelConfig]
    outputWatchdogMask: int
    outputWatchdogTimeout: int
    def __init__(self, channelConfig: _Optional[_Iterable[_Union[ChannelConfig, _Mapping]]] = ..., outputWatchdogMask: _Optional[int] = ..., outputWatchdogTimeout: _Optional[int] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("numberOfChannels",)
    NUMBEROFCHANNELS_FIELD_NUMBER: _ClassVar[int]
    numberOfChannels: int
    def __init__(self, numberOfChannels: _Optional[int] = ...) -> None: ...

class ConfigurationResponse(_message.Message):
    __slots__ = ("get", "set", "describe")
    GET_FIELD_NUMBER: _ClassVar[int]
    SET_FIELD_NUMBER: _ClassVar[int]
    DESCRIBE_FIELD_NUMBER: _ClassVar[int]
    get: ConfigurationGetResponse
    set: ConfigurationSetResponse
    describe: ConfigurationDescribeResponse
    def __init__(self, get: _Optional[_Union[ConfigurationGetResponse, _Mapping]] = ..., set: _Optional[_Union[ConfigurationSetResponse, _Mapping]] = ..., describe: _Optional[_Union[ConfigurationDescribeResponse, _Mapping]] = ...) -> None: ...

class GetSingle(_message.Message):
    __slots__ = ("channel",)
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    channel: int
    def __init__(self, channel: _Optional[int] = ...) -> None: ...

class GetAll(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ("single", "all")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    single: GetSingle
    all: GetAll
    def __init__(self, single: _Optional[_Union[GetSingle, _Mapping]] = ..., all: _Optional[_Union[GetAll, _Mapping]] = ...) -> None: ...

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

class FunctionControlSet(_message.Message):
    __slots__ = ("single", "all")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    single: SetSingle
    all: SetAll
    def __init__(self, single: _Optional[_Union[SetSingle, _Mapping]] = ..., all: _Optional[_Union[SetAll, _Mapping]] = ...) -> None: ...

class GetSingleResponse(_message.Message):
    __slots__ = ("channel", "state", "diag")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DIAG_FIELD_NUMBER: _ClassVar[int]
    channel: int
    state: bool
    diag: int
    def __init__(self, channel: _Optional[int] = ..., state: _Optional[bool] = ..., diag: _Optional[int] = ...) -> None: ...

class GetAllResponse(_message.Message):
    __slots__ = ("inputs", "diag")
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    DIAG_FIELD_NUMBER: _ClassVar[int]
    inputs: int
    diag: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, inputs: _Optional[int] = ..., diag: _Optional[_Iterable[int]] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("single", "all")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    single: GetSingleResponse
    all: GetAllResponse
    def __init__(self, single: _Optional[_Union[GetSingleResponse, _Mapping]] = ..., all: _Optional[_Union[GetAllResponse, _Mapping]] = ...) -> None: ...

class SetSingleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetAllResponse(_message.Message):
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
    __slots__ = ("timestamp", "values", "value_valid")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    VALUE_VALID_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    values: int
    value_valid: int
    def __init__(self, timestamp: _Optional[int] = ..., values: _Optional[int] = ..., value_valid: _Optional[int] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
