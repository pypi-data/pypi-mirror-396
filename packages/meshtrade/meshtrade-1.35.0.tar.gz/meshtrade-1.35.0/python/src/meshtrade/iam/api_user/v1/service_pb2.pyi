from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.iam.api_user.v1 import api_user_pb2 as _api_user_pb2
from meshtrade.option.method_options.v1 import method_options_pb2 as _method_options_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAPIUserRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetAPIUserByKeyHashRequest(_message.Message):
    __slots__ = ("key_hash",)
    KEY_HASH_FIELD_NUMBER: _ClassVar[int]
    key_hash: str
    def __init__(self, key_hash: _Optional[str] = ...) -> None: ...

class CreateAPIUserRequest(_message.Message):
    __slots__ = ("api_user",)
    API_USER_FIELD_NUMBER: _ClassVar[int]
    api_user: _api_user_pb2.APIUser
    def __init__(self, api_user: _Optional[_Union[_api_user_pb2.APIUser, _Mapping]] = ...) -> None: ...

class AssignRolesToAPIUserRequest(_message.Message):
    __slots__ = ("name", "roles")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    name: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...

class RevokeRolesFromAPIUserRequest(_message.Message):
    __slots__ = ("name", "roles")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    name: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...

class ListAPIUsersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListAPIUsersResponse(_message.Message):
    __slots__ = ("api_users",)
    API_USERS_FIELD_NUMBER: _ClassVar[int]
    api_users: _containers.RepeatedCompositeFieldContainer[_api_user_pb2.APIUser]
    def __init__(self, api_users: _Optional[_Iterable[_Union[_api_user_pb2.APIUser, _Mapping]]] = ...) -> None: ...

class SearchAPIUsersRequest(_message.Message):
    __slots__ = ("display_name",)
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    display_name: str
    def __init__(self, display_name: _Optional[str] = ...) -> None: ...

class SearchAPIUsersResponse(_message.Message):
    __slots__ = ("api_users",)
    API_USERS_FIELD_NUMBER: _ClassVar[int]
    api_users: _containers.RepeatedCompositeFieldContainer[_api_user_pb2.APIUser]
    def __init__(self, api_users: _Optional[_Iterable[_Union[_api_user_pb2.APIUser, _Mapping]]] = ...) -> None: ...

class ActivateAPIUserRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeactivateAPIUserRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...
