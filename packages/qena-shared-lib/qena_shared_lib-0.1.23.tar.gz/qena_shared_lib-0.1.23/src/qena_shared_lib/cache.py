from typing import Any, TypeVar, cast

from redis.asyncio import Redis

from .alias import CamelCaseAliasedBaseModel
from .redis import RedisDependent

__all__ = [
    "CachedObject",
    "CacheManager",
]


CO = TypeVar("CO", bound="CachedObject")


class CachedObject(CamelCaseAliasedBaseModel):
    @classmethod
    def from_raw_value(
        cls, obj: Any, *args: Any, **kwargs: Any
    ) -> "CachedObject":
        cache_object = cls.model_validate_json(json_data=obj, *args, **kwargs)

        return cast(CachedObject, cache_object)

    @classmethod
    def redis_key(cls) -> str:
        return cls.__name__


class CacheManager(RedisDependent):
    def attach(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    @property
    def redis(self) -> Redis:
        return self._redis_client

    async def get(self, cached_object_type: type[CO]) -> CO | None:
        cache_object = await self._redis_client.get(
            cached_object_type.redis_key()
        )

        if cache_object is None:
            return None

        return cast(CO, cached_object_type.from_raw_value(obj=cache_object))

    async def set(self, cache_object: CachedObject) -> None:
        if not isinstance(cache_object, CachedObject):
            raise TypeError(
                f"object is not type of `CachedObject`, got `{cache_object.__class__.__name__}`"
            )

        await self._redis_client.set(
            name=cache_object.redis_key(),
            value=cache_object.model_dump_json(),
        )

    async def unset(self, cached_object_type: type[CO]) -> None:
        await self._redis_client.delete(cached_object_type.redis_key())
