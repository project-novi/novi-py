import grpc
import inspect
import shelve
import yaml

from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from pydantic import BaseModel

from novi import BaseObject, Client, Identity, HookPoint, Session

from typing import Optional, Type, TypeVar

_min_utc = datetime.min.replace(tzinfo=timezone.utc)

T = TypeVar('T', bound=BaseModel)


class _State:
    initialized: bool

    client: Client
    identity: Identity
    session: Session

    plugin_dir: Path
    config_template: Optional[Path]

    def __init__(self):
        self.initialized = False

    def ensure_init(self):
        if not self.initialized:
            raise RuntimeError('plugin API not initialized')


_state = _State()


def initialize(
    server: str,
    identity: str,
    plugin_dir: Path,
    config_template: Optional[Path],
):
    _state.client = Client(
        grpc.insecure_channel(
            server, options=(('grpc.default_authority', 'localhost'),)
        )
    )
    _state.identity = Identity(identity)
    _state.session = _state.client.session(identity=_state.identity)

    _state.plugin_dir = plugin_dir
    _state.config_template = config_template

    _state.initialized = True


def join():
    _state.ensure_init()
    _state.session.join()


def get_plugin_dir() -> Path:
    _state.ensure_init()
    return _state.plugin_dir


def get_data_dir() -> Path:
    path = get_plugin_dir() / 'data'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir() -> Path:
    path = get_plugin_dir() / 'cache'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_dir() -> Path:
    path = get_plugin_dir() / 'db'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db(name: str) -> shelve.Shelf:
    from dbm import gnu

    db = gnu.open(str(get_db_dir() / f'{name}.db'))
    return shelve.Shelf(db)


def get_config_file() -> Path:
    return get_plugin_dir() / 'config.yaml'


def get_config_template_file() -> Path:
    _state.ensure_init()
    return _state.config_template


def load_config(model: Type[T]) -> T:
    config = {}

    try:
        with get_config_template_file().open() as f:
            config.update(yaml.safe_load(f))
    except FileNotFoundError:
        pass

    try:
        with get_config_file().open() as f:
            config.update(yaml.safe_load(f))
    except FileNotFoundError:
        pass

    return model.model_validate(config)


def get_client() -> Client:
    _state.ensure_init()
    return _state.client


def get_identity() -> Identity:
    _state.ensure_init()
    return _state.identity


def new_session(**kwargs) -> Session:
    _state.ensure_init()
    return _state.client.session(identity=_state.identity, **kwargs)


def wrap_session(
    wrap_object: bool = True,
    append_session: bool = True,
    lock: Optional[bool] = True,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with new_session(lock=lock) as session:
                if wrap_object:

                    def wrap(obj):
                        if isinstance(obj, BaseObject):
                            return obj.with_session(session)
                        return obj

                    args = [wrap(arg) for arg in args]
                    kwargs = {k: wrap(v) for k, v in kwargs.items()}

                if append_session:
                    kwargs['session'] = session

                return func(*args, **kwargs)

        wrapper.__signature__ = inspect.signature(func)

        return wrapper

    return decorator


def subs(filter: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.subscribe(filter, cb, **kwargs)

        return cb

    return decorator


def fix(filter: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.subscribe(filter, cb, checkpoint=_min_utc, **kwargs)

        return cb

    return decorator


def hook(point: HookPoint, filter: str = '*'):
    def decorator(cb):
        _state.ensure_init()
        _state.session.register_hook(point, filter, cb)

        return cb

    return decorator


def function(name: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.register_function(name, cb, **kwargs)

        return cb

    return decorator
