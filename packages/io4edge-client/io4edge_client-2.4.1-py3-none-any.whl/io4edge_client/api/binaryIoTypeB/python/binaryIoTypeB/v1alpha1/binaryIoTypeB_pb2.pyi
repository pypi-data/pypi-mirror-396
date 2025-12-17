from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BINARYIOTYPEB_INPUT: _ClassVar[ChannelDirection]
    BINARYIOTYPEB_OUTPUT: _ClassVar[ChannelDirection]
    BINARYIOTYPEB_INPUT_OUTPUT: _ClassVar[ChannelDirection]

class SubscriptionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BINARYIOTYPEB_ON_RISING_EDGE: _ClassVar[SubscriptionType]
    BINARYIOTYPEB_ON_FALLING_EDGE: _ClassVar[SubscriptionType]
    BINARYIOTYPEB_ON_ANY_EDGE: _ClassVar[SubscriptionType]
BINARYIOTYPEB_INPUT: ChannelDirection
BINARYIOTYPEB_OUTPUT: ChannelDirection
BINARYIOTYPEB_INPUT_OUTPUT: ChannelDirection
BINARYIOTYPEB_ON_RISING_EDGE: SubscriptionType
BINARYIOTYPEB_ON_FALLING_EDGE: SubscriptionType
BINARYIOTYPEB_ON_ANY_EDGE: SubscriptionType

class ConfigurationSet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ChannelConfig(_message.Message):
    __slots__ = ("channel", "direction")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    channel: int
    direction: ChannelDirection
    def __init__(self, channel: _Optional[int] = ..., direction: _Optional[_Union[ChannelDirection, str]] = ...) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("channelConfig",)
    CHANNELCONFIG_FIELD_NUMBER: _ClassVar[int]
    channelConfig: _containers.RepeatedCompositeFieldContainer[ChannelConfig]
    def __init__(self, channelConfig: _Optional[_Iterable[_Union[ChannelConfig, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("channel", "state")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    state: bool
    def __init__(self, channel: _Optional[int] = ..., state: _Optional[bool] = ...) -> None: ...

class GetAllResponse(_message.Message):
    __slots__ = ("inputs",)
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    inputs: int
    def __init__(self, inputs: _Optional[int] = ...) -> None: ...

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

class SubscribeChannel(_message.Message):
    __slots__ = ("channel", "subscriptionType")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTIONTYPE_FIELD_NUMBER: _ClassVar[int]
    channel: int
    subscriptionType: SubscriptionType
    def __init__(self, channel: _Optional[int] = ..., subscriptionType: _Optional[_Union[SubscriptionType, str]] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("subscribeChannel",)
    SUBSCRIBECHANNEL_FIELD_NUMBER: _ClassVar[int]
    subscribeChannel: _containers.RepeatedCompositeFieldContainer[SubscribeChannel]
    def __init__(self, subscribeChannel: _Optional[_Iterable[_Union[SubscribeChannel, _Mapping]]] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "inputs")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    inputs: int
    def __init__(self, timestamp: _Optional[int] = ..., inputs: _Optional[int] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
