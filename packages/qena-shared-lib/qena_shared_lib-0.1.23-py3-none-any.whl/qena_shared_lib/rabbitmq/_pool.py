from asyncio import Lock
from uuid import UUID

try:
    from pika.adapters.asyncio_connection import AsyncioConnection
except ImportError:
    pass

from ..utils import AsyncEventLoopMixin
from ._channel import BaseChannel

__all__ = ["ChannelPool"]


class ChannelPool(AsyncEventLoopMixin):
    def __init__(
        self,
        initial_pool_size: int = 50,
    ):
        self._initial_pool_size = initial_pool_size
        self._pool: dict[UUID, BaseChannel] = {}
        self._pool_lock = Lock()

    async def fill(
        self,
        connection: AsyncioConnection,
    ) -> None:
        self._connection = connection

        async with self._pool_lock:
            for _ in range(self._initial_pool_size):
                await self._add_new_channel()

    async def drain(self) -> None:
        async with self._pool_lock:
            for channel_base in self._pool.values():
                with channel_base as channel:
                    if channel.is_closing or channel.is_closed:
                        continue

                    channel.close()

            self._pool.clear()

    async def _add_new_channel(self) -> BaseChannel:
        channel = BaseChannel(
            connection=self._connection,
        )
        channel_id = await channel.open()
        self._pool[channel_id] = channel

        return channel

    async def get(self) -> BaseChannel:
        async with self._pool_lock:
            _channel_base = None

            for channel_base in self._pool.values():
                if not channel_base.healthy:
                    _ = self._pool.pop(channel_base.channel_id)

                    continue

                if not channel_base.reserved:
                    _channel_base = channel_base

                    break

            if _channel_base is None:
                _channel_base = await self._add_new_channel()

            _channel_base.reserve()

            return _channel_base

    def __len__(self) -> int:
        return len(self._pool)
