import grpc

from .errors import PermissionDeniedError, handle_error
from .identity import Identity
from .misc import auto_map
from .model import SessionMode
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
        self,
        mode: SessionMode = SessionMode.AUTO,
        identity: Identity | None = None,
    ) -> Session:
        gen = self._stub.NewSession(
            novi_pb2.NewSessionRequest(mode=mode.value),
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
    def has_permission(
        self, identity: Identity, permission: str | Iterable[str]
    ) -> bool:
        if isinstance(permission, str):
            permission = [permission]
        return auto_map(
            self._stub.HasPermission(
                novi_pb2.HasPermissionRequest(permissions=permission),
                metadata=(('identity', identity.token),),
            ),
            lambda reply: reply.ok,
        )

    def check_permission(
        self, identity: Identity, permission: str | Iterable[str]
    ):
        def action(ok):
            if not ok:
                raise PermissionDeniedError(
                    'permission denied', {'permission': permission}
                )

        return auto_map(
            self.has_permission(identity, permission),
            action,
        )
