import aiohttp
import asyncio
import grpc
import inspect
import json

from asyncio import Task, Queue
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from ..errors import NoviError, handle_error
from ..identity import Identity
from ..misc import use_signature_as_coro, use_signature_with_return
from ..model import EventKind, HookAction, HookPoint
from ..object import BaseObject, EditableObject
from ..proto import novi_pb2
from ..session import Session as SyncSession, _wrap_function
from .object import Object

from collections.abc import AsyncIterator, Callable, Iterator
from typing import ParamSpec, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

P = ParamSpec('P')
R = TypeVar('R')


async def _queue_as_gen(q: Queue):
    while True:
        yield await q.get()


class Session(SyncSession):
    _tasks: list[Task]

    def __init__(
        self,
        client: 'Client',
        token: str | None,
        identity: Identity | None = None,
    ):
        super().__init__(client, token, identity)
        self._tasks = []

    def _new_object(self, pb: novi_pb2.Object) -> Object:
        return Object.from_pb(pb, self)

    async def _send(self, fn, request, map_result=None):
        result = await fn(request, metadata=self._build_metadata())
        if map_result:
            return map_result(result)
        return result

    def __enter__(self):
        raise RuntimeError('use async with')

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError('use async with')

    async def __aenter__(self):
        return super().__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await super().__exit__(exc_type, exc_val, exc_tb)

    def _spawn_task(self, coro):
        task = asyncio.create_task(coro)
        self._tasks.append(task)

    async def join(self):
        await asyncio.gather(*self._tasks)

    @use_signature_as_coro(SyncSession.end)
    def end(self, *args, **kwargs):
        return super().end(*args, **kwargs)

    @use_signature_as_coro(SyncSession.login_as)
    def login_as(self, *args, **kwargs):
        return super().login_as(*args, **kwargs)

    @use_signature_as_coro(SyncSession.create_object)
    def create_object(self, *args, **kwargs):
        return super().create_object(*args, **kwargs)

    @use_signature_as_coro(SyncSession.get_object)
    def get_object(self, *args, **kwargs):
        return super().get_object(*args, **kwargs)

    @use_signature_as_coro(SyncSession.update_object)
    def update_object(self, *args, **kwargs):
        return super().update_object(*args, **kwargs)

    @use_signature_as_coro(SyncSession.replace_object)
    def replace_object(self, *args, **kwargs):
        return super().replace_object(*args, **kwargs)

    @use_signature_as_coro(SyncSession.delete_object_tags)
    def delete_object_tags(self, *args, **kwargs):
        return super().delete_object_tags(*args, **kwargs)

    @use_signature_as_coro(SyncSession.delete_object)
    def delete_object(self, *args, **kwargs):
        return super().delete_object(*args, **kwargs)

    @use_signature_as_coro(SyncSession.query)
    def query(self, *args, **kwargs):
        return super().query(*args, **kwargs)

    @use_signature_as_coro(SyncSession.query_one)
    def query_one(self, *args, **kwargs):
        return super().query_one(*args, **kwargs)

    @use_signature_with_return(
        SyncSession._subscribe,
        AsyncIterator[tuple[BaseObject, EventKind]],
    )
    async def subscribe_stream(self, *args, **kwargs):
        it = super()._subscribe(*args, **kwargs)
        try:
            async for event in it:
                object = self._new_object(event.object)
                kind = EventKind(event.kind)
                yield object, kind
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise NoviError.from_grpc(e) from None

    @use_signature_as_coro(SyncSession.subscribe)
    async def subscribe(
        self,
        filter: str,
        callback: Callable[[BaseObject, EventKind], None],
        checkpoint: datetime | None = None,
        accept_kinds: set[EventKind] = {
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
        permission: str | None = None,
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
        id: UUID | str,
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
        session: aiohttp.ClientSession | None = None,
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
