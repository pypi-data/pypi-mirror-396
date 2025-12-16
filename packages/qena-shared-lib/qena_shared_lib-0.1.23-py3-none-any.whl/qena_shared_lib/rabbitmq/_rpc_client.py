from asyncio import Future, Lock
from functools import partial
from importlib import import_module
from time import time
from types import UnionType
from typing import Any, Callable, Generic, TypeVar
from uuid import uuid4

try:
    from pika import BasicProperties
    from pika.channel import Channel
    from pika.frame import Method
    from pika.spec import Basic
except ImportError:
    pass
from prometheus_client import Counter, Summary
from pydantic_core import from_json, to_json

from ..exceptions import (
    RabbitMQBlockedError,
    RabbitMQRpcRequestPendingError,
    RabbitMQRpcRequestTimeoutError,
    RabbitMQServiceException,
)
from ..logging import LoggerFactory
from ..utils import AsyncEventLoopMixin, TypeAdapterCache
from ._pool import ChannelPool

__all__ = ["RpcClient"]


class ExitHandler:
    _EXITING = False
    _RPC_FUTURES: list[Future[Any]] = []
    _ORIGINAL_EXIT_HANDLER: Callable[..., None]

    @classmethod
    def is_exising(cls) -> bool:
        return cls._EXITING

    @classmethod
    def add_rpc_future(cls, rpc_future: Future[Any]) -> None:
        cls._RPC_FUTURES.append(rpc_future)

    @classmethod
    def remove_rpc_future(cls, rpc_future: Future[Any]) -> None:
        try:
            cls._RPC_FUTURES.remove(rpc_future)
        except:
            pass

    @classmethod
    def cancel_futures(cls) -> None:
        cls._EXITING = True

        for rpc_future in cls._RPC_FUTURES:
            if not rpc_future.done():
                rpc_future.cancel()

    @staticmethod
    def patch_exit_handler() -> None:
        try:
            Server = import_module("uvicorn.server").Server
        except ModuleNotFoundError:
            return

        ExitHandler._ORIGINAL_EXIT_HANDLER = Server.handle_exit
        Server.handle_exit = ExitHandler.handle_exit

    @staticmethod
    def notify_clients() -> None:
        ExitHandler.cancel_futures()

    @staticmethod
    def handle_exit(*args: Any, **kwargs: Any) -> None:
        ExitHandler.notify_clients()
        ExitHandler._ORIGINAL_EXIT_HANDLER(*args, **kwargs)


ExitHandler.patch_exit_handler()


R = TypeVar("R")


class RpcClient(Generic[R], AsyncEventLoopMixin):
    _SUCCEEDED_RPC_CALLS = Counter(
        name="succeeded_rpc_calls",
        documentation="RPC calls made",
        labelnames=["routing_key", "procedure"],
    )
    _FAILED_RPC_CALL = Counter(
        name="failed_rpc_call",
        documentation="Failed RPC calls",
        labelnames=["routing_key", "procedure", "exception"],
    )
    _RPC_CALL_LATENCY = Summary(
        name="rpc_call_latency",
        documentation="Time it took for RPC calls",
        labelnames=["routing_key", "procedure"],
    )

    def __init__(
        self,
        routing_key: str,
        channel_pool: ChannelPool,
        blocked_connection_check_callback: Callable[[], bool],
        exchange: str | None = None,
        procedure: str | None = None,
        headers: dict[str, str] | None = None,
        return_type: type[R] | UnionType | None = None,
        timeout: float = 15,
    ):
        self._routing_key = routing_key
        self._exchange = exchange or ""
        self._headers = headers or {}
        self._procedure = procedure if procedure is not None else "__default__"

        self._headers.update({"procedure": self._procedure})

        self._return_type = return_type
        self._timeout = timeout
        self._channel_pool = channel_pool
        self._blocked_connection_check_callback = (
            blocked_connection_check_callback
        )
        self._rpc_future: Future[R] | None = None
        self._rpc_call_start_time: float | None = None
        self._rpc_call_lock = Lock()
        self._rpc_call_pending = False
        self._logger = LoggerFactory.get_logger("rabbitmq.rpc_client")

    async def call_with_arguments(self, *args: Any, **kwargs: Any) -> R:
        return await self._get_channel_and_call(
            ({"args": args, "kwargs": kwargs})
        )

    async def call(self, message: Any | None = None) -> R:
        return await self._get_channel_and_call(message)

    async def _get_channel_and_call(self, message: Any) -> R:
        if self._blocked_connection_check_callback():
            raise RabbitMQBlockedError(
                "rabbitmq broker is not able to accept message right now for rpc call"
            )

        async with self._rpc_call_lock:
            if self._rpc_call_pending:
                raise RabbitMQRpcRequestPendingError(
                    "previous rpc request not done yet"
                )

            self._rpc_call_pending = True

        self._rpc_call_start_time = time()
        self._channel_base = await self._channel_pool.get()
        self._channel = self._channel_base.channel
        self._rpc_future = self.loop.create_future()

        ExitHandler.add_rpc_future(self._rpc_future)
        self._channel.queue_declare(
            queue="",
            exclusive=True,
            auto_delete=True,
            callback=partial(self._on_queue_declared, message),
        )

        return await self._rpc_future

    def _on_queue_declared(self, message: Any, method: Method) -> None:
        queue = getattr(method.method, "queue")

        try:
            self._rpc_reply_consumer_tag = self._channel.basic_consume(
                queue=queue,
                on_message_callback=self._on_reply_message,
                auto_ack=True,
            )
        except Exception as e:
            self._finalize_call(exception=e)

            return

        self._correlation_id = str(uuid4())

        try:
            self._channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._routing_key,
                properties=BasicProperties(
                    content_type="application/json",
                    reply_to=queue,
                    correlation_id=self._correlation_id,
                    headers=self._headers,
                ),
                body=to_json(message),
            )
        except Exception as e:
            self._finalize_call(exception=e)

            return

        if self._timeout > 0:
            self._timeout_timer_handle = self.loop.call_later(
                delay=self._timeout, callback=self._on_timeout
            )

        self._logger.debug(
            "rpc request sent to exchange `%s`, routing key `%s` and procedure `%s`",
            self._exchange,
            self._routing_key,
            self._procedure,
        )

    def _on_timeout(self) -> None:
        self._finalize_call(
            exception=RabbitMQRpcRequestTimeoutError(
                f"rpc worker didn't responed in a timely manner within `{self._timeout}` seconds"
            )
        )

    def _on_reply_message(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        del channel, method

        if properties.correlation_id != self._correlation_id:
            self._finalize_call(
                exception=ValueError(
                    f"correlation id {properties.correlation_id} from rpc worker doesn't match {self._correlation_id}"
                )
            )

            return

        try:
            response = from_json(body)
        except Exception as e:
            self._finalize_call(exception=e)

            return

        if isinstance(response, dict) and "exception" in response:
            self._finalize_call(
                exception=RabbitMQServiceException(
                    code=response.get("code") or 0,
                    message=response.get("message")
                    or "unknown error occured from the rpc worker side",
                )
            )

        if self._return_type is not None:
            type_adapter = TypeAdapterCache.get_type_adapter(self._return_type)

            try:
                response = type_adapter.validate_python(response)
            except Exception as e:
                self._finalize_call(exception=e)

                return

        self._finalize_call(response=response)

    def _finalize_call(
        self,
        response: Any = None,
        exception: BaseException | None = None,
    ) -> None:
        if not self._timeout_timer_handle.cancelled():
            self._timeout_timer_handle.cancel()

        self._rpc_call_pending = False
        self._channel.basic_cancel(self._rpc_reply_consumer_tag)
        self._channel_base.release()

        if self._rpc_future is None:
            return

        ExitHandler.remove_rpc_future(self._rpc_future)

        if self._rpc_future.done():
            return
        elif exception is not None:
            self._rpc_future.set_exception(exception)
            self._FAILED_RPC_CALL.labels(
                routing_key=self._routing_key,
                procedure=self._procedure,
                exception=exception.__class__.__name__,
            ).inc()
        else:
            self._rpc_future.set_result(response)
            self._SUCCEEDED_RPC_CALLS.labels(
                routing_key=self._routing_key, procedure=self._procedure
            ).inc()

        self._RPC_CALL_LATENCY.labels(
            routing_key=self._routing_key, procedure=self._procedure
        ).observe((self._rpc_call_start_time or time()) - time())
