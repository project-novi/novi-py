import inspect

from .model import Tags
from .proto import novi_pb2

from datetime import datetime, timezone
from uuid import UUID

from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


def dt_to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp()) * 1_000_000 + dt.microsecond


def dt_from_timestamp(ts: int) -> datetime:
    dt = datetime.fromtimestamp(ts // 1_000_000, tz=timezone.utc)
    return dt.replace(microsecond=ts % 1_000_000)


def uuid_from_pb(pb: novi_pb2.UUID) -> UUID:
    return UUID(int=pb.hi << 64 | pb.lo)


def uuid_to_pb(uuid: UUID) -> novi_pb2.UUID:
    return novi_pb2.UUID(hi=uuid.int >> 64, lo=uuid.int & (1 << 64) - 1)


def rfc3339(dt: datetime) -> str:
    return dt.isoformat()[:-6] + 'Z'


def tags_to_pb(ts: Tags) -> novi_pb2.Tags:
    tags = []
    properties = {}
    for tag, value in ts.items():
        if value is None:
            tags.append(tag)
        else:
            properties[tag] = value

    return novi_pb2.Tags(tags=tags, properties=properties)


def mock(f: Callable[P, R]) -> Callable[
    [Callable[..., R]],
    Callable[P, R],
]:
    return lambda _: _


def mock_as_coro(f: Callable[P, R]) -> Callable[
    [Callable[..., R]],
    Callable[P, Coroutine[Any, Any, R]],
]:
    return lambda _: _


def mock_with_return(f: Callable[P, Any], ret: type[R]) -> Callable[
    [Callable[..., Any]],
    Callable[P, R],
]:
    return lambda _: _


def auto_map(value, transform):
    if inspect.isawaitable(value):

        async def wrapper():
            return transform(await value)

        return wrapper()

    return transform(value)
