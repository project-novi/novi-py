import aiohttp
import asyncio
import grpc
import inspect

from asyncio import Task, Queue
from contextlib import asynccontextmanager
from datetime import datetime

from ..errors import NoviError, handle_error
from ..identity import Identity
from ..misc import mock_as_coro, mock_with_return
from ..model import EventKind, HookPoint
from ..object import BaseObject
from ..proto import novi_pb2
from ..session import Session as SyncSession, _wrap_function
from .object import Object

from collections.abc import AsyncIterator, Callable, Coroutine, Iterator
from typing import Any, ParamSpec, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

P = ParamSpec('P')
R = TypeVar('R')


async def _queue_as_gen(q: Queue):
    while True:
        yield await q.get()


def _mock_return_object(f: Callable[P, Any]) -> Callable[
    [Callable[..., Any]],
    Callable[P, Coroutine[Any, Any, Object]],
]:
    return lambda _: _


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

    @mock_as_coro(SyncSession.end)
    def end(self, *args, **kwargs):
        return super().end(*args, **kwargs)

    @mock_as_coro(SyncSession.login_as)
    def login_as(self, *args, **kwargs):
        return super().login_as(*args, **kwargs)

    @_mock_return_object(SyncSession.create_object)
    def create_object(self, *args, **kwargs):
        return super().create_object(*args, **kwargs)

    @_mock_return_object(SyncSession.get_object)
    def get_object(self, *args, **kwargs):
        return super().get_object(*args, **kwargs)

    @_mock_return_object(SyncSession.update_object)
    def update_object(self, *args, **kwargs):
        return super().update_object(*args, **kwargs)

    @_mock_return_object(SyncSession.replace_object)
    def replace_object(self, *args, **kwargs):
        return super().replace_object(*args, **kwargs)

    @_mock_return_object(SyncSession.delete_object_tags)
    def delete_object_tags(self, *args, **kwargs):
        return super().delete_object_tags(*args, **kwargs)

    @_mock_return_object(SyncSession.delete_object)
    def delete_object(self, *args, **kwargs):
        return super().delete_object(*args, **kwargs)

    @mock_with_return(SyncSession.query, Coroutine[Any, Any, list[Object]])
    def query(self, *args, **kwargs):
        return super().query(*args, **kwargs)

    @mock_with_return(
        SyncSession.query_one, Coroutine[Any, Any, Object | None]
    )
    def query_one(self, *args, **kwargs):
        return super().query_one(*args, **kwargs)

    @mock_with_return(
        SyncSession._subscribe,
        AsyncIterator[tuple[BaseObject, EventKind]],
    )
    async def subscribe_stream(self, *args, **kwargs):
        it = self._subscribe(*args, **kwargs)
        try:
            async for event in it:
                object = self._new_object(event.object)
                kind = EventKind(event.kind)
                yield object, kind
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise NoviError.from_grpc(e) from None

    @mock_as_coro(SyncSession.subscribe)
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
        await q.put(self._core_hook_init(point, filter))

        reply_stream: AsyncIterator[novi_pb2.RegCoreHookReply] = super()._send(
            self.client._stub.RegisterCoreHook, _queue_as_gen(q)
        )

        async def worker():
            try:
                async for reply in reply_stream:
                    resp = self._core_hook_call(callback, reply)
                    if inspect.isawaitable(resp):
                        resp = await resp

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
        await q.put(self._hook_init(function, before))

        reply_stream: Iterator[novi_pb2.RegHookReply] = super()._send(
            self.client._stub.RegisterHook, _queue_as_gen(q)
        )

        async def worker():
            try:
                async for reply in reply_stream:
                    resp = self._hook_call(callback, reply)
                    if inspect.isawaitable(resp):
                        resp = await resp

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
        await q.put(self._function_init(name, permission))

        reply_stream: Iterator[novi_pb2.RegFunctionReply] = super()._send(
            self.client._stub.RegisterFunction, _queue_as_gen(q)
        )

        async def worker():
            try:
                async for reply in reply_stream:
                    resp = self._function_call(function, reply)
                    if inspect.isawaitable(resp):
                        resp = await resp

                    await q.put(resp)
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_task(worker())

    @mock_as_coro(SyncSession.get_object_url)
    def get_object_url(self, *args, **kwargs):
        return super().get_object_url(*args, **kwargs)

    @asynccontextmanager
    @mock_with_return(
        SyncSession.open_object, AsyncIterator[aiohttp.StreamReader]
    )
    async def open_object(self, *args, **kwargs):
        url = await self.get_object_url(*args, **kwargs)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                yield resp.content

    @mock_as_coro(SyncSession.store_object)
    def store_object(self, *args, **kwargs):
        return super().store_object(*args, **kwargs)
