from typing import Any, Callable

try:
    from pika import BasicProperties
except ImportError:
    pass
from prometheus_client import Counter
from pydantic_core import to_json

from ..exceptions import RabbitMQBlockedError
from ..logging import LoggerFactory
from ._pool import ChannelPool

__all__ = ["Publisher"]


class Publisher:
    _PUBLISHED_MESSAGES = Counter(
        name="published_messages",
        documentation="Published messages",
        labelnames=["routing_key", "target"],
    )

    def __init__(
        self,
        routing_key: str,
        channel_pool: ChannelPool,
        blocked_connection_check_callback: Callable[[], bool],
        exchange: str | None = None,
        target: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        self._routing_key = routing_key
        self._exchange = exchange or ""
        self._headers = headers or {}
        self._target = target if target is not None else "__default__"

        self._headers.update({"target": self._target})

        self._channel_pool = channel_pool
        self._blocked_connection_check_callback = (
            blocked_connection_check_callback
        )
        self._logger = LoggerFactory.get_logger("rabbitmq.publisher")

    async def publish_as_arguments(self, *args: Any, **kwargs: Any) -> None:
        await self._get_channel_and_publish({"args": args, "kwargs": kwargs})

    async def publish(self, message: Any | None = None) -> None:
        await self._get_channel_and_publish(message)

    async def _get_channel_and_publish(self, message: Any) -> None:
        if self._blocked_connection_check_callback():
            raise RabbitMQBlockedError(
                "rabbitmq broker is not able to accept message right now for publishing"
            )

        with await self._channel_pool.get() as channel:
            channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._routing_key,
                body=to_json(message),
                properties=BasicProperties(
                    content_type="application/json",
                    headers=self._headers,
                ),
            )

        self._logger.debug(
            "message published to exchange `%s`, routing key `%s` and target `%s`",
            self._exchange,
            self._routing_key,
            self._target,
        )
        self._PUBLISHED_MESSAGES.labels(
            routing_key=self._routing_key, target=self._target
        ).inc()
