import grpc

from ..client import Client as SyncClient
from ..errors import handle_error
from ..identity import Identity
from ..misc import mock_as_coro
from ..model import SessionMode
from ..proto import novi_pb2, novi_pb2_grpc
from .session import Session


class Client(SyncClient):
    def __init__(self, channel: grpc.aio.Channel):
        self._stub = novi_pb2_grpc.NoviStub(channel)

    @handle_error
    async def login(self, username: str, password: str) -> Identity:
        token = (
            await self._stub.Login(
                novi_pb2.LoginRequest(username=username, password=password)
            )
        ).identity
        return Identity(token)

    @handle_error
    async def session(
        self,
        mode: SessionMode = SessionMode.AUTO,
        identity: Identity | None = None,
    ) -> Session:
        gen = self._stub.NewSession(
            novi_pb2.NewSessionRequest(mode=mode.value),
            metadata=(('identity', identity.token),) if identity else (),
        )
        token = (await gen.read()).token
        session = Session(self, token)
        session.identity = identity

        async def read_gen():
            try:
                while True:
                    if await gen.read() is None:
                        break
            except grpc.RpcError:
                pass

        session._spawn_task(read_gen())

        return session

    @handle_error
    def temporary_session(self, identity: Identity | None = None) -> Session:
        session = Session(self, None)
        session.identity = identity
        return session

    @handle_error
    async def use_master_key(self, master_key: str) -> Identity:
        token = (
            await self._stub.UseMasterKey(
                novi_pb2.UseMasterKeyRequest(key=master_key)
            )
        ).identity
        return Identity(token)

    @mock_as_coro(SyncClient.has_permission)
    def has_permission(self, *args, **kwargs):
        return super().has_permission(*args, **kwargs)

    @mock_as_coro(SyncClient.check_permission)
    def check_permission(self, *args, **kwargs):
        return super().check_permission(*args, **kwargs)
