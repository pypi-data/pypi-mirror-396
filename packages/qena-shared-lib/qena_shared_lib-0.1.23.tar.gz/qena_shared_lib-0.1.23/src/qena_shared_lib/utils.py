from asyncio import AbstractEventLoop, get_running_loop
from types import UnionType
from typing import Generator

from pydantic import TypeAdapter

__all__ = ["AsyncEventLoopMixin", "TypeAdapterCache"]


class AsyncEventLoopMixin:
    _LOOP: AbstractEventLoop | None = None

    @property
    def loop(self) -> AbstractEventLoop:
        if AsyncEventLoopMixin._LOOP is None:
            AsyncEventLoopMixin._LOOP = get_running_loop()

        return AsyncEventLoopMixin._LOOP

    @staticmethod
    def reset_running_loop() -> None:
        AsyncEventLoopMixin._LOOP = get_running_loop()


class TypeAdapterCache:
    _CACHE: dict[type | UnionType, TypeAdapter] = {}

    @classmethod
    def cache_annotation(cls, annotation: type | UnionType) -> None:
        if annotation not in cls._CACHE:
            cls._CACHE[annotation] = TypeAdapter(annotation)

    @classmethod
    def get_type_adapter(cls, annotation: type | UnionType) -> TypeAdapter:
        cls.cache_annotation(annotation)

        return cls._CACHE[annotation]


class YieldOnce:
    def __await__(self) -> Generator[None, None, None]:
        return (yield)


def yield_now() -> YieldOnce:
    return YieldOnce()
