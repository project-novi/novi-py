from ..object import Object as SyncObject


class Object(SyncObject):
    async def assign(self, coro):
        return super().assign(await coro)

    async def read_text(self, encoding: str = 'utf-8', **kwargs) -> str:
        """Reads the object's content as text."""

        result = ''
        async with self.open(**kwargs) as f:
            async for line in f:
                result += line.decode(encoding)

        return result

    async def read_bytes(self, **kwargs) -> bytes:
        """Reads the object's content as bytes."""

        async with self.open(**kwargs) as f:
            return await f.read()
