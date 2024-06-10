import aiohttp
from contextlib import _AsyncGeneratorContextManager

from ..misc import mock_as_coro, mock_with_return
from ..object import Object as SyncObject

from typing import TYPE_CHECKING
from typing_extensions import Unpack

if TYPE_CHECKING:
    from ..session import ObjectUrlOptions


class Object(SyncObject):
    async def assign(self, coro):
        return super().assign(await coro)

    @mock_as_coro(SyncObject.set)
    async def set(self, *args, **kwargs):
        return super().set(*args, **kwargs)

    @mock_as_coro(SyncObject.update)
    async def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @mock_as_coro(SyncObject.replace)
    async def replace(self, *args, **kwargs):
        return super().replace(*args, **kwargs)

    @mock_as_coro(SyncObject.delete_tag)
    async def delete_tag(self, *args, **kwargs):
        return super().delete_tag(*args, **kwargs)

    @mock_as_coro(SyncObject.delete_tags)
    async def delete_tags(self, *args, **kwargs):
        return super().delete_tags(*args, **kwargs)

    @mock_as_coro(SyncObject.delete)
    async def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @mock_as_coro(SyncObject.url)
    async def url(self, **kwargs):
        return super().url(**kwargs)

    @mock_with_return(
        SyncObject.open, _AsyncGeneratorContextManager[aiohttp.StreamReader]
    )
    def open(self, **kwargs):
        return super().open(**kwargs)

    async def read_text(
        self, *, encoding: str = 'utf-8', **kwargs: Unpack['ObjectUrlOptions']
    ) -> str:
        """Reads the object's content as text."""

        result = ''
        async with self.open(**kwargs) as f:
            async for line in f:
                result += line.decode(encoding)

        return result

    async def read_bytes(self, **kwargs: Unpack['ObjectUrlOptions']) -> bytes:
        """Reads the object's content as bytes."""

        async with self.open(**kwargs) as f:
            return await f.read()

    @mock_as_coro(SyncObject.store)
    def store(self, **kwargs):
        return super().store(**kwargs)
