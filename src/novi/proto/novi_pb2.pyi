from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SESSION_AUTO: _ClassVar[SessionMode]
    SESSION_READ_ONLY: _ClassVar[SessionMode]
    SESSION_READ_WRITE: _ClassVar[SessionMode]
    SESSION_IMMEDIATE: _ClassVar[SessionMode]

class ObjectLock(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOCK_NONE: _ClassVar[ObjectLock]
    LOCK_SHARE: _ClassVar[ObjectLock]
    LOCK_EXCLUSIVE: _ClassVar[ObjectLock]

class EventKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_CREATE: _ClassVar[EventKind]
    EVENT_UPDATE: _ClassVar[EventKind]
    EVENT_DELETE: _ClassVar[EventKind]
SESSION_AUTO: SessionMode
SESSION_READ_ONLY: SessionMode
SESSION_READ_WRITE: SessionMode
SESSION_IMMEDIATE: SessionMode
LOCK_NONE: ObjectLock
LOCK_SHARE: ObjectLock
LOCK_EXCLUSIVE: ObjectLock
EVENT_CREATE: EventKind
EVENT_UPDATE: EventKind
EVENT_DELETE: EventKind

class Error(_message.Message):
    __slots__ = ("kind", "message", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KIND_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    kind: str
    message: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, kind: _Optional[str] = ..., message: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UUID(_message.Message):
    __slots__ = ("hi", "lo")
    HI_FIELD_NUMBER: _ClassVar[int]
    LO_FIELD_NUMBER: _ClassVar[int]
    hi: int
    lo: int
    def __init__(self, hi: _Optional[int] = ..., lo: _Optional[int] = ...) -> None: ...

class TagValue(_message.Message):
    __slots__ = ("value", "updated")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    value: str
    updated: int
    def __init__(self, value: _Optional[str] = ..., updated: _Optional[int] = ...) -> None: ...

class Tags(_message.Message):
    __slots__ = ("properties", "tags")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    properties: _containers.ScalarMap[str, str]
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, properties: _Optional[_Mapping[str, str]] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class Object(_message.Message):
    __slots__ = ("id", "tags", "creator", "updated", "created")
    class TagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TagValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TagValue, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: UUID
    tags: _containers.MessageMap[str, TagValue]
    creator: UUID
    updated: int
    created: int
    def __init__(self, id: _Optional[_Union[UUID, _Mapping]] = ..., tags: _Optional[_Mapping[str, TagValue]] = ..., creator: _Optional[_Union[UUID, _Mapping]] = ..., updated: _Optional[int] = ..., created: _Optional[int] = ...) -> None: ...

class Scopes(_message.Message):
    __slots__ = ("scopes",)
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    scopes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, scopes: _Optional[_Iterable[str]] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginReply(_message.Message):
    __slots__ = ("identity",)
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    identity: str
    def __init__(self, identity: _Optional[str] = ...) -> None: ...

class LoginAsRequest(_message.Message):
    __slots__ = ("user", "temporary")
    USER_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_FIELD_NUMBER: _ClassVar[int]
    user: UUID
    temporary: bool
    def __init__(self, user: _Optional[_Union[UUID, _Mapping]] = ..., temporary: bool = ...) -> None: ...

class LoginAsReply(_message.Message):
    __slots__ = ("identity",)
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    identity: str
    def __init__(self, identity: _Optional[str] = ...) -> None: ...

class UseMasterKeyRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class UseMasterKeyReply(_message.Message):
    __slots__ = ("identity",)
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    identity: str
    def __init__(self, identity: _Optional[str] = ...) -> None: ...

class NewSessionRequest(_message.Message):
    __slots__ = ("mode",)
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: SessionMode
    def __init__(self, mode: _Optional[_Union[SessionMode, str]] = ...) -> None: ...

class NewSessionReply(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class EndSessionRequest(_message.Message):
    __slots__ = ("commit",)
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    commit: bool
    def __init__(self, commit: bool = ...) -> None: ...

class EndSessionReply(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateObjectRequest(_message.Message):
    __slots__ = ("tags",)
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tags: Tags
    def __init__(self, tags: _Optional[_Union[Tags, _Mapping]] = ...) -> None: ...

class CreateObjectReply(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class GetObjectRequest(_message.Message):
    __slots__ = ("id", "lock", "precondition")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCK_FIELD_NUMBER: _ClassVar[int]
    PRECONDITION_FIELD_NUMBER: _ClassVar[int]
    id: UUID
    lock: ObjectLock
    precondition: str
    def __init__(self, id: _Optional[_Union[UUID, _Mapping]] = ..., lock: _Optional[_Union[ObjectLock, str]] = ..., precondition: _Optional[str] = ...) -> None: ...

class GetObjectReply(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class UpdateObjectRequest(_message.Message):
    __slots__ = ("id", "tags", "force")
    ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    id: UUID
    tags: Tags
    force: bool
    def __init__(self, id: _Optional[_Union[UUID, _Mapping]] = ..., tags: _Optional[_Union[Tags, _Mapping]] = ..., force: bool = ...) -> None: ...

class UpdateObjectReply(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class ReplaceObjectRequest(_message.Message):
    __slots__ = ("id", "tags", "scopes", "force")
    ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    id: UUID
    tags: Tags
    scopes: Scopes
    force: bool
    def __init__(self, id: _Optional[_Union[UUID, _Mapping]] = ..., tags: _Optional[_Union[Tags, _Mapping]] = ..., scopes: _Optional[_Union[Scopes, _Mapping]] = ..., force: bool = ...) -> None: ...

class ReplaceObjectReply(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class DeleteObjectTagsRequest(_message.Message):
    __slots__ = ("id", "tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    id: UUID
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[_Union[UUID, _Mapping]] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteObjectTagsReply(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class DeleteObjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: UUID
    def __init__(self, id: _Optional[_Union[UUID, _Mapping]] = ...) -> None: ...

class DeleteObjectReply(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ("filter", "checkpoint", "updated_after", "updated_before", "created_after", "created_before", "order", "limit", "lock")
    class Order(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CREATED_DESC: _ClassVar[QueryRequest.Order]
        CREATED_ASC: _ClassVar[QueryRequest.Order]
        UPDATED_DESC: _ClassVar[QueryRequest.Order]
        UPDATED_ASC: _ClassVar[QueryRequest.Order]
    CREATED_DESC: QueryRequest.Order
    CREATED_ASC: QueryRequest.Order
    UPDATED_DESC: QueryRequest.Order
    UPDATED_ASC: QueryRequest.Order
    FILTER_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AFTER_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
    CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    LOCK_FIELD_NUMBER: _ClassVar[int]
    filter: str
    checkpoint: int
    updated_after: int
    updated_before: int
    created_after: int
    created_before: int
    order: QueryRequest.Order
    limit: int
    lock: ObjectLock
    def __init__(self, filter: _Optional[str] = ..., checkpoint: _Optional[int] = ..., updated_after: _Optional[int] = ..., updated_before: _Optional[int] = ..., created_after: _Optional[int] = ..., created_before: _Optional[int] = ..., order: _Optional[_Union[QueryRequest.Order, str]] = ..., limit: _Optional[int] = ..., lock: _Optional[_Union[ObjectLock, str]] = ...) -> None: ...

class QueryReply(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("filter", "checkpoint", "accept_kinds")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_KINDS_FIELD_NUMBER: _ClassVar[int]
    filter: str
    checkpoint: int
    accept_kinds: _containers.RepeatedScalarFieldContainer[EventKind]
    def __init__(self, filter: _Optional[str] = ..., checkpoint: _Optional[int] = ..., accept_kinds: _Optional[_Iterable[_Union[EventKind, str]]] = ...) -> None: ...

class SubscribeReply(_message.Message):
    __slots__ = ("object", "kind")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    object: Object
    kind: EventKind
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ..., kind: _Optional[_Union[EventKind, str]] = ...) -> None: ...

class ObjectEdits(_message.Message):
    __slots__ = ("deletes", "update", "clear")
    DELETES_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    CLEAR_FIELD_NUMBER: _ClassVar[int]
    deletes: _containers.RepeatedScalarFieldContainer[str]
    update: Tags
    clear: bool
    def __init__(self, deletes: _Optional[_Iterable[str]] = ..., update: _Optional[_Union[Tags, _Mapping]] = ..., clear: bool = ...) -> None: ...

class RegCoreHookRequest(_message.Message):
    __slots__ = ("initiate", "result")
    class HookPoint(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BEFORE_CREATE: _ClassVar[RegCoreHookRequest.HookPoint]
        AFTER_CREATE: _ClassVar[RegCoreHookRequest.HookPoint]
        BEFORE_UPDATE: _ClassVar[RegCoreHookRequest.HookPoint]
        AFTER_UPDATE: _ClassVar[RegCoreHookRequest.HookPoint]
        BEFORE_DELETE: _ClassVar[RegCoreHookRequest.HookPoint]
        AFTER_DELETE: _ClassVar[RegCoreHookRequest.HookPoint]
        BEFORE_VIEW: _ClassVar[RegCoreHookRequest.HookPoint]
    BEFORE_CREATE: RegCoreHookRequest.HookPoint
    AFTER_CREATE: RegCoreHookRequest.HookPoint
    BEFORE_UPDATE: RegCoreHookRequest.HookPoint
    AFTER_UPDATE: RegCoreHookRequest.HookPoint
    BEFORE_DELETE: RegCoreHookRequest.HookPoint
    AFTER_DELETE: RegCoreHookRequest.HookPoint
    BEFORE_VIEW: RegCoreHookRequest.HookPoint
    class Initiate(_message.Message):
        __slots__ = ("point", "filter")
        POINT_FIELD_NUMBER: _ClassVar[int]
        FILTER_FIELD_NUMBER: _ClassVar[int]
        point: RegCoreHookRequest.HookPoint
        filter: str
        def __init__(self, point: _Optional[_Union[RegCoreHookRequest.HookPoint, str]] = ..., filter: _Optional[str] = ...) -> None: ...
    class CallResult(_message.Message):
        __slots__ = ("call_id", "response", "error")
        CALL_ID_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        call_id: int
        response: ObjectEdits
        error: Error
        def __init__(self, call_id: _Optional[int] = ..., response: _Optional[_Union[ObjectEdits, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...
    INITIATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    initiate: RegCoreHookRequest.Initiate
    result: RegCoreHookRequest.CallResult
    def __init__(self, initiate: _Optional[_Union[RegCoreHookRequest.Initiate, _Mapping]] = ..., result: _Optional[_Union[RegCoreHookRequest.CallResult, _Mapping]] = ...) -> None: ...

class RegCoreHookReply(_message.Message):
    __slots__ = ("call_id", "object", "old_object", "session", "identity")
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    OLD_OBJECT_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    call_id: int
    object: Object
    old_object: Object
    session: str
    identity: str
    def __init__(self, call_id: _Optional[int] = ..., object: _Optional[_Union[Object, _Mapping]] = ..., old_object: _Optional[_Union[Object, _Mapping]] = ..., session: _Optional[str] = ..., identity: _Optional[str] = ...) -> None: ...

class HookAction(_message.Message):
    __slots__ = ("update_args", "result_or_args")
    UPDATE_ARGS_FIELD_NUMBER: _ClassVar[int]
    RESULT_OR_ARGS_FIELD_NUMBER: _ClassVar[int]
    update_args: bool
    result_or_args: str
    def __init__(self, update_args: bool = ..., result_or_args: _Optional[str] = ...) -> None: ...

class RegHookRequest(_message.Message):
    __slots__ = ("initiate", "result")
    class Initiate(_message.Message):
        __slots__ = ("function", "before")
        FUNCTION_FIELD_NUMBER: _ClassVar[int]
        BEFORE_FIELD_NUMBER: _ClassVar[int]
        function: str
        before: bool
        def __init__(self, function: _Optional[str] = ..., before: bool = ...) -> None: ...
    class CallResult(_message.Message):
        __slots__ = ("call_id", "response", "error")
        CALL_ID_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        call_id: int
        response: HookAction
        error: Error
        def __init__(self, call_id: _Optional[int] = ..., response: _Optional[_Union[HookAction, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...
    INITIATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    initiate: RegHookRequest.Initiate
    result: RegHookRequest.CallResult
    def __init__(self, initiate: _Optional[_Union[RegHookRequest.Initiate, _Mapping]] = ..., result: _Optional[_Union[RegHookRequest.CallResult, _Mapping]] = ...) -> None: ...

class RegHookReply(_message.Message):
    __slots__ = ("call_id", "arguments", "original_result", "session", "identity")
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_RESULT_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    call_id: int
    arguments: str
    original_result: str
    session: str
    identity: str
    def __init__(self, call_id: _Optional[int] = ..., arguments: _Optional[str] = ..., original_result: _Optional[str] = ..., session: _Optional[str] = ..., identity: _Optional[str] = ...) -> None: ...

class RegFunctionRequest(_message.Message):
    __slots__ = ("initiate", "result")
    class Initiate(_message.Message):
        __slots__ = ("name", "hookable")
        NAME_FIELD_NUMBER: _ClassVar[int]
        HOOKABLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        hookable: bool
        def __init__(self, name: _Optional[str] = ..., hookable: bool = ...) -> None: ...
    class CallResult(_message.Message):
        __slots__ = ("call_id", "response", "error")
        CALL_ID_FIELD_NUMBER: _ClassVar[int]
        RESPONSE_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        call_id: int
        response: str
        error: Error
        def __init__(self, call_id: _Optional[int] = ..., response: _Optional[str] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...
    INITIATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    initiate: RegFunctionRequest.Initiate
    result: RegFunctionRequest.CallResult
    def __init__(self, initiate: _Optional[_Union[RegFunctionRequest.Initiate, _Mapping]] = ..., result: _Optional[_Union[RegFunctionRequest.CallResult, _Mapping]] = ...) -> None: ...

class RegFunctionReply(_message.Message):
    __slots__ = ("call_id", "arguments", "session", "identity")
    CALL_ID_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    call_id: int
    arguments: str
    session: str
    identity: str
    def __init__(self, call_id: _Optional[int] = ..., arguments: _Optional[str] = ..., session: _Optional[str] = ..., identity: _Optional[str] = ...) -> None: ...

class CallFunctionRequest(_message.Message):
    __slots__ = ("name", "arguments")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    arguments: str
    def __init__(self, name: _Optional[str] = ..., arguments: _Optional[str] = ...) -> None: ...

class CallFunctionReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class HasPermissionRequest(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, permissions: _Optional[_Iterable[str]] = ...) -> None: ...

class HasPermissionReply(_message.Message):
    __slots__ = ("ok",)
    OK_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    def __init__(self, ok: bool = ...) -> None: ...
