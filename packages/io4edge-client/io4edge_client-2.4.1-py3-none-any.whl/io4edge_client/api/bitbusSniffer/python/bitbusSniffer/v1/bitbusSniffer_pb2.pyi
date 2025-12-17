from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationSet(_message.Message):
    __slots__ = ("ignore_crc", "baud_62500", "address_filter")
    IGNORE_CRC_FIELD_NUMBER: _ClassVar[int]
    BAUD_62500_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FILTER_FIELD_NUMBER: _ClassVar[int]
    ignore_crc: bool
    baud_62500: bool
    address_filter: bytes
    def __init__(self, ignore_crc: _Optional[bool] = ..., baud_62500: _Optional[bool] = ..., address_filter: _Optional[bytes] = ...) -> None: ...

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

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Frame(_message.Message):
    __slots__ = ("bitbus_frame",)
    BITBUS_FRAME_FIELD_NUMBER: _ClassVar[int]
    bitbus_frame: bytes
    def __init__(self, bitbus_frame: _Optional[bytes] = ...) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("frames",)
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    frames: _containers.RepeatedCompositeFieldContainer[Frame]
    def __init__(self, frames: _Optional[_Iterable[_Union[Frame, _Mapping]]] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "flags", "bitbus_frame")
    class Flags(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        none: _ClassVar[Sample.Flags]
        bad_crc: _ClassVar[Sample.Flags]
        frames_lost: _ClassVar[Sample.Flags]
        buf_overrun: _ClassVar[Sample.Flags]
    none: Sample.Flags
    bad_crc: Sample.Flags
    frames_lost: Sample.Flags
    buf_overrun: Sample.Flags
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    BITBUS_FRAME_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    flags: int
    bitbus_frame: bytes
    def __init__(self, timestamp: _Optional[int] = ..., flags: _Optional[int] = ..., bitbus_frame: _Optional[bytes] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
