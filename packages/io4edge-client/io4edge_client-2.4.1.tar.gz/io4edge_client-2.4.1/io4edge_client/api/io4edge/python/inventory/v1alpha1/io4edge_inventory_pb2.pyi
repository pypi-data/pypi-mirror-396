from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Unit(_message.Message):
    __slots__ = ("root_article", "major_version", "serial")
    ROOT_ARTICLE_FIELD_NUMBER: _ClassVar[int]
    MAJOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERIAL_FIELD_NUMBER: _ClassVar[int]
    root_article: str
    major_version: int
    serial: str
    def __init__(self, root_article: _Optional[str] = ..., major_version: _Optional[int] = ..., serial: _Optional[str] = ...) -> None: ...
