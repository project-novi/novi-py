import aiohttp
import asyncio
import grpc
import inspect
import json

from asyncio import Task, Queue
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import TypeAdapter
from uuid import UUID

from ..errors import NoviError, handle_error
from ..identity import Identity
from ..misc import dt_to_timestamp
from ..model import EventKind, HookAction, HookPoint
from ..object import BaseObject, EditableObject
from ..proto import novi_pb2
from ..session import Session as SyncSession
from .object import Object

from typing import (
    Any,
    AsyncIterator,
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


async def _queue_as_gen(q: Queue):
    while True:
        yield await q.get()


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


class Session(SyncSession):
    _tasks: List[Task]

    def __init__(
        self,
        client: 'Client',
        token: Optional[str],
        identity: Optional[Identity] = None,
    ):
        super().__init__(client, token, identity)
        self._tasks = []

    def _new_object(self, pb: novi_pb2.Object) -> Object:
        return Object.from_pb(pb, self)

    async def _send(self, fn, request, map_result=None):
        metadata = []
        if self.token:
            metadata.append(('session', self.token))
        if self.identity:
            metadata.append(('identity', self.identity.token))
        result = await fn(request, metadata=metadata)
        if map_result:
            return map_result(result)
        return result

    def __enter__(self):
        raise RuntimeError('use async with')

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError('use async with')

    async def __aenter__(self):
        return super().__enter__()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        return super().__exit__(exc_type, exc_val, exc_tb)

    async def query_one(self, filter: str, **kwargs) -> Optional[Object]:
        objects = await self.query(filter, limit=1, **kwargs)
        if objects:
            return objects[0]
        return None

    def _spawn_task(self, coro):
        task = asyncio.create_task(coro)
        self._tasks.append(task)

    async def join(self):
        await asyncio.gather(*self._tasks)

    async def subscribe_stream(
        self,
        filter: str,
        checkpoint: Optional[datetime] = None,
        accept_kinds: Set[EventKind] = {
            EventKind.CREATE,
            EventKind.UPDATE,
            EventKind.DELETE,
        },
    ) -> AsyncIterator[Tuple[BaseObject, EventKind]]:
        it = super()._send(
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
            async for event in it:
                object = self._new_object(event.object)
                kind = EventKind(event.kind)
                yield object, kind
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise NoviError.from_grpc(e) from None

    async def subscribe(
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
        async def worker():
            try:
                async for object, kind in self.subscribe_stream(
                    filter, checkpoint, accept_kinds
                ):
                    resp = callback(object, kind)
                    if inspect.isawaitable(resp):
                        await resp

            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise

        self._spawn_task(worker())

    @handle_error
    async def register_core_hook(
        self, point: HookPoint, filter: str, callback: Callable
    ):
        q = Queue()
        await q.put(
            novi_pb2.RegCoreHookRequest(
                initiate=novi_pb2.RegCoreHookRequest.Initiate(
                    point=point.value,
                    filter=filter,
                )
            )
        )

        reply_stream: AsyncIterator[novi_pb2.RegCoreHookReply] = super()._send(
            self.client._stub.RegisterCoreHook, _queue_as_gen(q)
        )

        async def worker():
            try:
                async for reply in reply_stream:
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
                        if inspect.isawaitable(resp):
                            resp = await resp

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

                    await q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_task(worker())

    @handle_error
    async def register_hook(
        self, function: str, before: bool, callback: Callable
    ):
        q = Queue()
        await q.put(
            novi_pb2.RegHookRequest(
                initiate=novi_pb2.RegHookRequest.Initiate(
                    function=function,
                    before=before,
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegHookReply] = super()._send(
            self.client._stub.RegisterHook, _queue_as_gen(q)
        )

        async def worker():
            try:
                async for reply in reply_stream:
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
                        if inspect.isawaitable(resp):
                            resp = await resp

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

                    await q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_task(worker())

    @handle_error
    async def register_function(
        self,
        name: str,
        function: Callable,
        permission: Optional[str] = None,
        **kwargs,
    ):
        function = _wrap_function(function, **kwargs)
        q = Queue()
        await q.put(
            novi_pb2.RegFunctionRequest(
                initiate=novi_pb2.RegFunctionRequest.Initiate(
                    name=name, permission=permission
                )
            )
        )

        reply_stream: Iterator[novi_pb2.RegFunctionReply] = super()._send(
            self.client._stub.RegisterFunction, _queue_as_gen(q)
        )

        async def worker():
            try:
                async for reply in reply_stream:
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

                    await q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_task(worker())

    async def get_object_url(
        self,
        id: Union[UUID, str],
        variant: str = 'original',
        resolve_ipfs: bool = True,
    ) -> str:
        url = (
            await self.call_function(
                'file.url',
                {'id': str(id), 'variant': variant},
            )
        )['url']
        if url.startswith('ipfs://') and resolve_ipfs:
            from ..file import get_ipfs_gateway

            url = get_ipfs_gateway() + '/ipfs/' + url[7:]

        return url

    @asynccontextmanager
    async def open_object(
        self,
        *args,
        session: Optional[aiohttp.ClientSession] = None,
        **kwargs,
    ) -> AsyncIterator[aiohttp.StreamReader]:
        url = await self.get_object_url(*args, **kwargs)

        if session is None:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    yield resp.content
        else:
            async with session.get(url) as resp:
                yield resp.content
