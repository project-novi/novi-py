import aiohttp
import asyncio
import grpc
import inspect

from asyncio import Lock, Task, Queue, Semaphore
from contextlib import asynccontextmanager

from ..errors import NoviError, PreconditionFailedError, handle_error
from ..identity import Identity
from ..misc import KeyLock, mock_as_coro, mock_with_return
from ..model import EventKind, ObjectLock, SessionMode, SubscribeEvent
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

    def persist(self) -> 'Session':
        self._entered = False
        return Session(self.client, self.token, self.identity)

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

    async def _sync_sub_object(
        self,
        session: 'Session',
        object: BaseObject,
        filter: str,
        lock: ObjectLock,
        latest: bool,
        recheck: bool,
    ) -> Object:
        if latest:
            try:
                return await session.get_object(
                    object.id,
                    precondition=filter if recheck else None,
                    lock=lock,
                )
            except PreconditionFailedError:
                return None
        else:
            return object.with_session(session)

    @mock_with_return(
        SyncSession.subscribe_stream,
        AsyncIterator[SubscribeEvent],
    )
    async def subscribe_stream(
        self,
        filter: str,
        *args,
        wrap_session: SessionMode | None = None,
        lock: ObjectLock = ObjectLock.SHARE,
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
                object = BaseObject.from_pb(event.object)
                if wrap_session is not None:
                    async with await self.client.session(
                        mode=wrap_session
                    ) as session:
                        object = await self._sync_sub_object(
                            session, object, filter, lock, latest, recheck
                        )
                        if object is not None:
                            yield SubscribeEvent(object, kind, session)

                else:
                    yield SubscribeEvent(object, kind)
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
        wrap_session = kwargs.get('wrap_session')
        if parallel is not None:
            kwargs['wrap_session'] = None

        async def worker():
            locks = KeyLock(Lock)
            sem = Semaphore(parallel) if parallel is not None else None
            lock = kwargs.get('lock', ObjectLock.SHARE)
            latest = kwargs.get('latest', True)
            recheck = kwargs.get('recheck', True)

            async def task(event):
                if sem is not None:
                    sem.acquire()
                id = event.object.id
                await locks.acquire(id)
                try:
                    if wrap_session is not None:
                        async with await self.client.session(
                            mode=wrap_session
                        ) as session:
                            event.session = session
                            event.object = await self._sync_sub_object(
                                event.session,
                                event.object,
                                filter,
                                lock,
                                latest,
                                recheck,
                            )
                            if event.object is not None:
                                resp = callback(event)
                                if inspect.isawaitable(resp):
                                    await resp
                    else:
                        resp = callback(event)
                        if inspect.isawaitable(resp):
                            await resp
                finally:
                    locks.release(id)
                    if sem is not None:
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

    @mock_as_coro(SyncSession.call_function)
    def call_function(self, *args, **kwargs):
        return super().call_function(*args, **kwargs)

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
