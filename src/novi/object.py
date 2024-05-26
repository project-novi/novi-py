from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from . import novi_pb2
from .misc import uuid_from_pb, dt_from_timestamp

from typing import Dict, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session import Session


@dataclass
class TagValue:
    value: Optional[str]
    updated: datetime


Tags = Dict[str, Optional[str]]
TagDict = Dict[str, TagValue]


def _format_tags(tag_dict: TagDict) -> str:
    s = '{'
    tags = sorted(tag_dict.keys())
    for tag in tags:
        s += repr(tag)
        val = tag_dict[tag]
        if val.value is not None:
            if len(val.value) < 10:
                s += f': {repr(val.value)}'
            else:
                s += ': ...'

        s += ', '

    if len(tags) > 0:
        s = s[:-2]

    s += '}'
    return s


@dataclass
class BaseObject:
    id: UUID
    tags: TagDict
    creator: Optional[UUID]
    created: datetime
    updated: datetime

    @classmethod
    def from_pb(cls, pb: novi_pb2.Object):
        return cls(
            id=uuid_from_pb(pb.id),
            tags={
                tag: TagValue(value=tv.value, updated=tv.updated)
                for tag, tv in pb.tags.items()
            },
            creator=(
                uuid_from_pb(pb.creator) if pb.HasField('creator') else None
            ),
            created=dt_from_timestamp(pb.created),
            updated=dt_from_timestamp(pb.updated),
        )

    def assign(self, other: 'BaseObject'):
        self.tags = other.tags
        self.creator = other.creator
        self.created = other.created
        self.updated = other.updated

    def with_session(self, session: 'Session') -> 'Object':
        obj = Object(
            id=self.id,
            tags=self.tags,
            creator=self.creator,
            created=self.created,
            updated=self.updated,
        )
        obj._session = session
        return obj

    def __getitem__(self, tag: str) -> Optional[str]:
        return self.tags[tag].value

    def __str__(self):
        return (
            f'Object(id={self.id}, '
            f'tags={_format_tags(self.tags)}, '
            f'creator={self.creator})'
        )

    def __repr__(self):
        return (
            f'Object(id={self.id}, '
            f'tags={_format_tags(self.tags)}, '
            f'creator={self.creator}, '
            f'updated={self.updated}, '
            f'created={self.created})'
        )


class Object(BaseObject):
    _session: 'Session'

    @classmethod
    def from_pb(cls, pb: novi_pb2.Object, session: 'Session'):
        obj = super(Object, cls).from_pb(pb)
        obj._session = session
        return obj

    def set(self, tag: str, value: Optional[str] = None):
        self.assign(self._session.update_object(self.id, {tag: value}))

    def update(self, tags: Tags):
        self.assign(self._session.update_object(self.id, tags))

    def replace(self, tags: Tags, scopes: Optional[Tags] = None):
        self.assign(self._session.replace_object(self.id, tags, scopes))

    def delete_tag(self, tag: str):
        return self.delete_tags([tag])

    def delete_tags(self, tags: Iterator[str]):
        self.assign(self._session.delete_object_tags(self.id, tags))

    def delete(self):
        self._session.delete_object(self.id)


class EditableObject(BaseObject):
    pass
