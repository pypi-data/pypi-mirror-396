from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.type.v1 import token_pb2 as _token_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Instrument(_message.Message):
    __slots__ = ("name", "owner", "owners", "display_name", "token")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    name: str
    owner: str
    owners: _containers.RepeatedScalarFieldContainer[str]
    display_name: str
    token: _token_pb2.Token
    def __init__(self, name: _Optional[str] = ..., owner: _Optional[str] = ..., owners: _Optional[_Iterable[str]] = ..., display_name: _Optional[str] = ..., token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ...) -> None: ...
