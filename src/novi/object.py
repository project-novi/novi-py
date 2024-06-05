import shutil

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID

from .errors import InvalidArgumentError
from .file import object_path
from .misc import uuid_from_pb, dt_from_timestamp, rfc3339
from .proto import novi_pb2

from typing import (
    ClassVar,
    Dict,
    Iterator,
    Optional,
    Set,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from .session import Session


class ObjectFormat:
    FULL: ClassVar['ObjectFormat']
    BRIEF: ClassVar['ObjectFormat']

    fields: Set[str]
    tags: Optional[bool]

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
        obj._session = session
        return obj

    def __getitem__(self, tag: str) -> Optional[str]:
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

    def file_uri(self, variant: str = 'original') -> str:
        """Returns the URI of the object files."""
        return self.path(variant).resolve().as_uri()

    def path(self, variant: str = 'original', direct: bool = False) -> Path:
        """Returns the local path of the object files, will fetch the file
        from the remote storage if necessary."""
        from .errors import FileNotFoundError

        rid, rvar = str(self.id), variant
        if not direct:
            key = f'@file:{variant}'
            if not self.has(key):
                raise FileNotFoundError(
                    'missing in object meta',
                    {
                        'id': str(self.id),
                        'variant': variant,
                    },
                )

            if redirect := self[f'@file:{variant}']:
                from urllib.parse import urlparse

                url = urlparse(redirect)
                if url.scheme == 'object':
                    rid, rvar = url.netloc, (
                        'original' if len(url.path) <= 1 else url.path[1:]
                    )
                else:
                    raise FileNotFoundError(
                        'redirect not supported',
                        {
                            'id': str(self.id),
                            'variant': variant,
                        },
                    )

        return object_path(rid, rvar)

    def open(
        self,
        mode: str = 'r',
        variant: str = 'original',
        direct: bool = False,
        **kwargs,
    ):
        """Opens the object as a file-like object."""

        return self.path(variant=variant, direct=direct).open(mode, **kwargs)

    def read_text(self, **kwargs) -> str:
        """Reads the object as a text file."""

        with self.open(mode='r', **kwargs) as f:
            return f.read()

    def read_bytes(self, **kwargs) -> bytes:
        """Reads the object as a bytes file."""

        with self.open(mode='rb', **kwargs) as f:
            return f.read()

    def upload(
        self,
        data: Union[Path, bytes, str],
        move: bool = False,
        variant: str = 'original',
    ):
        """Uploads content to the object."""

        path = self.path(variant=variant, direct=True)

        if isinstance(data, Path):
            if move:
                shutil.move(data, path)
            else:
                shutil.copy(data, path)

        elif isinstance(data, bytes):
            path.write_bytes(data)

        elif isinstance(data, str):
            path.write_text(data)

        else:
            raise ValueError(f'unknown content type: {type(data)}')

        self.set(f'@file:{variant}')

    def upload_from_url(self, url: str, variant: str = 'original', **kwargs):
        from urllib.request import urlretrieve

        file, headers = urlretrieve(url)
        self.upload(Path(file), move=True, variant=variant)


class Object(BaseObject):
    _session: 'Session'

    @classmethod
    def from_pb(cls, pb: novi_pb2.Object, session: 'Session'):
        obj = super().from_pb(pb)
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
