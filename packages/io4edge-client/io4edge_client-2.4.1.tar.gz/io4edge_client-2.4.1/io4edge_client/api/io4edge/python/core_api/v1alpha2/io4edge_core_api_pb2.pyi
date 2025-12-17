from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandId(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDENTIFY_HARDWARE: _ClassVar[CommandId]
    IDENTIFY_FIRMWARE: _ClassVar[CommandId]
    LOAD_FIRMWARE_CHUNK: _ClassVar[CommandId]
    PROGRAM_HARDWARE_IDENTIFICATION: _ClassVar[CommandId]
    RESTART: _ClassVar[CommandId]
    SET_PERSISTENT_PARAMETER: _ClassVar[CommandId]
    GET_PERSISTENT_PARAMETER: _ClassVar[CommandId]
    READ_PARTITION_CHUNK: _ClassVar[CommandId]
    GET_RESET_REASON: _ClassVar[CommandId]

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[Status]
    UNKNOWN_COMMAND: _ClassVar[Status]
    ILLEGAL_PARAMETER: _ClassVar[Status]
    BAD_CHUNK_SEQ: _ClassVar[Status]
    BAD_CHUNK_SIZE: _ClassVar[Status]
    NOT_COMPATIBLE: _ClassVar[Status]
    INTERNAL_ERROR: _ClassVar[Status]
    PROGRAMMING_ERROR: _ClassVar[Status]
    NO_HW_INVENTORY: _ClassVar[Status]
    THIS_VERSION_FAILED_ALREADY: _ClassVar[Status]
IDENTIFY_HARDWARE: CommandId
IDENTIFY_FIRMWARE: CommandId
LOAD_FIRMWARE_CHUNK: CommandId
PROGRAM_HARDWARE_IDENTIFICATION: CommandId
RESTART: CommandId
SET_PERSISTENT_PARAMETER: CommandId
GET_PERSISTENT_PARAMETER: CommandId
READ_PARTITION_CHUNK: CommandId
GET_RESET_REASON: CommandId
OK: Status
UNKNOWN_COMMAND: Status
ILLEGAL_PARAMETER: Status
BAD_CHUNK_SEQ: Status
BAD_CHUNK_SIZE: Status
NOT_COMPATIBLE: Status
INTERNAL_ERROR: Status
PROGRAMMING_ERROR: Status
NO_HW_INVENTORY: Status
THIS_VERSION_FAILED_ALREADY: Status

class LoadFirmwareChunkCommand(_message.Message):
    __slots__ = ("chunk_number", "is_last_chunk", "data")
    CHUNK_NUMBER_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_CHUNK_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    chunk_number: int
    is_last_chunk: bool
    data: bytes
    def __init__(self, chunk_number: _Optional[int] = ..., is_last_chunk: _Optional[bool] = ..., data: _Optional[bytes] = ...) -> None: ...

class ProgramHardwareIdentificationCommand(_message.Message):
    __slots__ = ("signature", "root_article", "major_version", "serial_number")
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ROOT_ARTICLE_FIELD_NUMBER: _ClassVar[int]
    MAJOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    signature: str
    root_article: str
    major_version: int
    serial_number: str
    def __init__(self, signature: _Optional[str] = ..., root_article: _Optional[str] = ..., major_version: _Optional[int] = ..., serial_number: _Optional[str] = ...) -> None: ...

class SetPersistentParameterCommand(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class GetPersistentParameterCommand(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ReadPartitionChunkCommand(_message.Message):
    __slots__ = ("part_name", "offset")
    PART_NAME_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    part_name: str
    offset: int
    def __init__(self, part_name: _Optional[str] = ..., offset: _Optional[int] = ...) -> None: ...

class IdentifyHardwareResponse(_message.Message):
    __slots__ = ("root_article", "major_version", "serial_number")
    ROOT_ARTICLE_FIELD_NUMBER: _ClassVar[int]
    MAJOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    root_article: str
    major_version: int
    serial_number: str
    def __init__(self, root_article: _Optional[str] = ..., major_version: _Optional[int] = ..., serial_number: _Optional[str] = ...) -> None: ...

class IdentifyFirmwareResponse(_message.Message):
    __slots__ = ("name", "version")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class GetPersistentParameterResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ReadPartitionChunkResponse(_message.Message):
    __slots__ = ("part_name", "offset", "data")
    PART_NAME_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    part_name: str
    offset: int
    data: bytes
    def __init__(self, part_name: _Optional[str] = ..., offset: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class GetResetReasonResponse(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class CoreCommand(_message.Message):
    __slots__ = ("id", "load_firmware_chunk", "program_hardware_identification", "set_persistent_parameter", "get_persistent_parameter", "read_partition_chunk")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOAD_FIRMWARE_CHUNK_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_HARDWARE_IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
    SET_PERSISTENT_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    GET_PERSISTENT_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    READ_PARTITION_CHUNK_FIELD_NUMBER: _ClassVar[int]
    id: CommandId
    load_firmware_chunk: LoadFirmwareChunkCommand
    program_hardware_identification: ProgramHardwareIdentificationCommand
    set_persistent_parameter: SetPersistentParameterCommand
    get_persistent_parameter: GetPersistentParameterCommand
    read_partition_chunk: ReadPartitionChunkCommand
    def __init__(self, id: _Optional[_Union[CommandId, str]] = ..., load_firmware_chunk: _Optional[_Union[LoadFirmwareChunkCommand, _Mapping]] = ..., program_hardware_identification: _Optional[_Union[ProgramHardwareIdentificationCommand, _Mapping]] = ..., set_persistent_parameter: _Optional[_Union[SetPersistentParameterCommand, _Mapping]] = ..., get_persistent_parameter: _Optional[_Union[GetPersistentParameterCommand, _Mapping]] = ..., read_partition_chunk: _Optional[_Union[ReadPartitionChunkCommand, _Mapping]] = ...) -> None: ...

class CoreResponse(_message.Message):
    __slots__ = ("id", "status", "restarting_now", "identify_hardware", "identify_firmware", "persistent_parameter", "read_partition_chunk", "reset_reason")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESTARTING_NOW_FIELD_NUMBER: _ClassVar[int]
    IDENTIFY_HARDWARE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFY_FIRMWARE_FIELD_NUMBER: _ClassVar[int]
    PERSISTENT_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    READ_PARTITION_CHUNK_FIELD_NUMBER: _ClassVar[int]
    RESET_REASON_FIELD_NUMBER: _ClassVar[int]
    id: CommandId
    status: Status
    restarting_now: bool
    identify_hardware: IdentifyHardwareResponse
    identify_firmware: IdentifyFirmwareResponse
    persistent_parameter: GetPersistentParameterResponse
    read_partition_chunk: ReadPartitionChunkResponse
    reset_reason: GetResetReasonResponse
    def __init__(self, id: _Optional[_Union[CommandId, str]] = ..., status: _Optional[_Union[Status, str]] = ..., restarting_now: _Optional[bool] = ..., identify_hardware: _Optional[_Union[IdentifyHardwareResponse, _Mapping]] = ..., identify_firmware: _Optional[_Union[IdentifyFirmwareResponse, _Mapping]] = ..., persistent_parameter: _Optional[_Union[GetPersistentParameterResponse, _Mapping]] = ..., read_partition_chunk: _Optional[_Union[ReadPartitionChunkResponse, _Mapping]] = ..., reset_reason: _Optional[_Union[GetResetReasonResponse, _Mapping]] = ...) -> None: ...
