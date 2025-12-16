from asyncio import Future, Queue, Task, wait_for
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable, cast
from uuid import UUID, uuid4

from pika.adapters.asyncio_connection import AsyncioConnection
from pika.channel import Channel
from pika.exchange_type import ExchangeType
from pika.frame import Method
from pika.spec import Basic, BasicProperties
from pydantic_core import to_json

from qena_shared_lib.rabbitmq import (
    AbstractRabbitMQService,
    BaseChannel,
    ChannelPool,
)

from .alias import CamelCaseAliasedBaseModel
from .remotelogging import BaseRemoteLogSender
from .utils import AsyncEventLoopMixin

__all__ = [
    "Event",
    "EventBus",
    "EventBusChannelAdapter",
    "EventQueue",
    "EventReciever",
    "GlobalEvent",
]


@dataclass
class Event:
    payload: Any | None = None

    def to_json(self) -> str:
        return cast(str, to_json(self.payload).decode())


EventQueue = Queue[Event]


class GlobalEvent(CamelCaseAliasedBaseModel):
    event_key: str
    payload: Any | None = None


class EventBusChannelAdapter(BaseChannel):
    def __init__(
        self,
        connection: AsyncioConnection,
        on_event_bus_channel_opened: Callable[[Channel], None],
        on_event_bus_consumer_cancel: Callable[[], None],
    ):
        super().__init__(connection=connection, failed_reopen_threshold=None)

        self._on_event_bus_channel_opened = on_event_bus_channel_opened
        self._on_event_bus_consumer_cancel = on_event_bus_consumer_cancel

    def _hook_on_channel_opened(self) -> None:
        if not isinstance(self._channel, Channel):
            raise RuntimeError("channel not initialized")

        self._on_event_bus_channel_opened(self._channel)

    def _hook_on_cancelled(self) -> None:
        self._on_event_bus_consumer_cancel()


class EventReciever:
    def __init__(self, event_key: str) -> None:
        self._event_key = event_key
        self._event_queue = EventQueue()
        self._reciever_id = uuid4()

    @property
    def event_key(self) -> str:
        return self._event_key

    @property
    def event_queue(self) -> EventQueue:
        return self._event_queue

    @property
    def reciever_id(self) -> UUID:
        return self._reciever_id

    async def wait_once(self, timeout: float) -> Event:
        return await wait_for(fut=self._event_queue.get(), timeout=timeout)

    async def subscribe(self) -> AsyncGenerator[Event, None]:
        while True:
            yield await self._event_queue.get()


class EventBus(AbstractRabbitMQService, AsyncEventLoopMixin):
    EVENT_BUS_EXCHANGE = "event_bus"

    @classmethod
    def set_event_bus_exchange(cls, name: str) -> None:
        cls.EVENT_BUS_EXCHANGE = name

    def __init__(self, remote_logger: BaseRemoteLogSender):
        self._events: dict[str, dict[UUID, EventQueue]] = {}
        self._worker_id = uuid4()
        self._remote_logger = remote_logger
        self._first_connect = True
        self._event_reciever_tasks: list[Task[None]] = []

    def initialize(
        self, connection: AsyncioConnection, channel_pool: ChannelPool
    ) -> Future[None]:
        self._connection = connection
        self._channel_pool = channel_pool
        self._event_bus_future = self.loop.create_future()
        self._event_bus_channel_adapter = EventBusChannelAdapter(
            connection=connection,
            on_event_bus_channel_opened=self._declare_exchange,
            on_event_bus_consumer_cancel=self._register_consumer,
        )

        self._event_bus_channel_adapter.open().add_done_callback(
            self._on_event_bus_channel_open_done
        )

        return cast(Future[None], self._event_bus_future)

    def close(self) -> Future[None]:
        close_future = self.loop.create_future()

        close_future.set_result(None)

        return cast(Future[None], close_future)

    def _on_event_bus_channel_open_done(self, future: Future[UUID]) -> None:
        if future.cancelled():
            if not self._event_bus_future.done():
                self._event_bus_future.cancel()

            return

        exception = future.exception()

        if exception is not None:
            if not self._event_bus_future.done():
                self._event_bus_future.set_exception(exception)

            return

        self._event_bus_channel_id = future.result()

    def create_event_reciever(
        self,
        event_key: str,
    ) -> EventReciever:
        event_reciever = EventReciever(event_key=event_key)

        if event_key not in self._events:
            self._events[event_key] = {
                event_reciever.reciever_id: event_reciever.event_queue
            }
        else:
            self._events[event_key][event_reciever.reciever_id] = Queue()

        return event_reciever

    async def emit(
        self,
        event_key: str,
        payload: Any | None = None,
        event_reciever: EventReciever | None = None,
    ) -> None:
        await self._submit_event(
            event_key=event_key,
            event_reciever=event_reciever,
            payload=payload,
        )

    async def _submit_event(
        self,
        event_key: str,
        globally_emitted: bool = False,
        event_reciever: EventReciever | None = None,
        payload: Any | None = None,
    ) -> None:
        event = Event(payload)
        event_queues = self._events.get(event_key)

        if event_queues is None:
            if not globally_emitted:
                global_event = GlobalEvent(
                    event_key=event_key,
                    payload=payload,
                )

                await self._emit_globally(global_event)

            return

        if event_reciever is not None:
            event_queue = event_queues.get(event_reciever.reciever_id)

            if event_queue is None:
                return

            return await event_queue.put(event)

        for event_queue in event_queues.values():
            await event_queue.put(event)

    async def _emit_globally(self, global_event: GlobalEvent) -> None:
        if self._channel_pool is None:
            self._remote_logger.error(
                message="channel pool not initialized to publish to global event recievers",
                tags=["event_bus", "event_pool_not_initialized"],
            )

            return

        try:
            with await self._channel_pool.get() as channel:
                channel.basic_publish(
                    exchange=self.EVENT_BUS_EXCHANGE,
                    routing_key="IRRELEVANT",
                    body=global_event.model_dump_json().encode(),
                )
        except:
            self._remote_logger.exception(
                message="unable to publish event",
                tags=["event_bus", "global_event_publishing_error"],
            )

    async def remove(self, event_reciever: EventReciever) -> None:
        if (
            event_reciever.event_key not in self._events
            or event_reciever.reciever_id
            not in self._events[event_reciever.event_key]
        ):
            return

        del self._events[event_reciever.event_key][event_reciever.reciever_id]

        if not self._events[event_reciever.event_key]:
            del self._events[event_reciever.event_key]

    def _declare_exchange(self, channel: Channel) -> None:
        self._channel = channel

        self._channel.exchange_declare(
            exchange=self.EVENT_BUS_EXCHANGE,
            exchange_type=ExchangeType.fanout,
            auto_delete=True,
            callback=self._on_exchange_declared,
        )

    def _on_exchange_declared(self, method: Method) -> None:
        del method

        self._declare_queue()

    def _declare_queue(self) -> None:
        self._consumer_queue = self._unique_consumer_queue()

        try:
            self._channel.queue_declare(
                queue=self._consumer_queue,
                auto_delete=True,
                callback=self._on_queue_declared,
            )
        except Exception as e:
            if not self._event_bus_future.done():
                self._event_bus_future.set_exception(e)
            else:
                self._remote_logger.exception(
                    message=f"unable to declare queue {self._consumer_queue} for event bus",
                    tags=["event_bus", "queue_declaration_error"],
                )

    def _on_queue_declared(self, method: Method) -> None:
        del method

        try:
            self._channel.queue_bind(
                queue=self._consumer_queue,
                exchange=self.EVENT_BUS_EXCHANGE,
                callback=self._on_queue_bound,
            )
        except Exception as e:
            if not self._event_bus_future.done():
                self._event_bus_future.set_exception(e)
            else:
                self._remote_logger.exception(
                    message="unable to bind queue to exchange",
                    tags=["event_bus", "queue_binding_error"],
                )

    def _on_queue_bound(self, method: Method) -> None:
        del method

        self._register_consumer()

    def _register_consumer(self) -> None:
        try:
            self._channel.basic_consume(
                queue=self._consumer_queue,
                on_message_callback=self._on_message_recieved,
                auto_ack=True,
                callback=self._on_consumer_registered,
            )
        except Exception as e:
            if not self._event_bus_future.done():
                self._event_bus_future.set_exception(e)
            else:
                self._remote_logger.exception(
                    message=f"unable to start consuming {self._consumer_queue}",
                    tags=["event_bus", "consumer_registration_error"],
                )

    def _on_consumer_registered(self, method: Method) -> None:
        del method

        if not self._event_bus_future.done():
            self._event_bus_future.set_result(None)

    def _on_message_recieved(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        del channel, method, properties

        try:
            global_event = GlobalEvent.model_validate_json(body)
        except:
            self._remote_logger.exception(
                message="event not deserializable",
                tags=["event_bus", "event_deserialization_error"],
            )

            return

        event_reciever_task = self.loop.create_task(
            self._submit_event(
                event_key=global_event.event_key,
                globally_emitted=True,
                payload=global_event.payload,
            )
        )

        event_reciever_task.add_done_callback(self._on_event_emit)
        self._event_reciever_tasks.append(event_reciever_task)

    def _on_event_emit(self, task: Task[None]) -> None:
        if task in self._event_reciever_tasks:
            self._event_reciever_tasks.remove(task)

        if task.cancelled():
            return

        e = task.exception()

        if e is not None:
            self._remote_logger.error(
                message="unable to emit from global event",
                tags=["event_bus", "emit_event_error", task.get_name()],
                exception=e,
            )

    def _unique_consumer_queue(self) -> str:
        return f"{self.EVENT_BUS_EXCHANGE}.worker.{self._worker_id.hex}"
