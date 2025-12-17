from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("generator_pattern",)
    GENERATOR_PATTERN_FIELD_NUMBER: _ClassVar[int]
    generator_pattern: str
    def __init__(self, generator_pattern: _Optional[str] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FilterMask(_message.Message):
    __slots__ = ("f_code_mask", "address", "mask", "include_timedout_frames")
    F_CODE_MASK_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MASK_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_TIMEDOUT_FRAMES_FIELD_NUMBER: _ClassVar[int]
    f_code_mask: int
    address: int
    mask: int
    include_timedout_frames: bool
    def __init__(self, f_code_mask: _Optional[int] = ..., address: _Optional[int] = ..., mask: _Optional[int] = ..., include_timedout_frames: _Optional[bool] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: _containers.RepeatedCompositeFieldContainer[FilterMask]
    def __init__(self, filter: _Optional[_Iterable[_Union[FilterMask, _Mapping]]] = ...) -> None: ...
