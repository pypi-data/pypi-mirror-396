from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.market_data.price.v1 import price_pb2 as _price_pb2
from meshtrade.option.method_options.v1 import method_options_pb2 as _method_options_pb2
from meshtrade.type.v1 import token_pb2 as _token_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCurrentPriceByTokenPairRequest(_message.Message):
    __slots__ = ("base_token", "quote_token")
    BASE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    QUOTE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    base_token: _token_pb2.Token
    quote_token: _token_pb2.Token
    def __init__(self, base_token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., quote_token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ...) -> None: ...
