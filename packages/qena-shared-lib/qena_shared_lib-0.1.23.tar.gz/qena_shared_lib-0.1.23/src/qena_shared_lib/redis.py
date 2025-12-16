from abc import ABC, abstractmethod
from inspect import isawaitable

from redis.asyncio import ConnectionPool, Redis

from .logging import LoggerFactory

__all__ = [
    "RedisDependent",
    "RedisManager",
]


class RedisDependent(ABC):
    @abstractmethod
    def attach(self, redis_client: Redis) -> None:
        pass


class RedisManager:
    def __init__(self, url: str):
        self._logger = LoggerFactory.get_logger("redis")
        self._redis_dependents: set[RedisDependent] = set()
        self._url = url

    async def connect(self) -> None:
        self._redis_connection_pool = ConnectionPool.from_url(self._url)
        self._redis_client = Redis.from_pool(self._redis_connection_pool)

        response = self._redis_client.ping()

        if isawaitable(response):
            await response

        for redis_dependent in self._redis_dependents:
            redis_dependent.attach(self._redis_client)

        self._logger.info("connected to redis")

    async def disconnect(self) -> None:
        await self._redis_connection_pool.aclose()
        self._logger.info("disconnected from redis")

    def add(self, redis_dependent: RedisDependent) -> "RedisManager":
        self._redis_dependents.add(redis_dependent)

        return self
