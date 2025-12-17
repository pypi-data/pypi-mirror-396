from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationSet(_message.Message):
    __slots__ = ("sample_rate_milliHz", "full_scale_g", "high_pass_filter_enable", "band_width_ratio")
    SAMPLE_RATE_MILLIHZ_FIELD_NUMBER: _ClassVar[int]
    FULL_SCALE_G_FIELD_NUMBER: _ClassVar[int]
    HIGH_PASS_FILTER_ENABLE_FIELD_NUMBER: _ClassVar[int]
    BAND_WIDTH_RATIO_FIELD_NUMBER: _ClassVar[int]
    sample_rate_milliHz: int
    full_scale_g: int
    high_pass_filter_enable: bool
    band_width_ratio: int
    def __init__(self, sample_rate_milliHz: _Optional[int] = ..., full_scale_g: _Optional[int] = ..., high_pass_filter_enable: _Optional[bool] = ..., band_width_ratio: _Optional[int] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("sample_rate_millihz", "full_scale_g", "high_pass_filter_enable", "band_width_ratio")
    SAMPLE_RATE_MILLIHZ_FIELD_NUMBER: _ClassVar[int]
    FULL_SCALE_G_FIELD_NUMBER: _ClassVar[int]
    HIGH_PASS_FILTER_ENABLE_FIELD_NUMBER: _ClassVar[int]
    BAND_WIDTH_RATIO_FIELD_NUMBER: _ClassVar[int]
    sample_rate_millihz: int
    full_scale_g: int
    high_pass_filter_enable: bool
    band_width_ratio: int
    def __init__(self, sample_rate_millihz: _Optional[int] = ..., full_scale_g: _Optional[int] = ..., high_pass_filter_enable: _Optional[bool] = ..., band_width_ratio: _Optional[int] = ...) -> None: ...

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
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Sample(_message.Message):
    __slots__ = ("timestamp", "x", "y", "z")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    x: float
    y: float
    z: float
    def __init__(self, timestamp: _Optional[int] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...
