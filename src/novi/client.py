import grpc

from urllib.parse import urlparse
from urllib.request import urlopen

from .errors import PermissionDeniedError, handle_error
from .identity import Identity
from .misc import auto_map
from .model import SessionMode
from .proto import novi_pb2, novi_pb2_grpc
from .session import Session

from collections.abc import Callable, Iterable
from typing import TypedDict
from typing_extensions import Unpack

Resolver = Callable[[str], str]


class ResolveUrlOptions(TypedDict, total=False):
    dont_resolve: set[str] | bool | None


class Client:
    _url_resolvers: dict[str, Resolver]

    def __init__(self, channel: grpc.Channel):
        self._stub = novi_pb2_grpc.NoviStub(channel)
        self._url_resolvers = {}

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
                metadata=(('identity', identity.token),) if identity else (),
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

    def add_url_resolver(self, scheme: str, resolver: Resolver):
        self._url_resolvers[scheme] = resolver

    def remove_url_resolver(self, scheme: str):
        self._url_resolvers.pop(scheme)

    # On edit, please also edit `ResolveUrlOptions`
    def resolve_url(
        self, url: str, *, dont_resolve: set[str] | bool | None = None
    ) -> str:
        if dont_resolve is True:
            return url
        elif dont_resolve is None or dont_resolve is False:
            dont_resolve = {}

        assert isinstance(dont_resolve, set)
        scheme = urlparse(url)[0]
        try:
            return self._url_resolvers[scheme](url)
        except KeyError:
            return url

    def open_url(self, url: str, **kwargs: Unpack[ResolveUrlOptions]):
        url = self.resolve_url(url, **kwargs)
        return urlopen(url)
