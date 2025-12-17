from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChannelConfig(_message.Message):
    __slots__ = ("channel", "sample_rate", "gain")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    GAIN_FIELD_NUMBER: _ClassVar[int]
    channel: int
    sample_rate: float
    gain: int
    def __init__(self, channel: _Optional[int] = ..., sample_rate: _Optional[float] = ..., gain: _Optional[int] = ...) -> None: ...

class ChannelGroupSpecification(_message.Message):
    __slots__ = ("channels", "supported_sample_rates", "supported_gains")
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_SAMPLE_RATES_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_GAINS_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedScalarFieldContainer[int]
    supported_sample_rates: _containers.RepeatedScalarFieldContainer[float]
    supported_gains: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, channels: _Optional[_Iterable[int]] = ..., supported_sample_rates: _Optional[_Iterable[float]] = ..., supported_gains: _Optional[_Iterable[int]] = ...) -> None: ...

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
    __slots__ = ("channelSpecification",)
    CHANNELSPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    channelSpecification: _containers.RepeatedCompositeFieldContainer[ChannelGroupSpecification]
    def __init__(self, channelSpecification: _Optional[_Iterable[_Union[ChannelGroupSpecification, _Mapping]]] = ...) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, value: _Optional[_Iterable[float]] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("channelMask",)
    CHANNELMASK_FIELD_NUMBER: _ClassVar[int]
    channelMask: int
    def __init__(self, channelMask: _Optional[int] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "baseChannel", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    BASECHANNEL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    baseChannel: int
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, timestamp: _Optional[int] = ..., baseChannel: _Optional[int] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
