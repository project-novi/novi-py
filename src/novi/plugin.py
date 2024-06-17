import asyncio
import grpc
import inspect
import shelve
import structlog
import yaml

from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from pydantic import BaseModel

from .aio import Client as AClient
from .client import Client
from .identity import Identity
from .model import HookPoint, ObjectLock, SessionMode, SubscribeEvent
from .object import BaseObject
from .session import Session

from typing import TypeVar

_min_utc = datetime.min.replace(tzinfo=timezone.utc)

T = TypeVar('T', bound=BaseModel)


def _wrap_subscriber_cb(cb):
    @wraps(cb)
    def wrapper(event: SubscribeEvent):
        if event.session is not None:
            event.session.identity = get_identity()

        cb(event)

    return wrapper


class _State:
    initialized: bool

    identifier: str

    server: str
    client: Client
    aclient: AClient | None
    identity: Identity
    session: Session

    plugin_dir: Path
    config_template: Path | None

    tasks: list[asyncio.Task]

    def __init__(self):
        self.initialized = False

    def ensure_init(self):
        if not self.initialized:
            raise RuntimeError('plugin API not initialized')


_state = _State()


def initialize(
    identifier: str,
    server: str,
    identity: str,
    plugin_dir: Path,
    config_template: Path | None,
):
    _state.identifier = identifier
    _state.server = server

    _state.client = Client(
        grpc.insecure_channel(
            _state.server,
            options=(('grpc.default_authority', 'localhost'),),
        )
    )
    _state.aclient = None
    _state.identity = Identity(identity)
    _state.session = _state.client.temporary_session(identity=_state.identity)

    _state.plugin_dir = plugin_dir
    _state.config_template = config_template

    _state.tasks = []

    _state.initialized = True


def join():
    _state.ensure_init()
    _state.session.join()


async def ajoin():
    _state.ensure_init()
    await asyncio.gather(*_state.tasks)


def add_task(task: asyncio.Task):
    _state.ensure_init()
    _state.tasks.append(task)


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


def load_config(model: type[T]) -> T:
    config = {}

    try:
        with get_config_template_file().open() as f:
            obj = yaml.safe_load(f)
            if obj is not None:
                config.update(obj)
    except FileNotFoundError:
        pass

    try:
        with get_config_file().open() as f:
            obj = yaml.safe_load(f)
            if obj is not None:
                config.update(obj)
    except FileNotFoundError:
        pass

    return model.model_validate(config)


def get_client() -> Client:
    _state.ensure_init()
    return _state.client


def get_async_client() -> AClient:
    _state.ensure_init()
    if _state.aclient is None:
        _state.aclient = AClient(
            grpc.aio.insecure_channel(
                _state.server,
                options=(('grpc.default_authority', 'localhost'),),
            )
        )
    return _state.aclient


def get_identity() -> Identity:
    _state.ensure_init()
    return _state.identity


def new_session(*args, **kwargs) -> Session:
    return get_client().session(*args, identity=_state.identity, **kwargs)


def wrap_session(
    mode: SessionMode = SessionMode.AUTO,
    *,
    wrap_object: bool = True,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with new_session(mode=mode) as session:
                if wrap_object:

                    def wrap(obj):
                        if isinstance(obj, BaseObject):
                            return obj.with_session(session)
                        return obj

                    args = [wrap(arg) for arg in args]
                    kwargs = {k: wrap(v) for k, v in kwargs.items()}

                if 'session' in inspect.getfullargspec(func).args:
                    kwargs['session'] = session

                return func(*args, **kwargs)

        wrapper.__signature__ = inspect.signature(func)

        return wrapper

    return decorator


def subs(filter: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.subscribe(filter, _wrap_subscriber_cb(cb), **kwargs)

        return cb

    return decorator


def fix(filter: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.subscribe(
            filter,
            _wrap_subscriber_cb(cb),
            checkpoint=_min_utc,
            wrap_session=kwargs.pop('wrap_session', SessionMode.AUTO),
            parallel=kwargs.pop('parallel', 1),
            lock=kwargs.pop('lock', ObjectLock.EXCLUSIVE),
            **kwargs,
        )

        return cb

    return decorator


def core_hook(point: HookPoint, filter: str = '*'):
    def decorator(cb):
        _state.ensure_init()
        _state.session.register_core_hook(point, filter, cb)

        return cb

    return decorator


def hook(function: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.register_hook(function, cb, **kwargs)

        return cb

    return decorator


def function(name: str, **kwargs):
    def decorator(cb):
        _state.ensure_init()
        _state.session.register_function(name, cb, **kwargs)

        return cb

    return decorator


def get_logger():
    _state.ensure_init()
    return structlog.get_logger(_state.identifier)
