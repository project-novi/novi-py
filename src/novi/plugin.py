import argparse
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
        if self.initialized:
            return

        parser = argparse.ArgumentParser()
        parser.add_argument('--server', required=True)
        parser.add_argument('--identity', required=True)
        args = parser.parse_args()

        channel = grpc.insecure_channel(args.server)
        self.client = Client(channel)
        self.identity = Identity(args.identity)

        self.initialized = True


_state = _State()


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
