from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Color(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RED: _ClassVar[Color]
    GREEN: _ClassVar[Color]
    BLUE: _ClassVar[Color]
    WHITE: _ClassVar[Color]
    YELLOW: _ClassVar[Color]
    CYAN: _ClassVar[Color]
    PURPLE: _ClassVar[Color]
    OFF: _ClassVar[Color]
RED: Color
GREEN: Color
BLUE: Color
WHITE: Color
YELLOW: Color
CYAN: Color
PURPLE: Color
OFF: Color

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
    __slots__ = ("channel", "color", "blink")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    BLINK_FIELD_NUMBER: _ClassVar[int]
    channel: int
    color: Color
    blink: bool
    def __init__(self, channel: _Optional[int] = ..., color: _Optional[_Union[Color, str]] = ..., blink: _Optional[bool] = ...) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("channelConfig", "maxChannels")
    CHANNELCONFIG_FIELD_NUMBER: _ClassVar[int]
    MAXCHANNELS_FIELD_NUMBER: _ClassVar[int]
    channelConfig: _containers.RepeatedCompositeFieldContainer[ChannelConfig]
    maxChannels: int
    def __init__(self, channelConfig: _Optional[_Iterable[_Union[ChannelConfig, _Mapping]]] = ..., maxChannels: _Optional[int] = ...) -> None: ...

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
    __slots__ = ("channel",)
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    channel: int
    def __init__(self, channel: _Optional[int] = ...) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("channel", "color", "blink")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    BLINK_FIELD_NUMBER: _ClassVar[int]
    channel: int
    color: Color
    blink: bool
    def __init__(self, channel: _Optional[int] = ..., color: _Optional[_Union[Color, str]] = ..., blink: _Optional[bool] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("color", "blink")
    COLOR_FIELD_NUMBER: _ClassVar[int]
    BLINK_FIELD_NUMBER: _ClassVar[int]
    color: Color
    blink: bool
    def __init__(self, color: _Optional[_Union[Color, str]] = ..., blink: _Optional[bool] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamData(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
