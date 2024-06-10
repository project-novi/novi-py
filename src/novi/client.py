import grpc

from .errors import handle_error
from .identity import Identity
from .proto import novi_pb2, novi_pb2_grpc
from .session import Session

from collections.abc import Iterable


class Client:
    def __init__(self, channel: grpc.Channel):
        self._stub = novi_pb2_grpc.NoviStub(channel)

    @handle_error
    def login(self, username: str, password: str) -> Identity:
        token = self._stub.Login(
            novi_pb2.LoginRequest(username=username, password=password)
        ).identity
        return Identity(token)

    @handle_error
    def session(
        self, identity: Identity | None = None, lock: bool | None = None
    ) -> Session:
        gen = self._stub.NewSession(
            novi_pb2.NewSessionRequest(lock=lock),
            metadata=(('identity', identity.token),) if identity else (),
        )
        token = next(gen).token
        session = Session(self, token)
        session.identity = identity

        def read_gen():
            try:
                for resp in gen:
                    pass
            except grpc.RpcError:
                pass

        session._spawn_worker(read_gen)

        return session

    @handle_error
    def temporary_session(self, identity: Identity | None = None) -> Session:
        session = Session(self, None)
        session.identity = identity
        return session

    @handle_error
    def use_master_key(self, master_key: str) -> Identity:
        token = self._stub.UseMasterKey(
            novi_pb2.UseMasterKeyRequest(key=master_key)
        ).identity
        return Identity(token)

    @handle_error
    def check_permission(
        self,
        identity: Identity,
        permission: str | Iterable[str],
        bail: bool = True,
    ) -> bool:
        if isinstance(permission, str):
            permission = [permission]
        return self._stub.CheckPermission(
            novi_pb2.CheckPermissionRequest(permissions=permission, bail=bail),
            metadata=(('identity', identity.token),),
        ).ok

    def has_permission(self, identity: Identity, permission: str) -> bool:
        return self.check_permission(identity, permission, bail=False)
