from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.option.method_options.v1 import method_options_pb2 as _method_options_pb2
from meshtrade.trading.limit_order.v1 import limit_order_pb2 as _limit_order_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateLimitOrderRequest(_message.Message):
    __slots__ = ("limit_order",)
    LIMIT_ORDER_FIELD_NUMBER: _ClassVar[int]
    limit_order: _limit_order_pb2.LimitOrder
    def __init__(self, limit_order: _Optional[_Union[_limit_order_pb2.LimitOrder, _Mapping]] = ...) -> None: ...

class CancelLimitOrderRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetLimitOrderRequest(_message.Message):
    __slots__ = ("name", "live_ledger_data")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LIVE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    live_ledger_data: bool
    def __init__(self, name: _Optional[str] = ..., live_ledger_data: bool = ...) -> None: ...

class GetLimitOrderByExternalReferenceRequest(_message.Message):
    __slots__ = ("external_reference", "live_ledger_data")
    EXTERNAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    LIVE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    external_reference: str
    live_ledger_data: bool
    def __init__(self, external_reference: _Optional[str] = ..., live_ledger_data: bool = ...) -> None: ...

class ListLimitOrdersRequest(_message.Message):
    __slots__ = ("live_ledger_data",)
    LIVE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    live_ledger_data: bool
    def __init__(self, live_ledger_data: bool = ...) -> None: ...

class ListLimitOrdersResponse(_message.Message):
    __slots__ = ("limit_orders",)
    LIMIT_ORDERS_FIELD_NUMBER: _ClassVar[int]
    limit_orders: _containers.RepeatedCompositeFieldContainer[_limit_order_pb2.LimitOrder]
    def __init__(self, limit_orders: _Optional[_Iterable[_Union[_limit_order_pb2.LimitOrder, _Mapping]]] = ...) -> None: ...

class SearchLimitOrdersRequest(_message.Message):
    __slots__ = ("token", "account", "live_ledger_data")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    LIVE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    token: str
    account: str
    live_ledger_data: bool
    def __init__(self, token: _Optional[str] = ..., account: _Optional[str] = ..., live_ledger_data: bool = ...) -> None: ...

class SearchLimitOrdersResponse(_message.Message):
    __slots__ = ("limit_orders",)
    LIMIT_ORDERS_FIELD_NUMBER: _ClassVar[int]
    limit_orders: _containers.RepeatedCompositeFieldContainer[_limit_order_pb2.LimitOrder]
    def __init__(self, limit_orders: _Optional[_Iterable[_Union[_limit_order_pb2.LimitOrder, _Mapping]]] = ...) -> None: ...

class MonitorLimitOrderRequest(_message.Message):
    __slots__ = ("name", "external_reference", "live_ledger_data")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    LIVE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    external_reference: str
    live_ledger_data: bool
    def __init__(self, name: _Optional[str] = ..., external_reference: _Optional[str] = ..., live_ledger_data: bool = ...) -> None: ...
