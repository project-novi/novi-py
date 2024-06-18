from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from typing import Any, Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .object import BaseObject
    from .session import Session

T = TypeVar('T', bound='BaseObject')


@dataclass
class TagValue:
    value: str | None
    updated: datetime


Tags = dict[str, str | None]
TagDict = dict[str, TagValue]


class SessionMode(Enum):
    AUTO = 0
    READ_ONLY = 1
    READ_WRITE = 2
    IMMEDIATE = 3


class ObjectLock(Enum):
    NONE = 0
    SHARE = 1
    EXCLUSIVE = 2

    def __str__(self):
        return self.name.lower()


class QueryOrder(Enum):
    CREATED_DESC = 0
    CREATED_ASC = 1
    UPDATED_DESC = 2
    UPDATED_ASC = 3


class HookPoint(Enum):
    BEFORE_CREATE = 0
    AFTER_CREATE = 1
    BEFORE_UPDATE = 2
    AFTER_UPDATE = 3
    BEFORE_DELETE = 4
    AFTER_DELETE = 5
    BEFORE_VIEW = 6


class EventKind(Enum):
    CREATE = 0
    UPDATE = 1
    DELETE = 2


@dataclass
class HookAction:
    update_args: bool
    result_or_args: Any

    @staticmethod
    def none():
        return HookAction(update_args=False, result_or_args=None)

    @staticmethod
    def update_result(result: dict[str, Any]):
        return HookAction(update_args=False, result_or_args=result)

    @staticmethod
    def update_arguments(args: dict[str, Any]):
        return HookAction(update_args=True, result_or_args=args)


@dataclass
class SubscribeEvent(Generic[T]):
    object: T
    kind: EventKind
    session: 'Session | None' = None
