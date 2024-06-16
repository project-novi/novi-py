import aiohttp
import asyncio
import grpc
import inspect
import sys

from asyncio import Task, Queue, Semaphore
from contextlib import asynccontextmanager

from ..errors import NoviError, PreconditionFailedError, handle_error
from ..identity import Identity
from ..misc import mock_as_coro, mock_with_return, uuid_from_pb
from ..model import EventKind, SessionMode, SubscribeEvent
from ..object import BaseObject
from ..proto import novi_pb2
from ..session import Session as SyncSession
from .object import Object

from collections.abc import AsyncIterator, Callable, Coroutine
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
    client: 'Client'

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
        if not self._entered:
            return

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
        SyncSession.subscribe_stream,
        AsyncIterator[SubscribeEvent],
    )
    async def subscribe_stream(
        self,
        filter: str,
        *args,
        wrap_session: SessionMode | None = None,
        latest: bool = True,
        recheck: bool = True,
        parallel: int | None = None,
        **kwargs,
    ):
        it = super()._send(
            self.client._stub.Subscribe,
            self._subscribe_request(filter, *args, **kwargs),
        )
        try:
            async for event in it:
                kind = EventKind(event.kind)
                if wrap_session is not None:
                    session = await self.client.session(mode=wrap_session)
                    if parallel is None:
                        await session.__aenter__()

                    exc_info = None, None, None
                    try:
                        if latest:
                            try:
                                object = session.get_object(
                                    uuid_from_pb(event.object.id),
                                    precondition=filter if recheck else None,
                                )
                            except PreconditionFailedError:
                                continue
                        else:
                            object = session._new_object(event.object)

                        yield SubscribeEvent(object, kind, session)
                    except:  # noqa: E722
                        exc_info = sys.exc_info()
                    finally:
                        if parallel is None:
                            await session.__aexit__(*exc_info)

                else:
                    yield SubscribeEvent(
                        BaseObject.from_pb(event.object), kind, session
                    )
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.CANCELLED:
                raise NoviError.from_grpc(e) from None

    @mock_as_coro(SyncSession.subscribe)
    async def subscribe(
        self,
        filter: str,
        callback: Callable[[SubscribeEvent], None],
        parallel: int | None = None,
        **kwargs,
    ):
        async def worker():
            sem = Semaphore(parallel) if parallel is not None else None

            async def task(event):
                sem.acquire()
                try:
                    if event.session:
                        async with event.session:
                            resp = callback(event)
                            if inspect.isawaitable(resp):
                                await resp
                    else:
                        resp = callback(event)
                        if inspect.isawaitable(resp):
                            await resp
                finally:
                    sem.release()

            try:
                async for event in self.subscribe_stream(
                    filter, parallel=parallel, **kwargs
                ):
                    if parallel is None:
                        await task(event)
                    else:
                        self._spawn_task(task(event))

            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise

        self._spawn_task(worker())

    @handle_error
    async def _bidi_register(self, fn, init, callback: Callable):
        q = Queue()
        await q.put(init)

        reply_stream = super()._send(fn, _queue_as_gen(q))
        await reply_stream.read()

        async def worker():
            async def task_main(reply):
                resp = callback(reply)
                if inspect.isawaitable(resp):
                    await resp

                await q.put(resp)

            try:
                while True:
                    reply = await reply_stream.read()
                    asyncio.create_task(task_main(reply))
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.CANCELLED:
                    raise NoviError.from_grpc(e) from None

        self._spawn_task(worker())

    @mock_as_coro(SyncSession.register_core_hook)
    def register_core_hook(self, *args, **kwargs):
        return super().register_core_hook(*args, **kwargs)

    @mock_as_coro(SyncSession.register_hook)
    def register_hook(self, *args, **kwargs):
        return super().register_hook(*args, **kwargs)

    @mock_as_coro(SyncSession.register_function)
    def register_function(self, *args, **kwargs):
        return super().register_function(*args, **kwargs)

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

    @mock_as_coro(SyncSession.put_file)
    def put_file(self, *args, **kwargs):
        return super().put_file(*args, **kwargs)

    @mock_as_coro(SyncSession.store_file)
    def store_file(self, *args, **kwargs):
        return super().store_file(*args, **kwargs)

    @mock_as_coro(SyncSession.has_permission)
    def has_permission(self, *args, **kwargs):
        return super().has_permission(*args, **kwargs)

    @mock_as_coro(SyncSession.check_permission)
    def check_permission(self, *args, **kwargs):
        return super().check_permission(*args, **kwargs)
