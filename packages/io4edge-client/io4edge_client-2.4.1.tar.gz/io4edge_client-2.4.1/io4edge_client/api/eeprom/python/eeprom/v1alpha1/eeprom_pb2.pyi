from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationSet(_message.Message):
    __slots__ = ("eeprom_size", "block_size")
    EEPROM_SIZE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_SIZE_FIELD_NUMBER: _ClassVar[int]
    eeprom_size: int
    block_size: int
    def __init__(self, eeprom_size: _Optional[int] = ..., block_size: _Optional[int] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("eeprom_size", "block_size")
    EEPROM_SIZE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_SIZE_FIELD_NUMBER: _ClassVar[int]
    eeprom_size: int
    block_size: int
    def __init__(self, eeprom_size: _Optional[int] = ..., block_size: _Optional[int] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("ident", "capacity", "operations")
    IDENT_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    ident: str
    capacity: str
    operations: str
    def __init__(self, ident: _Optional[str] = ..., capacity: _Optional[str] = ..., operations: _Optional[str] = ...) -> None: ...

class ConfigurationResponse(_message.Message):
    __slots__ = ("get", "set", "describe")
    GET_FIELD_NUMBER: _ClassVar[int]
    SET_FIELD_NUMBER: _ClassVar[int]
    DESCRIBE_FIELD_NUMBER: _ClassVar[int]
    get: ConfigurationGetResponse
    set: ConfigurationSetResponse
    describe: ConfigurationDescribeResponse
    def __init__(self, get: _Optional[_Union[ConfigurationGetResponse, _Mapping]] = ..., set: _Optional[_Union[ConfigurationSetResponse, _Mapping]] = ..., describe: _Optional[_Union[ConfigurationDescribeResponse, _Mapping]] = ...) -> None: ...

class EepromReadRequest(_message.Message):
    __slots__ = ("address", "length")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    address: int
    length: int
    def __init__(self, address: _Optional[int] = ..., length: _Optional[int] = ...) -> None: ...

class EepromWriteRequest(_message.Message):
    __slots__ = ("address", "data")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    address: int
    data: bytes
    def __init__(self, address: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ("read", "status")
    READ_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    read: EepromReadRequest
    status: bool
    def __init__(self, read: _Optional[_Union[EepromReadRequest, _Mapping]] = ..., status: _Optional[bool] = ...) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("write", "erase")
    WRITE_FIELD_NUMBER: _ClassVar[int]
    ERASE_FIELD_NUMBER: _ClassVar[int]
    write: EepromWriteRequest
    erase: bool
    def __init__(self, write: _Optional[_Union[EepromWriteRequest, _Mapping]] = ..., erase: _Optional[bool] = ...) -> None: ...

class EepromReadResponse(_message.Message):
    __slots__ = ("address", "data", "bytes_read")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    BYTES_READ_FIELD_NUMBER: _ClassVar[int]
    address: int
    data: bytes
    bytes_read: int
    def __init__(self, address: _Optional[int] = ..., data: _Optional[bytes] = ..., bytes_read: _Optional[int] = ...) -> None: ...

class EepromWriteResponse(_message.Message):
    __slots__ = ("address", "bytes_written")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BYTES_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    address: int
    bytes_written: int
    def __init__(self, address: _Optional[int] = ..., bytes_written: _Optional[int] = ...) -> None: ...

class EepromStatusResponse(_message.Message):
    __slots__ = ("total_size", "available_bytes", "write_protected", "last_operation_success", "error_code")
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_BYTES_FIELD_NUMBER: _ClassVar[int]
    WRITE_PROTECTED_FIELD_NUMBER: _ClassVar[int]
    LAST_OPERATION_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    total_size: int
    available_bytes: int
    write_protected: bool
    last_operation_success: bool
    error_code: int
    def __init__(self, total_size: _Optional[int] = ..., available_bytes: _Optional[int] = ..., write_protected: _Optional[bool] = ..., last_operation_success: _Optional[bool] = ..., error_code: _Optional[int] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("read_response", "status_response")
    READ_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    STATUS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    read_response: EepromReadResponse
    status_response: EepromStatusResponse
    def __init__(self, read_response: _Optional[_Union[EepromReadResponse, _Mapping]] = ..., status_response: _Optional[_Union[EepromStatusResponse, _Mapping]] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ("write_response", "erase_completed")
    WRITE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERASE_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    write_response: EepromWriteResponse
    erase_completed: bool
    def __init__(self, write_response: _Optional[_Union[EepromWriteResponse, _Mapping]] = ..., erase_completed: _Optional[bool] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ("monitor_access", "sample_interval_ms")
    MONITOR_ACCESS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    monitor_access: bool
    sample_interval_ms: int
    def __init__(self, monitor_access: _Optional[bool] = ..., sample_interval_ms: _Optional[int] = ...) -> None: ...

class EepromAccessEvent(_message.Message):
    __slots__ = ("timestamp", "access_type", "address", "byte_count", "success")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BYTE_COUNT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    access_type: int
    address: int
    byte_count: int
    success: bool
    def __init__(self, timestamp: _Optional[int] = ..., access_type: _Optional[int] = ..., address: _Optional[int] = ..., byte_count: _Optional[int] = ..., success: _Optional[bool] = ...) -> None: ...

class StreamData(_message.Message):
    __slots__ = ("access_events",)
    ACCESS_EVENTS_FIELD_NUMBER: _ClassVar[int]
    access_events: _containers.RepeatedCompositeFieldContainer[EepromAccessEvent]
    def __init__(self, access_events: _Optional[_Iterable[_Union[EepromAccessEvent, _Mapping]]] = ...) -> None: ...
