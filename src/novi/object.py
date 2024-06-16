from dataclasses import dataclass
from datetime import datetime
from tempfile import NamedTemporaryFile
from uuid import UUID

from .errors import InvalidArgumentError
from .misc import auto_map, uuid_from_pb, dt_from_timestamp, rfc3339
from .model import TagDict, TagValue, Tags
from .proto import novi_pb2

from collections.abc import Iterator
from typing import (
    BinaryIO,
    ClassVar,
    ParamSpec,
    TypeVar,
    TYPE_CHECKING,
)
from typing_extensions import Unpack

if TYPE_CHECKING:
    from .session import Session, ObjectUrlOptions, StoreFileOptions

P = ParamSpec('P')
R = TypeVar('R')


class ObjectFormat:
    FULL: ClassVar['ObjectFormat']
    BRIEF: ClassVar['ObjectFormat']

    fields: set[str]
    tags: bool | None

    def __init__(self, fmt: str):
        self.fields = set()
        self.tags = None
        for field in fmt.split(','):
            if field in ('id', 'creator', 'updated', 'created'):
                self.fields.add(field)
            elif field == 'tags':
                self.tags = True
            elif field == 'tags:brief':
                self.tags = False
            else:
                raise InvalidArgumentError(f'unknown format field: {field}')


ObjectFormat.FULL = ObjectFormat('id,creator,updated,created,tags')
ObjectFormat.BRIEF = ObjectFormat('id,creator,updated,created,tags:brief')


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
    creator: UUID | None
    created: datetime
    updated: datetime

    @classmethod
    def from_pb(cls, pb: novi_pb2.Object):
        return cls(
            id=uuid_from_pb(pb.id),
            tags={
                tag: TagValue(
                    value=tv.value if tv.HasField('value') else None,
                    updated=dt_from_timestamp(tv.updated),
                )
                for tag, tv in pb.tags.items()
            },
            creator=(
                uuid_from_pb(pb.creator) if pb.HasField('creator') else None
            ),
            created=dt_from_timestamp(pb.created),
            updated=dt_from_timestamp(pb.updated),
        )

    def dump_python(self, fmt: ObjectFormat = ObjectFormat.BRIEF) -> str:
        result = {}
        for field in fmt.fields:
            result[field] = getattr(self, field)
            if field in ('id', 'creator'):
                result[field] = (
                    None if result[field] is None else str(result[field])
                )
            elif field in ('updated', 'created'):
                result[field] = rfc3339(result[field])

        if fmt.tags is not None:
            if fmt.tags:
                # full
                result['tags'] = {
                    tag: {
                        'value': tv.value,
                        'updated': rfc3339(tv.updated),
                    }
                    for tag, tv in self.tags.items()
                }
            else:
                # brief
                result['tags'] = {
                    tag: tv.value for tag, tv in self.tags.items()
                }

        return result

    def dump_json(
        self, fmt: ObjectFormat = ObjectFormat.BRIEF, **kwargs
    ) -> str:
        import json

        # TODO: optimize
        return json.dumps(self.dump_python(fmt), ensure_ascii=False, **kwargs)

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
        obj.session = session
        return obj

    def __getitem__(self, tag: str) -> str | None:
        return self.tags[tag].value

    def has(self, tag: str) -> bool:
        return tag in self.tags

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
    session: 'Session'

    @classmethod
    def from_pb(cls, pb: novi_pb2.Object, session: 'Session'):
        obj = super().from_pb(pb)
        obj.session = session
        return obj

    def set(self, tag: str, value: str | None = None):
        return self.assign(self.session.update_object(self.id, {tag: value}))

    def update(self, tags: Tags):
        return self.assign(self.session.update_object(self.id, tags))

    def replace(self, tags: Tags, scopes: Tags | None = None):
        return self.assign(self.session.replace_object(self.id, tags, scopes))

    def delete_tag(self, tag: str):
        return self.delete_tags([tag])

    def delete_tags(self, tags: Iterator[str]):
        return self.assign(self.session.delete_object_tags(self.id, tags))

    def delete(self):
        return self.session.delete_object(self.id)

    def url(
        self, variant: str = 'original', **kwargs: Unpack['ObjectUrlOptions']
    ) -> str:
        """Returns the URL of the object files."""
        return self.session.get_object_url(self.id, variant, **kwargs)

    def open(
        self, variant: str = 'original', **kwargs: Unpack['ObjectUrlOptions']
    ) -> BinaryIO:
        """Opens the object as a file-like object."""
        return self.session.open_object(self.id, variant, **kwargs)

    def read_text(
        self,
        variant: str = 'original',
        *,
        encoding: str = 'utf-8',
        **kwargs: Unpack['ObjectUrlOptions'],
    ) -> str:
        """Reads the object's content as text."""

        with self.open(variant, **kwargs) as f:
            return f.read().decode(encoding=encoding)

    def read_bytes(
        self, variant: str = 'original', **kwargs: Unpack['ObjectUrlOptions']
    ) -> bytes:
        """Reads the object's content as bytes."""

        with self.open(variant, **kwargs) as f:
            return f.read()

    def store(
        self, variant: str = 'original', **kwargs: Unpack['StoreFileOptions']
    ):
        """Stores a file or URL as the object's content."""
        return auto_map(
            self.session.store_file(self.id, variant, **kwargs),
            lambda _: self.assign(self.session.get_object(self.id)),
        )

    def store_bytes(
        self,
        data: bytes,
        variant: str = 'original',
        **kwargs: Unpack['StoreFileOptions'],
    ):
        """Stores bytes as the object's content."""
        with NamedTemporaryFile() as f:
            f.write(data)
            f.flush()
            return self.store(variant, path=f.name, **kwargs)

    def store_text(
        self,
        text: str,
        variant: str = 'original',
        *,
        encoding: str = 'utf-8',
        **kwargs: Unpack['StoreFileOptions'],
    ):
        """Stores text as the object's content."""
        return self.store_bytes(text.encode(encoding), variant, **kwargs)


class EditableObject(BaseObject):
    pass
