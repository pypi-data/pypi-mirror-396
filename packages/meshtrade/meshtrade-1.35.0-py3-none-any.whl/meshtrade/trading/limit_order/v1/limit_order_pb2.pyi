import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.type.v1 import amount_pb2 as _amount_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LimitOrderSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIMIT_ORDER_SIDE_UNSPECIFIED: _ClassVar[LimitOrderSide]
    LIMIT_ORDER_SIDE_BUY: _ClassVar[LimitOrderSide]
    LIMIT_ORDER_SIDE_SELL: _ClassVar[LimitOrderSide]

class LimitOrderState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIMIT_ORDER_STATE_UNSPECIFIED: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_SUBMISSION_IN_PROGRESS: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_SUBMISSION_FAILED: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_OPEN: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_COMPLETE_IN_PROGRESS: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_COMPLETE: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_CANCELLATION_IN_PROGRESS: _ClassVar[LimitOrderState]
    LIMIT_ORDER_STATE_CANCELLED: _ClassVar[LimitOrderState]
LIMIT_ORDER_SIDE_UNSPECIFIED: LimitOrderSide
LIMIT_ORDER_SIDE_BUY: LimitOrderSide
LIMIT_ORDER_SIDE_SELL: LimitOrderSide
LIMIT_ORDER_STATE_UNSPECIFIED: LimitOrderState
LIMIT_ORDER_STATE_SUBMISSION_IN_PROGRESS: LimitOrderState
LIMIT_ORDER_STATE_SUBMISSION_FAILED: LimitOrderState
LIMIT_ORDER_STATE_OPEN: LimitOrderState
LIMIT_ORDER_STATE_COMPLETE_IN_PROGRESS: LimitOrderState
LIMIT_ORDER_STATE_COMPLETE: LimitOrderState
LIMIT_ORDER_STATE_CANCELLATION_IN_PROGRESS: LimitOrderState
LIMIT_ORDER_STATE_CANCELLED: LimitOrderState

class LimitOrder(_message.Message):
    __slots__ = ("name", "owner", "owners", "account", "external_reference", "side", "limit_price", "quantity", "fill_price", "filled_quantity", "state", "number", "submitted_at")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    FILL_PRICE_FIELD_NUMBER: _ClassVar[int]
    FILLED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    owner: str
    owners: _containers.RepeatedScalarFieldContainer[str]
    account: str
    external_reference: str
    side: LimitOrderSide
    limit_price: _amount_pb2.Amount
    quantity: _amount_pb2.Amount
    fill_price: _amount_pb2.Amount
    filled_quantity: _amount_pb2.Amount
    state: LimitOrderState
    number: str
    submitted_at: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., owner: _Optional[str] = ..., owners: _Optional[_Iterable[str]] = ..., account: _Optional[str] = ..., external_reference: _Optional[str] = ..., side: _Optional[_Union[LimitOrderSide, str]] = ..., limit_price: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., quantity: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., fill_price: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., filled_quantity: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., state: _Optional[_Union[LimitOrderState, str]] = ..., number: _Optional[str] = ..., submitted_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
