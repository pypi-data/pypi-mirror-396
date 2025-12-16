from asyncio import Future
from inspect import Traceback
from random import uniform
from typing import cast
from uuid import UUID, uuid4

try:
    from pika.adapters.asyncio_connection import AsyncioConnection
    from pika.channel import Channel
    from pika.exceptions import ChannelClosedByClient
    from pika.spec import Basic
except ImportError:
    pass

from ..logging import LoggerFactory
from ..utils import AsyncEventLoopMixin

__all__ = ["BaseChannel"]


class BaseChannel(AsyncEventLoopMixin):
    def __init__(
        self,
        connection: AsyncioConnection,
        reopen_delay: int = 1,
        reopen_delay_jitter: tuple[float, float] = (0.0, 2.0),
        failed_reopen_threshold: int | None = 5,
    ):
        self._connection = connection
        self._reopen_delay = reopen_delay
        self._reopen_delay_jitter = reopen_delay_jitter
        self._failed_reopen_threshold = failed_reopen_threshold
        self._completion_future = self.loop.create_future()
        self._channel: Channel | None = None
        self._channel_id = uuid4()
        self._reopen_failures = 0
        self._reserved = False
        self._can_be_disposed = False
        self._logger = LoggerFactory.get_logger("rabbitmq.base_channel")

    def open(self) -> Future[UUID]:
        if self._channel is not None:
            raise RuntimeError("channel already opened")

        try:
            _ = self._connection.channel(
                channel_number=None, on_open_callback=self._on_channel_opened
            )
        except Exception as e:
            self._can_be_disposed = True

            if not self._completion_future.done():
                self._completion_future.set_exception(e)

        return self._completion_future

    def reserve(self) -> None:
        self._reserved = True

    def release(self) -> None:
        self._reserved = False

    def _on_channel_opened(self, channel: Channel) -> None:
        self._channel = channel

        try:
            self._hook_on_channel_opened()
        except Exception as e:
            if not self._completion_future.done():
                self._completion_future.set_exception(e)
            else:
                if self._channel is not None and not self.channel_closed():
                    self._channel.close()

                self._reopen()

            return

        self._channel.add_on_cancel_callback(self._on_cancelled)
        self._channel.add_on_close_callback(self._on_channel_closed)

        self._completion_future.set_result(self._channel_id)

    def _hook_on_channel_opened(self) -> None:
        pass

    def channel_closed(self) -> bool:
        if self._channel is None:
            raise RuntimeError("underlying channel not set")

        return cast(bool, self._channel.is_closing) or cast(
            bool, self._channel.is_closed
        )

    def _on_cancelled(self, method: Basic.Cancel) -> None:
        del method

        if not self._completion_future.done():
            self._completion_future.set_exception(
                RuntimeError("cancellation recieved from rabbitmq server")
            )

            return

        try:
            self._hook_on_cancelled()
        except:
            self._logger.exception("error occured on invoking cancel hook")

    def _hook_on_cancelled(self) -> None:
        pass

    def _on_channel_closed(
        self, channel: Channel, error: BaseException
    ) -> None:
        del channel

        try:
            self._hook_on_channel_closed(error)
        except:
            self._reopen_failures += 1

            return

        if not isinstance(error, ChannelClosedByClient):
            self._reopen()

    def _hook_on_channel_closed(self, error: BaseException) -> None:
        del error

    def _reopen(self) -> None:
        if (
            self._failed_reopen_threshold is not None
            and self._reopen_failures >= self._failed_reopen_threshold
        ):
            self._can_be_disposed = True

            return

        self.loop.call_later(
            delay=self._reopen_delay + uniform(*self._reopen_delay_jitter),
            callback=self._on_time_to_reopen,
        )

    def _on_time_to_reopen(self) -> None:
        if self._connection.is_closing or self._connection.is_closed:
            self._can_be_disposed = True

            return

        try:
            _ = self._connection.channel(
                channel_number=None, on_open_callback=self._on_channel_opened
            )
        except:
            self._logger.exception(
                "coudn't reopen channel %s", self._channel_id
            )
            self._reopen()

    def __enter__(self) -> Channel:
        if not self._reserved:
            self.reserve()

        if self._channel is None:
            raise RuntimeError("underlying channel not opened yet")

        return self._channel

    def __exit__(
        self,
        exception_type: type[Exception],
        exception_value: Exception,
        exception_traceback: Traceback,
    ) -> None:
        del exception_type, exception_value, exception_traceback

        self.release()

    @property
    def channel_id(self) -> UUID:
        return self._channel_id

    @property
    def healthy(self) -> bool:
        return (
            not self._can_be_disposed
            and self._channel is not None
            and not self._channel.is_closing
            and not self._channel.is_closed
        )

    @property
    def reserved(self) -> bool:
        return self._reserved

    @property
    def can_be_disposed(self) -> bool:
        return self._can_be_disposed

    @property
    def connection(self) -> AsyncioConnection:
        return self._connection

    @property
    def channel(self) -> Channel:
        if self._channel is None:
            raise RuntimeError("underlying channel not opened yet")

        return self._channel
