import grpc

from datetime import datetime, timezone

from novi import Client, Identity, HookPoint

_min_utc = datetime.min.replace(tzinfo=timezone.utc)


class _State:
    initialized: bool

    client: Client
    identity: Identity

    def __init__(self):
        self.initialized = False

    def ensure_init(self):
        if not self.initialized:
            raise RuntimeError('plugin API not initialized')


_state = _State()


def initialize(server: str, identity: str):
    _state.client = Client(grpc.insecure_channel(server))
    _state.identity = Identity(identity)
    _state.initialized = True


def get_client() -> Client:
    _state.ensure_init()
    return _state.client


def get_identity() -> Identity:
    _state.ensure_init()
    return _state.identity


def subs(filter: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        with _state.client.session(lock=False) as session:
            session.subscribe(filter, cb, **kwargs)

        return cb

    return decorator


def fix(filter: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        with _state.client.session(lock=False) as session:
            session.subscribe(filter, cb, checkpoint=_min_utc, **kwargs)

        return cb

    return decorator


def hook(point: HookPoint, filter: str = '*'):
    def decorator(cb):
        _state.ensure_init()
        with _state.client.session(lock=False) as session:
            session.register_hook(point, filter, cb)

        return cb

    return decorator


def function(name: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        with _state.client.session(lock=False) as session:
            session.register_function(name, cb, **kwargs)

        return cb

    return decorator
