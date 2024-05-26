from enum import Enum


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
