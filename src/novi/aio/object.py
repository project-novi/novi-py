import aiohttp

from contextlib import _AsyncGeneratorContextManager, asynccontextmanager

from ..client import ResolveUrlOptions
from ..misc import mock_as_coro, mock_with_return
from ..object import Object as SyncObject

from typing_extensions import Unpack


class Object(SyncObject):
    async def assign(self, coro):
        return super().assign(await coro)

    @mock_as_coro(SyncObject.sync)
    def sync(self, *args, **kwargs):
        return super().sync(*args, **kwargs)

    @mock_as_coro(SyncObject.set)
    def set(self, *args, **kwargs):
        return super().set(*args, **kwargs)

    @mock_as_coro(SyncObject.update)
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

    @mock_as_coro(SyncObject.replace)
    def replace(self, *args, **kwargs):
        return super().replace(*args, **kwargs)

    @mock_as_coro(SyncObject.delete_tag)
    def delete_tag(self, *args, **kwargs):
        return super().delete_tag(*args, **kwargs)

    @mock_as_coro(SyncObject.delete_tags)
    def delete_tags(self, *args, **kwargs):
        return super().delete_tags(*args, **kwargs)

    @mock_as_coro(SyncObject.delete)
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @asynccontextmanager
    @mock_with_return(
        SyncObject.open, _AsyncGeneratorContextManager[aiohttp.StreamReader]
    )
    def open(self, *args, **kwargs):
        return super().open(*args, **kwargs)

    async def read_text(
        self,
        variant: str = 'original',
        *,
        encoding: str = 'utf-8',
        **kwargs: Unpack[ResolveUrlOptions],
    ) -> str:
        """Reads the object's content as text."""

        result = ''
        async with self.open(variant, **kwargs) as f:
            async for line in f:
                result += line.decode(encoding)

        return result

    async def read_bytes(
        self, variant: str = 'original', **kwargs: Unpack[ResolveUrlOptions]
    ) -> bytes:
        """Reads the object's content as bytes."""

        async with self.open(variant, **kwargs) as f:
            return await f.read()

    @mock_as_coro(SyncObject.store)
    def store(self, *args, **kwargs):
        return super().store(*args, **kwargs)

    @mock_as_coro(SyncObject.store_bytes)
    def store_bytes(self, *args, **kwargs):
        return super().store_bytes(*args, **kwargs)

    @mock_as_coro(SyncObject.store_text)
    def store_text(self, *args, **kwargs):
        return super().store_text(*args, **kwargs)
