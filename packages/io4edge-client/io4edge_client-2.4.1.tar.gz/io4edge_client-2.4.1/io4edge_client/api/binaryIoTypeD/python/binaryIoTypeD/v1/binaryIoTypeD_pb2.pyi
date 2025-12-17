from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BINARYIOTYPED_INPUT_HIGH_ACTIVE: _ClassVar[ChannelMode]
    BINARYIOTYPED_INPUT_LOW_ACTIVE: _ClassVar[ChannelMode]
    BINARYIOTYPED_OUTPUT_HIGH_ACTIVE: _ClassVar[ChannelMode]
    BINARYIOTYPED_OUTPUT_LOW_ACTIVE: _ClassVar[ChannelMode]

class ChannelDiag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NoDiag: _ClassVar[ChannelDiag]
    NoSupplyVoltage: _ClassVar[ChannelDiag]
    Overload: _ClassVar[ChannelDiag]
BINARYIOTYPED_INPUT_HIGH_ACTIVE: ChannelMode
BINARYIOTYPED_INPUT_LOW_ACTIVE: ChannelMode
BINARYIOTYPED_OUTPUT_HIGH_ACTIVE: ChannelMode
BINARYIOTYPED_OUTPUT_LOW_ACTIVE: ChannelMode
NoDiag: ChannelDiag
NoSupplyVoltage: ChannelDiag
Overload: ChannelDiag

class ChannelConfig(_message.Message):
    __slots__ = ("channel", "mode", "initialValue", "overloadRecoveryTimeoutMs", "watchdogTimeoutMs", "frittingEnable")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    INITIALVALUE_FIELD_NUMBER: _ClassVar[int]
    OVERLOADRECOVERYTIMEOUTMS_FIELD_NUMBER: _ClassVar[int]
    WATCHDOGTIMEOUTMS_FIELD_NUMBER: _ClassVar[int]
    FRITTINGENABLE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    mode: ChannelMode
    initialValue: bool
    overloadRecoveryTimeoutMs: int
    watchdogTimeoutMs: int
    frittingEnable: bool
    def __init__(self, channel: _Optional[int] = ..., mode: _Optional[_Union[ChannelMode, str]] = ..., initialValue: _Optional[bool] = ..., overloadRecoveryTimeoutMs: _Optional[int] = ..., watchdogTimeoutMs: _Optional[int] = ..., frittingEnable: _Optional[bool] = ...) -> None: ...

class ConfigurationSet(_message.Message):
    __slots__ = ("channelConfig",)
    CHANNELCONFIG_FIELD_NUMBER: _ClassVar[int]
    channelConfig: _containers.RepeatedCompositeFieldContainer[ChannelConfig]
    def __init__(self, channelConfig: _Optional[_Iterable[_Union[ChannelConfig, _Mapping]]] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("channelConfig",)
    CHANNELCONFIG_FIELD_NUMBER: _ClassVar[int]
    channelConfig: _containers.RepeatedCompositeFieldContainer[ChannelConfig]
    def __init__(self, channelConfig: _Optional[_Iterable[_Union[ChannelConfig, _Mapping]]] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("numberOfChannels",)
    NUMBEROFCHANNELS_FIELD_NUMBER: _ClassVar[int]
    numberOfChannels: int
    def __init__(self, numberOfChannels: _Optional[int] = ...) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

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

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("inputs", "diag")
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    DIAG_FIELD_NUMBER: _ClassVar[int]
    inputs: int
    diag: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, inputs: _Optional[int] = ..., diag: _Optional[_Iterable[int]] = ...) -> None: ...

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
    __slots__ = ()
    def __init__(self) -> None: ...

class Sample(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamData(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
