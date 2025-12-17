from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
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
    __slots__ = ("height_pixel", "width_pixel", "max_num_of_pixel")
    HEIGHT_PIXEL_FIELD_NUMBER: _ClassVar[int]
    WIDTH_PIXEL_FIELD_NUMBER: _ClassVar[int]
    MAX_NUM_OF_PIXEL_FIELD_NUMBER: _ClassVar[int]
    height_pixel: int
    width_pixel: int
    max_num_of_pixel: int
    def __init__(self, height_pixel: _Optional[int] = ..., width_pixel: _Optional[int] = ..., max_num_of_pixel: _Optional[int] = ...) -> None: ...

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
    __slots__ = ()
    def __init__(self) -> None: ...

class SetPixelArea(_message.Message):
    __slots__ = ("start_x", "start_y", "end_x", "image")
    START_X_FIELD_NUMBER: _ClassVar[int]
    START_Y_FIELD_NUMBER: _ClassVar[int]
    END_X_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    start_x: int
    start_y: int
    end_x: int
    image: bytes
    def __init__(self, start_x: _Optional[int] = ..., start_y: _Optional[int] = ..., end_x: _Optional[int] = ..., image: _Optional[bytes] = ...) -> None: ...

class SetDisplayOn(_message.Message):
    __slots__ = ("on",)
    ON_FIELD_NUMBER: _ClassVar[int]
    on: bool
    def __init__(self, on: _Optional[bool] = ...) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("set_pixel_area", "display_on")
    SET_PIXEL_AREA_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_ON_FIELD_NUMBER: _ClassVar[int]
    set_pixel_area: SetPixelArea
    display_on: SetDisplayOn
    def __init__(self, set_pixel_area: _Optional[_Union[SetPixelArea, _Mapping]] = ..., display_on: _Optional[_Union[SetDisplayOn, _Mapping]] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetPixelAreaResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetDisplayOnResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ("set_pixel_area", "display_on")
    SET_PIXEL_AREA_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_ON_FIELD_NUMBER: _ClassVar[int]
    set_pixel_area: SetPixelAreaResponse
    display_on: SetDisplayOnResponse
    def __init__(self, set_pixel_area: _Optional[_Union[SetPixelAreaResponse, _Mapping]] = ..., display_on: _Optional[_Union[SetDisplayOnResponse, _Mapping]] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamData(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
