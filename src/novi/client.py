import grpc

from .proto import novi_pb2, novi_pb2_grpc
from .errors import handle_error
from .identity import Identity
from .session import Session

from typing import Optional


class Client:
    def __init__(self, channel: grpc.Channel):
        self._stub = novi_pb2_grpc.NoviStub(channel)
        self._active_sessions = []

    @handle_error
    def login(self, username: str, password: str) -> Identity:
        token = self._stub.Login(
            novi_pb2.LoginRequest(username=username, password=password)
        ).identity
        return Identity(token)

    @handle_error
    def session(
        self, identity: Optional[Identity] = None, lock: Optional[bool] = None
    ) -> Session:
        gen = self._stub.NewSession(
            novi_pb2.NewSessionRequest(lock=lock),
            metadata=(('identity', identity.token),) if identity else (),
        )
        token = next(gen).token
        self._active_sessions.append(gen)
        session = Session(self, token)
        session.identity = identity
        return session

    @handle_error
    def temporary_session(
        self, identity: Optional[Identity] = None
    ) -> Session:
        session = Session(self, None)
        session.identity = identity
        return session

    @handle_error
    def use_master_key(self, master_key: str) -> Identity:
        token = self._stub.UseMasterKey(
            novi_pb2.UseMasterKeyRequest(key=master_key)
        ).identity
        return Identity(token)
