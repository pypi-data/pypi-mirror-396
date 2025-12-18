import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.type.v1 import decimal_pb2 as _decimal_pb2
from meshtrade.type.v1 import token_pb2 as _token_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Price(_message.Message):
    __slots__ = ("base_token", "quote_token", "mid_price", "time")
    BASE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    QUOTE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MID_PRICE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    base_token: _token_pb2.Token
    quote_token: _token_pb2.Token
    mid_price: _decimal_pb2.Decimal
    time: _timestamp_pb2.Timestamp
    def __init__(self, base_token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., quote_token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., mid_price: _Optional[_Union[_decimal_pb2.Decimal, _Mapping]] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
