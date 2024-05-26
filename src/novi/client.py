import grpc

from . import novi_pb2, novi_pb2_grpc
from .errors import handle_error
from .identity import Identity
from .session import Session

from typing import Optional


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
    def session(self, lock: Optional[bool] = True) -> Session:
        token = self._stub.NewSession(
            novi_pb2.NewSessionRequest(lock=lock),
        ).token
        return Session(self, token)

    @handle_error
    def use_master_key(self, master_key: str) -> Identity:
        token = self._stub.UseMasterKey(
            novi_pb2.UseMasterKeyRequest(key=master_key)
        ).identity
        return Identity(token)
