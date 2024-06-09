import grpc
import inspect
import json

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from pydantic import TypeAdapter
from queue import Queue
from threading import Thread
from uuid import UUID

from .errors import NoviError, handle_error
from .identity import Identity
from .misc import uuid_to_pb, dt_to_timestamp, tags_to_pb
from .model import EventKind, HookAction, HookPoint, QueryOrder, Tags
from .object import BaseObject, Object, EditableObject
from .proto import novi_pb2

from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from .client import Client


def _queue_as_gen(q: Queue):
    while True:
        yield q.get()


def _wrap_function(
    func,
    wrap: bool = True,
    decode_model: bool = True,
    encode_model: bool = True,
    check_type: bool = True,
    pass_session: bool = True,
    filter_arguments: bool = True,
):
    if not wrap:
        return func

    def wrapper(arguments: Dict[str, Any], session: Optional['Session']):
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

        if pass_session:
            arguments['session'] = session

        if filter_arguments:
            new_args = {}
            for arg in inspect.getfullargspec(func)[0]:
                if arg in arguments:
                    new_args[arg] = arguments[arg]
            arguments = new_args

        resp = func(**arguments)

        if encode_model:
            resp = TypeAdapter(type(resp)).dump_python(resp, mode='json')

        return resp

    return wrapper


class Session:
    token: Optional[str]
    identity: Optional[Identity]

    _entered = False
    _workers: List[Thread]

    def __init__(
        self,
        client: 'Client',
        token: Optional[str],
        identity: Optional[Identity] = None,
    ):
        self.client = client
        self.token = token
        self.identity = identity

        self._workers = []

    def _new_object(self, pb: novi_pb2.Object):
        return Object.from_pb(pb, self)

    def _send(self, fn, request, map_result=None):
        metadata = []
        if self.token:
            metadata.append(('session', self.token))
        if self.identity:
            metadata.append(('identity', self.identity.token))
        result = fn(request, metadata=metadata)
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

    @contextmanager
    def use_identity(self, identity: Identity):
        old_identity = self.identity
        self.identity = identity
        try:
            yield
        finally:
            self.identity = old_identity

    @handle_error
    def login_as(
        self, user: Union[UUID, str], temporary: bool = False
    ) -> Identity:
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
    def get_object(self, id: Union[UUID, str]) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.GetObject,
            novi_pb2.GetObjectRequest(id=uuid_to_pb(id)),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def update_object(
        self, id: Union[UUID, str], tags: Tags, force: bool = False
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
        id: Union[UUID, str],
        tags: Tags,
        scopes: Optional[Set[str]] = None,
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
        self, id: Union[UUID, str], tags: Iterator[str]
    ) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return self._send(
            self.client._stub.DeleteObjectTags,
            novi_pb2.DeleteObjectTagsRequest(id=uuid_to_pb(id), tags=tags),
            lambda reply: self._new_object(reply.object),
        )

    @handle_error
    def delete_object(self, id: Union[UUID, str]):
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
        checkpoint: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        order: QueryOrder = QueryOrder.CREATED_DESC,
        limit: Optional[int] = 30,
    ) -> List[Object]:
        def to_timestamp(dt: Optional[datetime]):
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

    def query_one(self, filter: str, **kwargs) -> Optional[Object]:
        objects = self.query(filter, limit=1, **kwargs)
        if objects:
            return objects[0]
        return None

    def _spawn_worker(self, target, **kwargs):
        worker = Thread(target=target, **kwargs)
        self._workers.append(worker)
        worker.start()

    def join(self):
        for worker in self._workers:
            worker.join()

    def subscribe_stream(
        self,
        filter: str,
        checkpoint: Optional[datetime] = None,
        accept_kinds: Set[EventKind] = {
            EventKind.CREATE,
            EventKind.UPDATE,
            EventKind.DELETE,
        },
    ) -> Iterator[Tuple[BaseObject, EventKind]]:
        it = self._send(
            self.client._stub.Subscribe,
            novi_pb2.SubscribeRequest(
                filter=filter,
                checkpoint=(
                    None if checkpoint is None else dt_to_timestamp(checkpoint)
                ),
                accept_kinds=[kind.value for kind in accept_kinds],
            ),
        )
        try:
            for event in it:
                object = self._new_object(event.object)
                kind = EventKind(event.kind)
                yield object, kind
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise NoviError.from_grpc(e) from None

    def subscribe(
        self,
        filter: str,
        callback: Callable[[BaseObject, EventKind], None],
        checkpoint: Optional[datetime] = None,
        accept_kinds: Set[EventKind] = {
            EventKind.CREATE,
            EventKind.UPDATE,
            EventKind.DELETE,
        },
    ):
        def worker():
            try:
                for object, kind in self.subscribe_stream(
                    filter, checkpoint, accept_kinds
                ):
                    callback(object, kind)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise

        self._spawn_worker(worker)

    @handle_error
    def register_core_hook(
        self, point: HookPoint, filter: str, callback: Callable
    ):
        q = Queue()
        q.put(
            novi_pb2.RegCoreHookRequest(
                initiate=novi_pb2.RegCoreHookRequest.Initiate(
                    point=point.value,
                    filter=filter,
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegCoreHookReply] = self._send(
            self.client._stub.RegisterCoreHook, _queue_as_gen(q)
        )

        def worker():
            try:
                for reply in reply_stream:
                    try:
                        object = EditableObject.from_pb(reply.object)
                        old_object = (
                            EditableObject.from_pb(reply.old_object)
                            if reply.HasField('old_object')
                            else None
                        )
                        session = (
                            Session(self.client, reply.session)
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
                        resp = novi_pb2.RegCoreHookRequest(
                            result=novi_pb2.RegCoreHookRequest.CallResult(
                                call_id=reply.call_id,
                                response=novi_pb2.ObjectEdits(
                                    deletes=[], update={}, clear=False
                                ),
                            )
                        )
                    except Exception:
                        error = NoviError.current(
                            'error in core hook callback'
                        )
                        resp = novi_pb2.RegCoreHookRequest(
                            result=novi_pb2.RegCoreHookRequest.CallResult(
                                call_id=reply.call_id,
                                error=error.to_pb(),
                            )
                        )

                    q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_worker(worker)

    @handle_error
    def register_hook(self, function: str, before: bool, callback: Callable):
        q = Queue()
        q.put(
            novi_pb2.RegHookRequest(
                initiate=novi_pb2.RegHookRequest.Initiate(
                    function=function,
                    before=before,
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegHookReply] = self._send(
            self.client._stub.RegisterHook, _queue_as_gen(q)
        )

        def worker():
            try:
                for reply in reply_stream:
                    try:
                        session = Session(self.client, reply.session)
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
                        resp = novi_pb2.RegHookRequest(
                            result=novi_pb2.RegHookRequest.CallResult(
                                call_id=reply.call_id,
                                response=action_pb,
                            )
                        )
                    except Exception:
                        error = NoviError.current('error in hook callback')
                        resp = novi_pb2.RegHookRequest(
                            result=novi_pb2.RegHookRequest.CallResult(
                                call_id=reply.call_id,
                                error=error.to_pb(),
                            )
                        )

                    q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_worker(worker)

    @handle_error
    def register_function(
        self,
        name: str,
        function: Callable,
        permission: Optional[str] = None,
        **kwargs,
    ):
        function = _wrap_function(function, **kwargs)
        q = Queue()
        q.put(
            novi_pb2.RegFunctionRequest(
                initiate=novi_pb2.RegFunctionRequest.Initiate(
                    name=name, permission=permission
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegFunctionReply] = self._send(
            self.client._stub.RegisterFunction, _queue_as_gen(q)
        )

        def worker():
            try:
                for reply in reply_stream:
                    try:
                        session = Session(self.client, reply.session)
                        session.identity = Identity(reply.identity)
                        resp = function(
                            arguments=json.loads(reply.arguments),
                            session=session,
                        )
                        resp = novi_pb2.RegFunctionRequest(
                            result=novi_pb2.RegFunctionRequest.CallResult(
                                call_id=reply.call_id,
                                response=json.dumps(resp),
                            )
                        )
                    except Exception:
                        error = NoviError.current('error in function call')
                        resp = novi_pb2.RegFunctionRequest(
                            result=novi_pb2.RegFunctionRequest.CallResult(
                                call_id=reply.call_id,
                                error=error.to_pb(),
                            )
                        )

                    q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_worker(worker)

    @handle_error
    def call_function(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._send(
            self.client._stub.CallFunction,
            novi_pb2.CallFunctionRequest(
                name=name, arguments=json.dumps(arguments)
            ),
            lambda reply: json.loads(reply.result),
        )

    def get_object_url(
        self,
        id: Union[UUID, str],
        variant: str = 'original',
        resolve_ipfs: bool = True,
    ) -> str:
        url = self.call_function(
            'file.url',
            {'id': str(id), 'variant': variant},
        )['url']
        if url.startswith('ipfs://') and resolve_ipfs:
            from .file import get_ipfs_gateway

            url = get_ipfs_gateway() + '/ipfs/' + url[7:]

        return url

    def open_object(
        self,
        *args,
        **kwargs,
    ):
        from urllib.request import urlopen

        return urlopen(self.get_object_url(*args, **kwargs))

    def store_object(
        self,
        id: Union[UUID, str],
        path: Optional[Union[Path, str]] = None,
        url: Optional[str] = None,
        variant: str = 'original',
        storage: str = 'default',
        overwrite: bool = False,
    ):
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

        return self.call_function('file.store', args)
