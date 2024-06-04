import grpc
import inspect
import json

from contextlib import contextmanager
from datetime import datetime
from pydantic import TypeAdapter
from queue import Queue
from threading import Thread
from uuid import UUID

from .errors import NoviError, handle_error
from .identity import Identity
from .misc import uuid_to_pb, dt_to_timestamp
from .model import EventKind, HookPoint, QueryOrder
from .object import BaseObject, Object, EditableObject, Tags
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


def _tags_to_pb(ts: Tags) -> novi_pb2.Tags:
    tags = []
    properties = {}
    for tag, value in ts.items():
        if value is None:
            tags.append(tag)
        else:
            properties[tag] = value

    return novi_pb2.Tags(tags=tags, properties=properties)


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
        self._client = client
        self.token = token
        self.identity = identity

        self._workers = []

    def _send(self, fn, request):
        metadata = []
        if self.token:
            metadata.append(('session', self.token))
        if self.identity:
            metadata.append(('identity', self.identity.token))
        return fn(request, metadata=metadata)

    def __enter__(self):
        if self._entered:
            raise RuntimeError('session already entered')
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._entered:
            raise RuntimeError('session not entered')

        self.end(exc_type is None)

    def end(self, commit=True):
        self._entered = False
        self._send(
            self._client._stub.EndSession,
            novi_pb2.EndSessionRequest(commit=commit),
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
    def login_as(self, user: Union[UUID, str]) -> Identity:
        if isinstance(user, str):
            user = UUID(user)

        token = self._send(
            self._client._stub.LoginAs,
            novi_pb2.LoginAsRequest(user=uuid_to_pb(user)),
        ).identity
        return Identity(token)

    @handle_error
    def create_object(self, tags: Tags) -> Object:
        return Object.from_pb(
            self._send(
                self._client._stub.CreateObject,
                novi_pb2.CreateObjectRequest(tags=_tags_to_pb(tags)),
            ).object,
            self,
        )

    @handle_error
    def get_object(self, id: Union[UUID, str]) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return Object.from_pb(
            self._send(
                self._client._stub.GetObject,
                novi_pb2.GetObjectRequest(id=uuid_to_pb(id)),
            ).object,
            self,
        )

    @handle_error
    def update_object(
        self, id: Union[UUID, str], tags: Tags, force: bool = False
    ) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return Object.from_pb(
            self._send(
                self._client._stub.UpdateObject,
                novi_pb2.UpdateObjectRequest(
                    id=uuid_to_pb(id), tags=_tags_to_pb(tags), force=force
                ),
            ).object,
            self,
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

        return Object.from_pb(
            self._send(
                self._client._stub.ReplaceObject,
                novi_pb2.ReplaceObjectRequest(
                    id=uuid_to_pb(id),
                    tags=_tags_to_pb(tags),
                    scopes=(
                        None
                        if scopes is None
                        else novi_pb2.Scopes(scopes=scopes)
                    ),
                    force=force,
                ),
            ).object,
            self,
        )

    @handle_error
    def delete_object_tags(
        self, id: Union[UUID, str], tags: Iterator[str]
    ) -> Object:
        if isinstance(id, str):
            id = UUID(id)

        return Object.from_pb(
            self._send(
                self._client._stub.DeleteObjectTags,
                novi_pb2.DeleteObjectTagsRequest(id=uuid_to_pb(id), tags=tags),
            ).object,
            self,
        )

    @handle_error
    def delete_object(self, id: Union[UUID, str]):
        if isinstance(id, str):
            id = UUID(id)

        self._send(
            self._client._stub.DeleteObject,
            novi_pb2.DeleteObjectRequest(id=uuid_to_pb(id)),
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
    ):
        def to_timestamp(dt: Optional[datetime]):
            return None if dt is None else dt_to_timestamp(dt)

        objects = self._send(
            self._client._stub.Query,
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
        )
        return [Object.from_pb(obj, self) for obj in objects.objects]

    def query_one(
        self,
        filter: str,
        **kwargs,
    ) -> Optional[Object]:
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
            self._client._stub.Subscribe,
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
                object = Object.from_pb(event.object, self)
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

        def request_stream():
            while True:
                yield q.get()

        q.put(
            novi_pb2.RegCoreHookRequest(
                initiate=novi_pb2.RegCoreHookRequest.Initiate(
                    point=point.value,
                    filter=filter,
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegCoreHookReply] = self._send(
            self._client._stub.RegisterCoreHook, request_stream()
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
                            Session(self._client, reply.session)
                            if reply.HasField('session')
                            else None
                        )
                        resp = callback(
                            object=object,
                            old_object=old_object,
                            session=session,
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
                        error = NoviError.current()
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

        def request_stream():
            while True:
                yield q.get()

        q.put(
            novi_pb2.RegHookRequest(
                initiate=novi_pb2.RegHookRequest.Initiate(
                    function=function,
                    before=before,
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegHookReply] = self._send(
            self._client._stub.RegisterHook, request_stream()
        )

        def worker():
            try:
                for reply in reply_stream:
                    try:
                        session = Session(self._client, reply.session)
                        original_result = (
                            json.loads(reply.original_result)
                            if reply.HasField('original_result')
                            else None
                        )
                        resp = callback(
                            arguments=json.loads(reply.arguments),
                            original_reuslt=original_result,
                            session=session,
                        )
                        resp = novi_pb2.RegHookRequest(
                            result=novi_pb2.RegHookRequest.CallResult(
                                call_id=reply.call_id,
                                response=json.dumps(resp),
                            )
                        )
                    except Exception:
                        error = NoviError.current()
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
        **kwargs,
    ):
        function = _wrap_function(function, **kwargs)
        q = Queue()

        def request_stream():
            while True:
                yield q.get()

        q.put(
            novi_pb2.RegFunctionRequest(
                initiate=novi_pb2.RegFunctionRequest.Initiate(name=name)
            )
        )

        reply_stream: Iterator[novi_pb2.RegFunctionReply] = self._send(
            self._client._stub.RegisterFunction, request_stream()
        )

        def worker():
            try:
                for reply in reply_stream:
                    try:
                        session = (
                            Session(self._client, reply.session)
                            if reply.HasField('session')
                            else None
                        )
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
                        error = NoviError.current()
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
    ) -> Any:
        result = self._send(
            self._client._stub.CallFunction,
            novi_pb2.CallFunctionRequest(
                name=name, arguments=json.dumps(arguments)
            ),
        ).result
        return json.loads(result)
