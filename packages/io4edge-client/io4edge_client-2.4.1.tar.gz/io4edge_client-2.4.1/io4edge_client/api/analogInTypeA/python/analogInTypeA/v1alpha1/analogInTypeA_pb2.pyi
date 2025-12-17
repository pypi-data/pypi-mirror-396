from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationSet(_message.Message):
    __slots__ = ("sample_rate",)
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    sample_rate: int
    def __init__(self, sample_rate: _Optional[int] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("sample_rate",)
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    sample_rate: int
    def __init__(self, sample_rate: _Optional[int] = ...) -> None: ...

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
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    value: float
    def __init__(self, timestamp: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
