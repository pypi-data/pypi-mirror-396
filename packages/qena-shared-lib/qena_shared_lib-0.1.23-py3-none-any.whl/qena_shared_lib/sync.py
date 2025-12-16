from inspect import Traceback
from typing import cast

from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from typing_extensions import Self

from .redis import RedisDependent

__all__ = [
    "DistributedLockGuard",
    "DistributedLockManager",
]


class DistributedLockGuard:
    def __init__(
        self,
        distributed_lock_manager: "DistributedLockManager",
        key: str,
        blocking: bool = True,
    ):
        self._distributed_lock_manager = distributed_lock_manager
        self._key = key
        self._blocking = blocking
        self._is_acquired = False

    @property
    def is_aquired(self) -> bool:
        return self._is_acquired

    async def __aenter__(self) -> Self:
        if self._blocking:
            await self._distributed_lock_manager.acquire(self._key)
        else:
            self._is_acquired = (
                await self._distributed_lock_manager.try_acquire(self._key)
            )

        return self

    async def __aexit__(
        self,
        exception_type: type[Exception],
        exception: Exception,
        traceback: Traceback,
    ) -> None:
        del exception_type, exception, traceback

        await self._distributed_lock_manager.release(self._key)

        self._is_acquired = False


class DistributedLockManager(RedisDependent):
    def __init__(self, lock_timeout: int = 30):
        self._lock_timeout = lock_timeout
        self._lockes: dict[str, Lock] = {}

    def attach(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    async def acquire(self, key: str) -> None:
        lock = self._register_lock(key)

        await lock.acquire()

    async def try_acquire(self, key: str) -> bool:
        lock = self._register_lock(key=key, blocking=False)
        is_acquired = await lock.acquire()

        return cast(bool, is_acquired)

    def _register_lock(self, key: str, blocking: bool = True) -> Lock:
        if key not in self._lockes:
            self._lockes[key] = self._redis_client.lock(
                name=key, blocking=blocking, timeout=self._lock_timeout
            )

        return self._lockes[key]

    async def release(self, key: str) -> None:
        if key not in self._lockes or not await self._lockes[key].owned():
            return

        await self._lockes[key].release()

    def __call__(self, key: str, blocking: bool = True) -> DistributedLockGuard:
        return DistributedLockGuard(
            distributed_lock_manager=self, key=key, blocking=blocking
        )
