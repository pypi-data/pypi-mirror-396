from google.protobuf import descriptor_pb2 as _descriptor_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MethodType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METHOD_TYPE_UNSPECIFIED: _ClassVar[MethodType]
    METHOD_TYPE_READ: _ClassVar[MethodType]
    METHOD_TYPE_WRITE: _ClassVar[MethodType]

class MethodAccessLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METHOD_ACCESS_LEVEL_UNSPECIFIED: _ClassVar[MethodAccessLevel]
    METHOD_ACCESS_LEVEL_PUBLIC: _ClassVar[MethodAccessLevel]
    METHOD_ACCESS_LEVEL_AUTHORISED: _ClassVar[MethodAccessLevel]
METHOD_TYPE_UNSPECIFIED: MethodType
METHOD_TYPE_READ: MethodType
METHOD_TYPE_WRITE: MethodType
METHOD_ACCESS_LEVEL_UNSPECIFIED: MethodAccessLevel
METHOD_ACCESS_LEVEL_PUBLIC: MethodAccessLevel
METHOD_ACCESS_LEVEL_AUTHORISED: MethodAccessLevel
METHOD_OPTIONS_FIELD_NUMBER: _ClassVar[int]
method_options: _descriptor.FieldDescriptor

class MethodOptions(_message.Message):
    __slots__ = ("type", "access_level", "roles")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LEVEL_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    type: MethodType
    access_level: MethodAccessLevel
    roles: _containers.RepeatedScalarFieldContainer[_role_pb2.Role]
    def __init__(self, type: _Optional[_Union[MethodType, str]] = ..., access_level: _Optional[_Union[MethodAccessLevel, str]] = ..., roles: _Optional[_Iterable[_Union[_role_pb2.Role, str]]] = ...) -> None: ...
