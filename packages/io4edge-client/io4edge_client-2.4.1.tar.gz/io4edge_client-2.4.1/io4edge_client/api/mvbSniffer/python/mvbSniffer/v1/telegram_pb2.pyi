from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Telegram(_message.Message):
    __slots__ = ("timestamp", "state", "type", "address", "data", "telegram_nr", "line")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        kSuccessful: _ClassVar[Telegram.State]
        kTimedOut: _ClassVar[Telegram.State]
        kMissedMVBFrames: _ClassVar[Telegram.State]
        kMissedTelegrams: _ClassVar[Telegram.State]
    kSuccessful: Telegram.State
    kTimedOut: Telegram.State
    kMissedMVBFrames: Telegram.State
    kMissedTelegrams: Telegram.State
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        kProcessData16Bit: _ClassVar[Telegram.Type]
        kProcessData32Bit: _ClassVar[Telegram.Type]
        kProcessData64Bit: _ClassVar[Telegram.Type]
        kProcessData128Bit: _ClassVar[Telegram.Type]
        kProcessData256Bit: _ClassVar[Telegram.Type]
        kReserved_1: _ClassVar[Telegram.Type]
        kReserved_2: _ClassVar[Telegram.Type]
        kReserved_3: _ClassVar[Telegram.Type]
        kMastershipTransfer: _ClassVar[Telegram.Type]
        kGeneralEvent: _ClassVar[Telegram.Type]
        kReserved_4: _ClassVar[Telegram.Type]
        kReserved_5: _ClassVar[Telegram.Type]
        kMessageData: _ClassVar[Telegram.Type]
        kGroupEvent: _ClassVar[Telegram.Type]
        kSingleEvent: _ClassVar[Telegram.Type]
        kDeviceStatus: _ClassVar[Telegram.Type]
    kProcessData16Bit: Telegram.Type
    kProcessData32Bit: Telegram.Type
    kProcessData64Bit: Telegram.Type
    kProcessData128Bit: Telegram.Type
    kProcessData256Bit: Telegram.Type
    kReserved_1: Telegram.Type
    kReserved_2: Telegram.Type
    kReserved_3: Telegram.Type
    kMastershipTransfer: Telegram.Type
    kGeneralEvent: Telegram.Type
    kReserved_4: Telegram.Type
    kReserved_5: Telegram.Type
    kMessageData: Telegram.Type
    kGroupEvent: Telegram.Type
    kSingleEvent: Telegram.Type
    kDeviceStatus: Telegram.Type
    class Line(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        kA: _ClassVar[Telegram.Line]
        kB: _ClassVar[Telegram.Line]
    kA: Telegram.Line
    kB: Telegram.Line
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_NR_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    state: int
    type: Telegram.Type
    address: int
    data: bytes
    telegram_nr: int
    line: Telegram.Line
    def __init__(self, timestamp: _Optional[int] = ..., state: _Optional[int] = ..., type: _Optional[_Union[Telegram.Type, str]] = ..., address: _Optional[int] = ..., data: _Optional[bytes] = ..., telegram_nr: _Optional[int] = ..., line: _Optional[_Union[Telegram.Line, str]] = ...) -> None: ...

class TelegramCollection(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: _containers.RepeatedCompositeFieldContainer[Telegram]
    def __init__(self, entry: _Optional[_Iterable[_Union[Telegram, _Mapping]]] = ...) -> None: ...
