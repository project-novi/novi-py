import grpc

from ..errors import handle_error
from ..identity import Identity
from ..proto import novi_pb2, novi_pb2_grpc
from .session import Session

from collections.abc import Iterable


class Client:
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
        self, identity: Identity | None = None, lock: bool | None = None
    ) -> Session:
        gen = self._stub.NewSession(
            novi_pb2.NewSessionRequest(lock=lock),
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

    @handle_error
    async def check_permission(
        self,
        identity: Identity,
        permission: str | Iterable[str],
        bail: bool = True,
    ) -> bool:
        if isinstance(permission, str):
            permission = [permission]
        return (
            await self._stub.CheckPermission(
                novi_pb2.CheckPermissionRequest(
                    permissions=permission, bail=bail
                ),
                metadata=(('identity', identity.token),),
            )
        ).ok

    async def has_permission(
        self, identity: Identity, permission: str
    ) -> bool:
        return await self.check_permission(identity, permission, bail=False)
