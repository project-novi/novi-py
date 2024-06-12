import grpc
import inspect
import json

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, TypeAdapter
from queue import Queue
from threading import Thread
from uuid import UUID

from .errors import NoviError, handle_error
from .identity import Identity
from .misc import (
    uuid_to_pb,
    dt_to_timestamp,
    tags_to_pb,
    mock_with_return,
)
from .model import EventKind, HookAction, HookPoint, QueryOrder, Tags
from .object import BaseObject, Object, EditableObject
from .proto import novi_pb2

from collections.abc import Callable, Iterator
from typing import (
    Any,
    BinaryIO,
    Concatenate,
    ParamSpec,
    TypedDict,
    TypeVar,
    TYPE_CHECKING,
)
from typing_extensions import Unpack

if TYPE_CHECKING:
    from .client import Client


class ObjectUrlOptions(TypedDict, total=False):
    resolve_ipfs: bool


class StoreObjectOptions(TypedDict, total=False):
    path: Path | str | None
    url: str | None

    storage: str
    overwrite: bool


class WrapFunctionOptions(TypedDict, total=False):
    wrap: bool
    decode_model: bool
    check_type: bool
    includes: list[str]
    filter_arguments: bool


S = TypeVar('S')
P = ParamSpec('P')


def _queue_as_gen(q: Queue):
    while True:
        yield q.get()


def _auto_transform(value, transform):
    if inspect.isawaitable(value):

        async def wrapper():
            return transform(await value)

        return wrapper()

    return transform(value)


def _mock_subscribe(f: Callable[Concatenate[S, str, P], Any]) -> Callable[
    [Callable[..., None]],
    Callable[
        Concatenate[S, str, Callable[[BaseObject, EventKind], None], P], None
    ],
]:
    return lambda _: _


# On edit, please also edit `WrapFunctionOptions`
def _wrap_function(
    func,
    wrap: bool = True,
    decode_model: bool = True,
    check_type: bool = True,
    includes: list[str] = ['session', 'original_result'],
    filter_arguments: bool = True,
):
    if not wrap:
        return func

    def wrapper(arguments: dict[str, Any], **kwargs):
        if decode_model:
            for arg, ty in func.__annotations__.items():
                if arg not in arguments:
                    continue

                val = arguments[arg]
                if not isinstance(val, ty):
                    continue
                arguments[arg] = TypeAdapter(ty).validate_python(val)

        if check_type:
            for arg in inspect.getfullargspec(func)[0]:
                if arg not in arguments:
                    continue

                val = arguments[arg]
                ty = func.__annotations__.get(arg, None)
                if ty and not isinstance(val, ty):
                    raise TypeError(
                        f'expected {ty} for argument {arg!r}, got {type(val)}'
                    )

        for include in includes:
            if include in kwargs:
                arguments[include] = kwargs[include]

        if filter_arguments:
            new_args = {}
            for arg in inspect.getfullargspec(func)[0]:
                if arg in arguments:
                    new_args[arg] = arguments[arg]
            arguments = new_args

        return func(**arguments)

    return wrapper


class Session:
    token: str | None
    identity: Identity | None

    _entered = False
    _workers: list[Thread]

    def __init__(
        self,
        client: 'Client',
        token: str | None,
        identity: Identity | None = None,
    ):
        self.client = client
        self.token = token
        self.identity = identity

        self._workers = []

    def _new_object(self, pb: novi_pb2.Object):
        return Object.from_pb(pb, self)

    def _build_metadata(self):
        metadata = []
        if self.token:
            metadata.append(('session', self.token))
        if self.identity:
            metadata.append(('identity', self.identity.token))
        return metadata

    def _send(self, fn, request, map_result=None):
        result = fn(request, metadata=self._build_metadata())
        if map_result:
            return map_result(result)
        return result

    def __enter__(self):
        if self._entered:
            raise RuntimeError('session already entered')
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._entered:
            raise RuntimeError('session not entered')

        return self.end(exc_type is None)

    def end(self, commit=True):
        self._entered = False
        return self._send(
            self.client._stub.EndSession,
            novi_pb2.EndSessionRequest(commit=commit),
            lambda _: None,
        )

    def _spawn_worker(self, target, **kwargs):
        worker = Thread(target=target, **kwargs)
        self._workers.append(worker)
        worker.start()

    def join(self):
        for worker in self._workers:
            worker.join()

    @contextmanager
    def fidentity(self, identity: Identity):
        old_identity = self.identity
        self.identity = identity
        try:
            yield
        finally:
            self.identity = old_identity

    @handle_error
    def login_as(self, user: UUID | str, temporary: bool = False) -> Identity:
        if isinstance(user, str):
            user = UUID(user)

        return self._send(
            self.client._stub.LoginAs,
            novi_pb2.LoginAsRequest(
                user=uuid_to_pb(user), temporary=temporary
            ),
            lambda reply: Identity(reply.identity),
        )

    @handle_error
    def create_object(self, tags: Tags) -> Object:
        return self._send(
            self.client._stub.CreateObject,
            novi_pb2.CreateObjectRequest(tags=tags_to_pb(tags)),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def get_object(self, id: UUID | str) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.GetObject,
            novi_pb2.GetObjectRequest(id=uuid_to_pb(id)),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def update_object(
        self, id: UUID | str, tags: Tags, force: bool = False
    ) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.UpdateObject,
            novi_pb2.UpdateObjectRequest(
                id=uuid_to_pb(id), tags=tags_to_pb(tags), force=force
            ),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def replace_object(
        self,
        id: UUID | str,
        tags: Tags,
        scopes: set[str] | None = None,
        force: bool = False,
    ) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.ReplaceObject,
            novi_pb2.ReplaceObjectRequest(
                id=uuid_to_pb(id),
                tags=tags_to_pb(tags),
                scopes=(
                    None if scopes is None else novi_pb2.Scopes(scopes=scopes)
                ),
                force=force,
            ),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def delete_object_tags(
        self, id: UUID | str, tags: Iterator[str]
    ) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.DeleteObjectTags,
            novi_pb2.DeleteObjectTagsRequest(id=uuid_to_pb(id), tags=tags),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def delete_object(self, id: UUID | str):
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.DeleteObject,
            novi_pb2.DeleteObjectRequest(id=uuid_to_pb(id)),
            lambda _: None,
        )

    @handle_error
    def query(
        self,
        filter: str,
        checkpoint: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        order: QueryOrder = QueryOrder.CREATED_DESC,
        limit: int | None = 30,
    ) -> list[Object]:
        def to_timestamp(dt: datetime | None):
            return None if dt is None else dt_to_timestamp(dt)

        return self._send(
            self.client._stub.Query,
            novi_pb2.QueryRequest(
                filter=filter,
                checkpoint=to_timestamp(checkpoint),
                updated_after=to_timestamp(updated_after),
                updated_before=to_timestamp(updated_before),
                created_after=to_timestamp(created_after),
                created_before=to_timestamp(created_before),
                order=order.value,
                limit=limit,
            ),
            lambda reply: [self._new_object(obj) for obj in reply.objects],
        )

    def query_one(self, filter: str, **kwargs) -> Object | None:
        return _auto_transform(
            self.query(filter, limit=1, **kwargs),
            lambda objects: objects[0] if objects else None,
        )

    def _subscribe_request(
        self,
        filter: str,
        checkpoint: datetime | None = None,
        accept_kinds: set[EventKind] = {
            EventKind.CREATE,
            EventKind.UPDATE,
            EventKind.DELETE,
        },
    ):
        return novi_pb2.SubscribeRequest(
            filter=filter,
            checkpoint=(
                None if checkpoint is None else dt_to_timestamp(checkpoint)
            ),
            accept_kinds=[kind.value for kind in accept_kinds],
        )

    @mock_with_return(
        _subscribe_request, Iterator[tuple[BaseObject, EventKind]]
    )
    def subscribe_stream(self, *args, **kwargs):
        it = self._send(
            self.client._stub.Subscribe,
            self._subscribe_request(*args, **kwargs),
        )
        try:
            for event in it:
                object = self._new_object(event.object)
                kind = EventKind(event.kind)
                yield object, kind
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise NoviError.from_grpc(e) from None

    @_mock_subscribe(_subscribe_request)
    def subscribe(
        self,
        filter: str,
        callback: Callable[[BaseObject, EventKind], None],
        **kwargs,
    ):
        def worker():
            try:
                for object, kind in self.subscribe_stream(filter, **kwargs):
                    callback(object, kind)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise

        self._spawn_worker(worker)

    def _core_hook_init(self, point: HookPoint, filter: str):
        return novi_pb2.RegCoreHookRequest(
            initiate=novi_pb2.RegCoreHookRequest.Initiate(
                point=point.value,
                filter=filter,
            )
        )

    def _core_hook_call(
        self, callback: Callable, reply: novi_pb2.RegCoreHookReply
    ):
        try:
            object = EditableObject.from_pb(reply.object)
            old_object = (
                EditableObject.from_pb(reply.old_object)
                if reply.HasField('old_object')
                else None
            )
            session = (
                type(self)(self.client, reply.session)
                if reply.HasField('session')
                else None
            )
            identity = Identity(reply.identity)
            if session is not None:
                session.identity = identity
            resp = callback(
                object=object,
                old_object=old_object,
                session=session,
                identity=identity,
            )
            # TODO: ObjectEdits
            return _auto_transform(
                resp,
                lambda x: novi_pb2.RegCoreHookRequest(
                    result=novi_pb2.RegCoreHookRequest.CallResult(
                        call_id=reply.call_id,
                        response=novi_pb2.ObjectEdits(
                            deletes=[], update={}, clear=False
                        ),
                    )
                ),
            )
        except Exception:
            error = NoviError.current('error in core hook callback')
            return novi_pb2.RegCoreHookRequest(
                result=novi_pb2.RegCoreHookRequest.CallResult(
                    call_id=reply.call_id,
                    error=error.to_pb(),
                )
            )

    @handle_error
    def _bidi_register(self, fn, init, callback: Callable):
        q = Queue()
        q.put(init)

        reply_stream = self._send(fn, _queue_as_gen(q))
        next(reply_stream)

        def worker():
            try:
                for reply in reply_stream:
                    resp = callback(reply)
                    q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_worker(worker)

    def register_core_hook(
        self, point: HookPoint, filter: str, callback: Callable
    ):
        return self._bidi_register(
            self.client._stub.RegisterCoreHook,
            self._core_hook_init(point, filter),
            lambda reply: self._core_hook_call(callback, reply),
        )

    def _hook_init(self, function: str, before: bool):
        return novi_pb2.RegHookRequest(
            initiate=novi_pb2.RegHookRequest.Initiate(
                function=function,
                before=before,
            )
        )

    def _hook_call(self, callback: Callable, reply: novi_pb2.RegHookReply):
        try:
            session = type(self)(self.client, reply.session)
            session.identity = Identity(reply.identity)
            original_result = (
                json.loads(reply.original_result)
                if reply.HasField('original_result')
                else None
            )
            resp = callback(
                arguments=json.loads(reply.arguments),
                original_result=original_result,
                session=session,
            )

            def transform(resp):
                if resp is None:
                    resp = HookAction.none()
                assert isinstance(resp, HookAction)

                action_pb = novi_pb2.HookAction(
                    update_args=resp.update_args,
                    result_or_args=(
                        None
                        if resp.result_or_args is None
                        else json.dumps(resp.result_or_args)
                    ),
                )
                return novi_pb2.RegHookRequest(
                    result=novi_pb2.RegHookRequest.CallResult(
                        call_id=reply.call_id,
                        response=action_pb,
                    )
                )

            return _auto_transform(resp, transform)

        except Exception:
            error = NoviError.current('error in hook callback')
            return novi_pb2.RegHookRequest(
                result=novi_pb2.RegHookRequest.CallResult(
                    call_id=reply.call_id,
                    error=error.to_pb(),
                )
            )

    @handle_error
    def register_hook(
        self,
        function: str,
        callback: Callable,
        before: bool = True,
        **kwargs: Unpack[WrapFunctionOptions],
    ):
        callback = _wrap_function(callback, **kwargs)

        def transform(resp):
            if resp is None:
                resp = HookAction.none()
            elif isinstance(resp, dict):
                resp = HookAction.update_result(resp)
            elif isinstance(resp, BaseModel):
                resp = HookAction.update_result(resp.model_dump(mode='json'))
            elif not isinstance(resp, HookAction):
                raise TypeError('hook callback must return a HookAction')

            return resp

        def transformed_callback(*args, **kwargs):
            return _auto_transform(
                callback(*args, **kwargs),
                transform,
            )

        return self._bidi_register(
            self.client._stub.RegisterHook,
            self._hook_init(function, before),
            lambda reply: self._hook_call(transformed_callback, reply),
        )

    def _function_init(self, name: str, hookable: bool):
        return novi_pb2.RegFunctionRequest(
            initiate=novi_pb2.RegFunctionRequest.Initiate(
                name=name, hookable=hookable
            )
        )

    def _function_call(
        self, callback: Callable, reply: novi_pb2.RegFunctionReply
    ):
        try:
            session = type(self)(self.client, reply.session)
            session.identity = Identity(reply.identity)
            resp = callback(
                arguments=json.loads(reply.arguments),
                session=session,
            )
            return _auto_transform(
                resp,
                lambda x: novi_pb2.RegFunctionRequest(
                    result=novi_pb2.RegFunctionRequest.CallResult(
                        call_id=reply.call_id,
                        response='{}' if x is None else json.dumps(x),
                    )
                ),
            )
        except Exception:
            error = NoviError.current('error in function call')
            return novi_pb2.RegFunctionRequest(
                result=novi_pb2.RegFunctionRequest.CallResult(
                    call_id=reply.call_id,
                    error=error.to_pb(),
                )
            )

    @handle_error
    def register_function(
        self,
        name: str,
        function: Callable,
        hookable: bool = True,
        **kwargs: Unpack[WrapFunctionOptions],
    ):
        function = _wrap_function(function, **kwargs)

        def transform(resp):
            if resp is None:
                resp = {}
            elif isinstance(resp, BaseModel):
                resp = resp.model_dump(mode='json')
            elif not isinstance(resp, dict):
                raise TypeError(
                    'function return value must be a dict or BaseModel'
                )

            return resp

        def transformed_function(*args, **kwargs):
            return _auto_transform(
                function(*args, **kwargs),
                transform,
            )

        return self._bidi_register(
            self.client._stub.RegisterFunction,
            self._function_init(name, hookable),
            lambda reply: self._function_call(transformed_function, reply),
        )

    @handle_error
    def call_function(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        return self._send(
            self.client._stub.CallFunction,
            novi_pb2.CallFunctionRequest(
                name=name, arguments=json.dumps(arguments)
            ),
            lambda reply: json.loads(reply.result),
        )

    # On edit, please also edit `ObjectUrlOptions`
    def get_object_url(
        self,
        id: UUID | str,
        variant: str = 'original',
        resolve_ipfs: bool = True,
    ) -> str:
        def transform(resp):
            url = resp['url']
            if url.startswith('ipfs://') and resolve_ipfs:
                from .file import get_ipfs_gateway

                url = get_ipfs_gateway() + '/ipfs/' + url[7:]

            return url

        return _auto_transform(
            self.call_function(
                'file.url',
                {'id': str(id), 'variant': variant},
            ),
            transform,
        )

    @mock_with_return(get_object_url, BinaryIO)
    def open_object(self, *args, **kwargs):
        from urllib.request import urlopen

        return urlopen(self.get_object_url(*args, **kwargs))

    # On edit, please also edit `StoreObjectOptions`
    def store_object(
        self,
        id: UUID | str,
        variant: str = 'original',
        *,
        path: Path | str | None = None,
        url: str | None = None,
        storage: str = 'default',
        overwrite: bool = False,
    ) -> None:
        """Stores a file or URL as the object's content."""
        args = {
            'id': str(id),
            'variant': variant,
            'storage': storage,
            'overwrite': overwrite,
        }
        if path is not None:
            if url is not None:
                raise ValueError('cannot specify both path and url')
            args['path'] = str(path)
        elif url is not None:
            args['url'] = url
        else:
            raise ValueError('must specify either path or url')

        return _auto_transform(
            self.call_function('file.store', args),
            lambda _: None,
        )
