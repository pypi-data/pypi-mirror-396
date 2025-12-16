from abc import ABC, abstractmethod
from asyncio import (
    AbstractEventLoop,
    Future,
    Lock,
    Task,
    gather,
    iscoroutinefunction,
)
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from inspect import Parameter, signature
from random import uniform
from time import time
from types import MappingProxyType
from typing import Any, Callable, Collection, TypeVar, cast

try:
    from pika import BasicProperties
    from pika.adapters.asyncio_connection import AsyncioConnection
    from pika.channel import Channel
    from pika.frame import Method
    from pika.spec import Basic
except ImportError:
    pass
from prometheus_client import Counter, Summary
from punq import Container
from pydantic import ValidationError
from pydantic_core import from_json, to_json

from ..dependencies.miscellaneous import validate_annotation
from ..exception_handling import ServiceContext
from ..exceptions import RabbitMQBlockedError, RabbitMQServiceException
from ..logging import LoggerFactory
from ..remotelogging import BaseRemoteLogSender
from ..utils import AsyncEventLoopMixin, TypeAdapterCache
from ._channel import BaseChannel
from ._pool import ChannelPool

__all__ = [
    "BackoffRetryDelay",
    "consume",
    "CONSUMER_ATTRIBUTE",
    "Consumer",
    "execute",
    "FixedRetryDelay",
    "FlowControl",
    "LISTENER_ATTRIBUTE",
    "Listener",
    "ListenerBase",
    "ListenerContext",
    "RetryDelayJitter",
    "RetryDelayStrategy",
    "RetryPolicy",
    "RPC_WORKER_ATTRIBUTE",
    "RpcReply",
    "RpcWorker",
]


L = TypeVar("L")
DEFAULT_EXCHANGE = ""
LISTENER_ATTRIBUTE = "__rabbitmq_listener__"
CONSUMER_ATTRIBUTE = "__rabbitmq_consumer__"
RPC_WORKER_ATTRIBUTE = "__rabbitmq_rpc_worker__"


class FlowControl:
    def __init__(self, channel: Channel, loop: AbstractEventLoop):
        self._channel = channel
        self._loop = loop
        self._lock = Lock()
        self._flow_control_future: Future[None] | None = None

    async def request(self, prefetch_count: int) -> None:
        async with self._lock:
            self._flow_control_future = self._loop.create_future()

            self._channel.basic_qos(
                prefetch_count=prefetch_count,
                callback=self._on_prefetch_count_set,
            )

            await self._flow_control_future

    def _on_prefetch_count_set(self, method: Method) -> None:
        del method

        if self._flow_control_future is None:
            raise RuntimeError("flow control future not set")

        self._flow_control_future.set_result(None)


class RpcReply:
    def __init__(
        self,
        channel_pool: ChannelPool,
        reply_to: str,
        blocked_connection_check_callback: Callable[[], bool],
        correlation_id: str | None = None,
    ) -> None:
        self._channel_pool = channel_pool
        self._reply_to = reply_to
        self._blocked_connection_check_callback = (
            blocked_connection_check_callback
        )
        self._correlation_id = correlation_id
        self._replied = False

    async def reply(self, message: Any) -> None:
        base_channel = await self._channel_pool.get()
        reply_properties = BasicProperties(content_type="application/json")

        if self._correlation_id is not None:
            reply_properties.correlation_id = self._correlation_id

        if self._blocked_connection_check_callback():
            raise RabbitMQBlockedError(
                "rabbitmq broker is not able to accept message right now for manual reply"
            )

        try:
            with base_channel as channel:
                channel.basic_publish(
                    exchange=DEFAULT_EXCHANGE,
                    routing_key=self._reply_to,
                    properties=reply_properties,
                    body=to_json(message),
                )
        except:
            return

        self._replied = True

    @property
    def replied(self) -> bool:
        return self._replied


@dataclass
class ListenerContext(ServiceContext):
    queue: str
    listener_name: str
    body: bytes
    flow_control: FlowControl
    rpc_reply: RpcReply | None = None
    context_dispose_callback: Callable[..., None] | None = None

    def dispose(self) -> None:
        if self.context_dispose_callback is not None:
            self.context_dispose_callback(self)


class RetryDelayStrategy(ABC):
    @abstractmethod
    def delay(self, times_rejected: int) -> float:
        pass


@dataclass
class BackoffRetryDelay(RetryDelayStrategy):
    multiplier: float
    min: float
    max: float

    def __post_init__(self) -> None:
        if self.min > self.max:
            raise ValueError("`min` greater than `max`")

    def delay(self, times_rejected: int) -> float:
        retry_delay = self.multiplier * float(times_rejected)

        retry_delay = max(self.min, retry_delay)
        retry_delay = min(self.max, retry_delay)

        return retry_delay


@dataclass
class FixedRetryDelay(RetryDelayStrategy):
    retry_delay: float

    def delay(self, times_rejected: int) -> float:
        del times_rejected

        return self.retry_delay


@dataclass
class RetryDelayJitter:
    min: float = 0.5
    max: float = 1.0

    def __post_init__(self) -> None:
        if self.min > self.max:
            raise ValueError("`min` greater than `max`")


@dataclass
class RetryPolicy:
    exceptions: Collection[type[Exception]]
    max_retry: int
    retry_delay_strategy: RetryDelayStrategy
    retry_delay_jitter: RetryDelayJitter | None = None
    match_by_cause: bool = False

    def can_retry(self, times_rejected: int) -> bool:
        return times_rejected < self.max_retry

    def next_delay(self, times_rejected: int) -> float:
        retry_delay = self.retry_delay_strategy.delay(times_rejected)

        if self.retry_delay_jitter is not None:
            retry_delay = retry_delay + uniform(
                self.retry_delay_jitter.min, self.retry_delay_jitter.max
            )

        return retry_delay


@dataclass
class ListenerMethodContainer:
    listener_method: Callable[..., Any]
    parameters: MappingProxyType[str, Parameter]
    dependencies: dict[str, type]
    retry_policy: RetryPolicy | None = None

    def __post_init__(self) -> None:
        self._is_async_listener = iscoroutinefunction(self.listener_method)

    @property
    def is_async_listener(self) -> bool:
        return self._is_async_listener


class ListenerChannelAdapter(BaseChannel):
    def __init__(
        self,
        connection: AsyncioConnection,
        on_channel_open_callback: Callable[[Channel], None],
        on_cancel_callback: Callable[..., None],
    ) -> None:
        super().__init__(
            connection=connection,
            failed_reopen_threshold=None,
        )

        self._on_channle_open_listener_callback = on_channel_open_callback
        self._on_listener_cancel_callback = on_cancel_callback

    def _hook_on_channel_opened(self) -> None:
        self._on_channle_open_listener_callback(self.channel)

    def _hook_on_cancelled(self) -> None:
        self._on_listener_cancel_callback()


@dataclass
class ListenerMessageMetadata:
    body: bytes
    method: Basic.Deliver
    properties: BasicProperties
    listener_name: str
    listener_method_container: ListenerMethodContainer
    listener_start_time: float


class Listener(AsyncEventLoopMixin):
    _LISTENER_SUCCEEDED_COMSUMPTION = Counter(
        name="listener_succeeded_comsumption",
        documentation="Listener succeeded comsumption",
        labelnames=["queue", "listener_name"],
    )
    _LISTENER_FAILED_COMSUMPTION = Counter(
        name="listener_failed_comsumption",
        documentation="Listener failed comsumption",
        labelnames=["queue", "listener_name", "exception"],
    )
    _LISTENER_PROCESSING_LATENCY = Summary(
        name="listener_processing_latency",
        documentation="Listener processing latency",
        labelnames=["queue", "listener_name"],
    )

    def __init__(
        self,
        queue: str,
        listener_name_header_key: str,
        prefetch_count: int = 250,
        durable: bool = True,
        purge_on_startup: bool = False,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._queue = queue
        self._listener_name_header_key = listener_name_header_key
        self._prefetch_count = prefetch_count
        self._durable = durable
        self._purge_on_startup = purge_on_startup
        self._retry_policy = retry_policy
        self._listeners: dict[str, ListenerMethodContainer] = {}
        self._listeners_tasks_and_futures: list[Task[Any] | Future[Any]] = []
        self._consumer_tag: str | None = None
        self._cancelled = False
        self._logger = LoggerFactory.get_logger("rabbitmq.listener")

    @property
    def queue(self) -> str:
        return self._queue

    @property
    def listener_name_header_key(self) -> str:
        return self._listener_name_header_key

    @property
    def listeners(self) -> dict[str, ListenerMethodContainer]:
        return self._listeners

    def add_listener_method(
        self,
        listener_name: str | None,
        listener_method: Callable[..., Any],
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._register_listener_method(
            listener_name=listener_name,
            listener_method=listener_method,
            parameters=signature(listener_method).parameters,
            retry_policy=retry_policy,
        )

    def _register_listener_method(
        self,
        listener_name: str | None,
        listener_method: Callable[..., Any],
        parameters: MappingProxyType[str, Parameter],
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        listener_name = listener_name or "__default__"

        if listener_name in self._listeners:
            self._logger.warning(
                "listener with the name `%s` already exists", listener_name
            )

        dependencies = {}

        for parameter_name, parameter in parameters.items():
            if parameter.annotation is not Parameter.empty:
                if parameter.annotation is ListenerContext:
                    continue

                dependency = validate_annotation(parameter=parameter)

                if dependency is not None:
                    dependencies[parameter_name] = dependency

                    continue

                TypeAdapterCache.cache_annotation(parameter.annotation)

        self._listeners[listener_name] = ListenerMethodContainer(
            listener_method=listener_method,
            parameters=parameters,
            dependencies=dependencies,
            retry_policy=retry_policy,
        )

    async def configure(
        self,
        connection: AsyncioConnection,
        channel_pool: ChannelPool,
        on_exception_callback: Callable[[ListenerContext, BaseException], bool],
        blocked_connection_check_callback: Callable[[], bool],
        container: Container,
        remote_logger: BaseRemoteLogSender,
        global_retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._connection = connection
        self._channel_pool = channel_pool
        self._listener_future = self.loop.create_future()
        self._on_exception_callback = on_exception_callback
        self._blocked_connection_check_callback = (
            blocked_connection_check_callback
        )
        self._container = container
        self._remote_logger = remote_logger
        self._global_retry_policy = global_retry_policy
        self._listener_channel = ListenerChannelAdapter(
            connection=connection,
            on_channel_open_callback=self._on_channel_opened,
            on_cancel_callback=self._on_cancelled,
        )
        _ = await self._listener_channel.open()

        await self._listener_future

    async def cancel(self) -> None:
        self._cancelled = True

        if self._consumer_tag is not None:
            self._channel.basic_cancel(self._consumer_tag)

        _ = await gather(
            *self._listeners_tasks_and_futures, return_exceptions=True
        )

    def _on_channel_opened(self, channel: Channel) -> None:
        self._channel = channel
        self._flow_control = FlowControl(channel=self._channel, loop=self.loop)

        self._declare_queue()

    def _on_cancelled(self) -> None:
        if self._cancelled:
            return

        self._declare_queue()

    def _declare_queue(self) -> None:
        try:
            self._channel.queue_declare(
                queue=self._queue,
                durable=self._durable,
                callback=self._on_queue_declared,
            )
        except Exception as e:
            self._fail_listener(e)

    def _on_queue_declared(self, method: Method) -> None:
        del method

        if self._purge_on_startup:
            try:
                self._channel.queue_purge(
                    queue=self._queue,
                    callback=lambda _: self._set_prefetch_count(),
                )
            except Exception as e:
                self._fail_listener(e)
        else:
            self._set_prefetch_count()

    def _set_prefetch_count(self) -> None:
        try:
            self._channel.basic_qos(
                prefetch_count=self._prefetch_count,
                callback=lambda _: self._register_listener(),
            )
        except Exception as e:
            self._fail_listener(e)

    def _register_listener(self) -> None:
        try:
            self._consumer_tag = self._channel.basic_consume(
                queue=self._queue,
                auto_ack=True,
                on_message_callback=self._on_message,
            )
        except Exception as e:
            self._fail_listener(e)

            return

        if not self._listener_future.done():
            self._listener_future.set_result(None)

    def _fail_listener(self, exception: Exception) -> None:
        if not self._listener_future.done():
            self._listener_future.set_exception(exception)

        if not self._channel.is_closing or not self._channel.is_closed:
            self._channel.close()

    def _on_message(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        del channel

        if properties.headers is not None:
            listener_name = (
                properties.headers.get(self._listener_name_header_key)
                or "__default__"
            )
        else:
            listener_name = "__default__"

        if not isinstance(listener_name, str):
            listener_name = str(listener_name)

        self._logger.debug(
            "message recieved from `%s` queue for listener `%s`",
            self._queue,
            listener_name,
        )

        listener_method_container = self._listeners.get(listener_name)

        if listener_method_container is None:
            self._remote_logger.error(
                message=f"no listener registered with the name `{listener_name}` on queue `{self._queue}`",
                tags=[
                    "rabbitmq",
                    "listener_doesnt_exist",
                    self._queue,
                    listener_name,
                ],
                extra={
                    "serviceType": "rabbitmq",
                    "queue": self._queue,
                    "listenerName": listener_name,
                },
            )

            return

        self._parse_and_execute(
            ListenerMessageMetadata(
                body=body,
                method=method,
                properties=properties,
                listener_name=listener_name,
                listener_method_container=listener_method_container,
                listener_start_time=time(),
            )
        )

    def _parse_and_execute(
        self, listener_message_metadata: ListenerMessageMetadata
    ) -> None:
        try:
            listener_method_args, listener_method_kwargs = self._parse_args(
                listener_message_metadata
            )
        except Exception as e:
            self._call_exception_callback(
                exception=e,
                listener_message_metadata=listener_message_metadata,
                message=f"arguments for listener `{listener_message_metadata.listener_name}` in queue `{self._queue}` are not valid",
            )

            return

        listener_task_or_future: Task[Any] | Future[Any] | None = None

        if listener_message_metadata.listener_method_container.is_async_listener:
            listener_task_or_future = self.loop.create_task(
                listener_message_metadata.listener_method_container.listener_method(
                    *listener_method_args, **listener_method_kwargs
                )
            )
        else:
            listener_task_or_future = self.loop.run_in_executor(
                executor=None,
                func=partial(
                    listener_message_metadata.listener_method_container.listener_method,
                    *listener_method_args,
                    **listener_method_kwargs,
                ),
            )

        assert listener_task_or_future is not None

        self._listeners_tasks_and_futures.append(listener_task_or_future)
        listener_task_or_future.add_done_callback(
            partial(self._on_listener_done_executing, listener_message_metadata)
        )

    def _parse_args(
        self, listener_message_metadata: ListenerMessageMetadata
    ) -> tuple[list[Any], dict[str, Any]]:
        try:
            message = from_json(listener_message_metadata.body)
        except:
            message = listener_message_metadata.body.decode()

        assigned_args: list[Any] = []
        listener_method_args = []
        listener_method_kwargs = {}
        next_positional_arg = 0

        if isinstance(message, dict):
            args = message.get("args")
            kwargs = message.get("kwargs")

            if isinstance(args, list) and isinstance(kwargs, dict):
                for (
                    parameter_name,
                    parameter,
                ) in listener_message_metadata.listener_method_container.parameters.items():
                    dependency_key = listener_message_metadata.listener_method_container.dependencies.get(
                        parameter_name
                    )
                    dependency = None
                    listener_context = None

                    if dependency_key is not None:
                        dependency = self._container.resolve(dependency_key)

                    if parameter.annotation is not Parameter.empty and (
                        parameter.annotation is ListenerContext
                        or dependency is ListenerContext
                    ):
                        listener_context = ListenerContext(
                            queue=self._queue,
                            listener_name=listener_message_metadata.listener_name,
                            body=listener_message_metadata.body,
                            flow_control=self._flow_control,
                        )

                    if (
                        parameter.kind == Parameter.POSITIONAL_ONLY
                        or parameter.kind == Parameter.POSITIONAL_OR_KEYWORD
                    ):
                        if (
                            listener_context is not None
                            or dependency is not None
                        ):
                            listener_method_args.append(
                                listener_context or dependency
                            )
                        elif next_positional_arg < len(args):
                            listener_method_args.append(
                                self._validate_parameter(
                                    parameter=parameter,
                                    obj=args[next_positional_arg],
                                )
                            )

                            next_positional_arg += 1
                        elif parameter.name in kwargs:
                            listener_method_kwargs[parameter.name] = (
                                self._assign_kwarg(
                                    parameter=parameter,
                                    assigned_args=assigned_args,
                                    listener_context=listener_context,
                                    dependency=dependency,
                                    kwargs=kwargs,
                                )
                            )
                        elif (
                            parameter.name not in assigned_args
                            and parameter.default is Parameter.empty
                        ):
                            raise ValueError(
                                f"argument {parameter.name} has no default"
                            )
                    elif parameter.kind == Parameter.VAR_POSITIONAL:
                        listener_method_args.extend(
                            [
                                self._validate_parameter(
                                    parameter=parameter,
                                    obj=arg,
                                )
                                for arg in args[next_positional_arg:]
                            ]
                        )

                        next_positional_arg += len(args[next_positional_arg:])
                    elif parameter.kind == Parameter.KEYWORD_ONLY:
                        if (
                            listener_context is not None
                            or dependency is not None
                        ):
                            listener_method_kwargs[parameter.name] = (
                                listener_context or dependency
                            )
                        elif parameter.name in kwargs:
                            listener_method_kwargs[parameter.name] = (
                                self._assign_kwarg(
                                    parameter=parameter,
                                    assigned_args=assigned_args,
                                    listener_context=listener_context,
                                    dependency=dependency,
                                    kwargs=kwargs,
                                )
                            )
                        elif (
                            parameter.name not in assigned_args
                            and parameter.default is Parameter.empty
                        ):
                            raise ValueError(
                                f"argument {parameter.name} has no default"
                            )
                    elif parameter.kind == Parameter.VAR_KEYWORD:
                        listener_method_kwargs.update(
                            {
                                k: self._validate_parameter(
                                    parameter=parameter,
                                    obj=v,
                                )
                                for k, v in kwargs.items()
                                if k not in assigned_args
                            }
                        )

                    assigned_args.append(parameter.name)

                return listener_method_args, listener_method_kwargs

        message_consumed = False

        for (
            parameter_name,
            parameter,
        ) in listener_message_metadata.listener_method_container.parameters.items():
            dependency = listener_message_metadata.listener_method_container.dependencies.get(
                parameter_name
            )

            if parameter.annotation is not Parameter.empty and (
                parameter.annotation is ListenerContext
                or dependency is ListenerContext
            ):
                listener_method_args.append(
                    ListenerContext(
                        queue=self._queue,
                        listener_name=listener_message_metadata.listener_name,
                        body=listener_message_metadata.body,
                        flow_control=self._flow_control,
                    )
                )
            elif dependency is not None:
                listener_method_args.append(self._container.resolve(dependency))
            elif not message_consumed and message is not None:
                listener_method_args.append(
                    self._validate_parameter(
                        parameter=parameter,
                        obj=message,
                    )
                )

                message_consumed = True
            elif parameter.default is Parameter.empty:
                raise ValueError(f"argument {parameter_name} has no default")

        return listener_method_args, listener_method_kwargs

    def _assign_kwarg(
        self,
        parameter: Parameter,
        assigned_args: list[str],
        listener_context: ListenerContext | None,
        dependency: Any | None,
        kwargs: dict[str, Any],
    ) -> ListenerContext | Any:
        if parameter.name in assigned_args:
            raise KeyError(f"argument {parameter.name} already assigned")

        if listener_context is not None or dependency is not None:
            return listener_context or dependency

        return self._validate_parameter(
            parameter=parameter,
            obj=kwargs[parameter.name],
        )

    def _validate_parameter(self, parameter: Parameter, obj: Any) -> Any:
        annotation = parameter.annotation

        if annotation is Parameter.empty:
            return obj

        annotation_type_adapter = TypeAdapterCache.get_type_adapter(annotation)

        return annotation_type_adapter.validate_python(obj)

    def _on_listener_done_executing(
        self,
        listener_message_metadata: ListenerMessageMetadata,
        task_or_future: Task[Any] | Future[Any],
    ) -> None:
        if (
            not self._cancelled
            and task_or_future in self._listeners_tasks_and_futures
        ):
            self._listeners_tasks_and_futures.remove(task_or_future)

        if task_or_future.cancelled():
            return

        self._observe_listener_time(listener_message_metadata)

        exception = task_or_future.exception()

        if exception is not None:
            if listener_message_metadata.properties.reply_to is None:
                retry_policy = (
                    listener_message_metadata.listener_method_container.retry_policy
                    or self._retry_policy
                    or self._global_retry_policy
                )

                if retry_policy is not None and (
                    self._is_recoverable_exception(
                        exception=exception,
                        retry_policy_exceptions=retry_policy.exceptions,
                    )
                    or (
                        retry_policy.match_by_cause
                        and self._has_recoverable_cause(
                            exception=exception,
                            retry_policy_exceptions=retry_policy.exceptions,
                        )
                    )
                ):
                    times_rejected = None

                    if listener_message_metadata.properties.headers is not None:
                        try:
                            _times_rejected = listener_message_metadata.properties.headers.get(
                                "times_rejected"
                            )

                            if isinstance(_times_rejected, int):
                                times_rejected = _times_rejected
                            elif isinstance(
                                _times_rejected,
                                (str, bytes, bytearray, Decimal),
                            ):
                                times_rejected = int(_times_rejected)
                        except:
                            pass

                    if times_rejected is None:
                        times_rejected = 0

                    if retry_policy.can_retry(times_rejected):
                        self._reject_message(
                            listener_message_metadata=listener_message_metadata,
                            retry_policy=retry_policy,
                            times_rejected=times_rejected,
                        )

                        return

            self._call_exception_callback(
                exception=exception,
                listener_message_metadata=listener_message_metadata,
                message=f"error occured while executing listener `{listener_message_metadata.listener_name}` in queue `{self._queue}`",
            )

        if (
            listener_message_metadata.properties.reply_to is not None
            and exception is None
        ):
            self._reply_response(
                listener_message_metadata=listener_message_metadata,
                response=task_or_future.result(),
            )

        self._logger.debug(
            "message from queue `%s` consumed by listener `%s`",
            self.queue,
            listener_message_metadata.listener_name,
        )

        if exception is not None:
            self._LISTENER_FAILED_COMSUMPTION.labels(
                queue=self._queue,
                listener_name=listener_message_metadata.listener_name,
                exception=exception.__class__.__name__,
            ).inc()
        else:
            self._LISTENER_SUCCEEDED_COMSUMPTION.labels(
                queue=self._queue,
                listener_name=listener_message_metadata.listener_name,
            ).inc()

    def _observe_listener_time(
        self, listener_message_metadata: ListenerMessageMetadata
    ) -> None:
        self._LISTENER_PROCESSING_LATENCY.labels(
            queue=self._queue,
            listener_name=listener_message_metadata.listener_name,
        ).observe(listener_message_metadata.listener_start_time - time())

    def _is_recoverable_exception(
        self,
        exception: BaseException,
        retry_policy_exceptions: Collection[type[Exception]],
    ) -> bool:
        return self._in_retry_policy_exceptions(
            exception=exception, retry_policy_exceptions=retry_policy_exceptions
        )

    def _has_recoverable_cause(
        self,
        exception: BaseException,
        retry_policy_exceptions: Collection[type[Exception]],
    ) -> bool:
        cause = exception.__cause__ or exception.__context__

        while cause is not None:
            if self._in_retry_policy_exceptions(
                exception=cause,
                retry_policy_exceptions=retry_policy_exceptions,
            ):
                return True

            cause = cause.__cause__ or cause.__context__

        return False

    def _in_retry_policy_exceptions(
        self,
        exception: BaseException,
        retry_policy_exceptions: Collection[type[Exception]],
    ) -> bool:
        return any(
            exception_type in retry_policy_exceptions
            for exception_type in type(exception).mro()
        )

    def _call_exception_callback(
        self,
        exception: BaseException,
        listener_message_metadata: ListenerMessageMetadata,
        message: str | None = None,
    ) -> None:
        context_dispose_callback = None
        rpc_reply = None
        tags = [
            "rabbitmq",
            self._queue,
            listener_message_metadata.listener_name,
        ]
        extra = {
            "serviceType": "rabbitmq",
            "queue": self._queue,
            "listenerName": listener_message_metadata.listener_name,
            "section": "exceptionHandlerCallback",
            "raisedException": exception.__class__.__name__,
        }

        if listener_message_metadata.properties.reply_to is not None:

            def on_context_disposed(context: ListenerContext) -> None:
                assert listener_message_metadata.properties.reply_to is not None
                assert context.rpc_reply is not None

                if not context.rpc_reply.replied:
                    self._reply_response(
                        listener_message_metadata=listener_message_metadata,
                        response=self._reponse_from_exception(exception),
                    )

            context_dispose_callback = on_context_disposed
            rpc_reply = RpcReply(
                channel_pool=self._channel_pool,
                reply_to=listener_message_metadata.properties.reply_to,
                blocked_connection_check_callback=self._blocked_connection_check_callback,
                correlation_id=listener_message_metadata.properties.correlation_id,
            )

        try:
            exception_callback_succeeded = self._on_exception_callback(
                ListenerContext(
                    queue=self._queue,
                    listener_name=listener_message_metadata.listener_name,
                    body=listener_message_metadata.body,
                    flow_control=self._flow_control,
                    rpc_reply=rpc_reply,
                    context_dispose_callback=context_dispose_callback,
                ).set_labels(
                    {
                        "queue": self._queue,
                        "listener_name": listener_message_metadata.listener_name,
                        "exception": exception.__class__.__name__,
                    }
                ),
                exception,
            )
        except:
            tags.append("exception_callback_error")
            self._remote_logger.exception(
                message=f"error occured while invoking rabbitmq exception handler callback in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}`",
                tags=tags,
                extra=extra,
            )

            return

        if not exception_callback_succeeded:
            tags.append("exception_callback_unsuccessful")
            self._remote_logger.exception(
                message=(
                    message
                    or f"error occured while handling event in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}`"
                ),
                tags=tags,
                extra=extra,
            )

    def _reject_message(
        self,
        listener_message_metadata: ListenerMessageMetadata,
        retry_policy: RetryPolicy,
        times_rejected: int,
    ) -> None:
        message_redelivery_delay = retry_policy.next_delay(times_rejected)

        self._logger.debug(
            "message will be redelivered to listenr `%s` on queue `%s` after `%f` seconds, times redelivered `%d`",
            listener_message_metadata.listener_name,
            self._queue,
            message_redelivery_delay,
            times_rejected,
        )
        self.loop.call_later(
            delay=message_redelivery_delay,
            callback=partial(
                self._on_time_to_redeliver_message,
                listener_message_metadata,
                times_rejected,
            ),
        )

    def _on_time_to_redeliver_message(
        self,
        listener_message_metadata: ListenerMessageMetadata,
        times_rejected: int,
    ) -> None:
        self.loop.create_task(self._channel_pool.get()).add_done_callback(
            partial(
                self._on_redelivery_channel_found,
                listener_message_metadata,
                times_rejected,
            )
        )

    def _on_redelivery_channel_found(
        self,
        listener_message_metadata: ListenerMessageMetadata,
        times_rejected: int,
        task: Task[BaseChannel],
    ) -> None:
        if task.cancelled():
            return

        exception = task.exception()

        if exception is not None:
            self._call_exception_callback(
                exception=exception,
                listener_message_metadata=listener_message_metadata,
                message=f"error occured while getting channel from pool in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}` after rejecteed {times_rejected} times",
            )

            return

        headers = {
            self._listener_name_header_key: listener_message_metadata.listener_name,
            "times_rejected": times_rejected + 1,
        }

        if listener_message_metadata.properties.headers is None:
            listener_message_metadata.properties.headers = headers
        else:
            cast(
                dict[str, Any], listener_message_metadata.properties.headers
            ).update(headers)

        if self._blocked_connection_check_callback():
            self._remote_logger.error(
                message=f"couldn't redeliver message to queue `{self._queue}` and listener `{listener_message_metadata.listener_name}` due to blocked connection",
                tags=[
                    "rabbitmq",
                    "redelivery_connection_blocked",
                    self._queue,
                    listener_message_metadata.listener_name,
                ],
                extra={
                    "serviceType": "rabbitmq",
                    "queue": self._queue,
                    "listenerName": listener_message_metadata.listener_name,
                },
            )

            return

        try:
            with task.result() as channel:
                channel.basic_publish(
                    exchange=DEFAULT_EXCHANGE,
                    routing_key=self._queue,
                    body=listener_message_metadata.body,
                    properties=listener_message_metadata.properties,
                )
        except Exception as e:
            self._call_exception_callback(
                exception=e,
                listener_message_metadata=listener_message_metadata,
                message=f"error occured while sending event for redelivery in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}` after rejecteed {times_rejected} times",
            )

            return

        self._logger.debug(
            "message queued for redelivery to `%s` on queue `%s`, times redelivered `%d`",
            listener_message_metadata.listener_name,
            self._queue,
            times_rejected + 1,
        )

    def _reply_response(
        self,
        listener_message_metadata: ListenerMessageMetadata,
        response: Any,
    ) -> None:
        assert listener_message_metadata.properties.reply_to is not None

        reponse_properties = BasicProperties(content_type="application/json")

        if listener_message_metadata.properties.correlation_id is None:
            self._logger.warning(
                "`correlation_id` property not supplied for listener `%s` and queue `%s`",
                listener_message_metadata.listener_name,
                self._queue,
            )
        else:
            reponse_properties.correlation_id = (
                listener_message_metadata.properties.correlation_id
            )

        try:
            response_body = to_json(response)
        except Exception as e:
            self._call_exception_callback(
                exception=e,
                listener_message_metadata=listener_message_metadata,
                message=f"listener response is not json serializable in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}`",
            )

            return

        self.loop.create_task(self._channel_pool.get()).add_done_callback(
            partial(
                self._on_reply_channel_found,
                listener_message_metadata,
                response_body,
                reponse_properties,
            )
        )

    def _reponse_from_exception(
        self, exception: BaseException
    ) -> dict[str, Any]:
        match exception:
            case RabbitMQServiceException() as rabbitmq_exception:
                code = rabbitmq_exception.code
                message = rabbitmq_exception.message
                data = rabbitmq_exception.data
            case ValidationError() as validation_error:
                code = 0
                message = validation_error.title
                data = validation_error.json()
            case unknown_execption:
                code = 0
                message = str(unknown_execption)
                data = None

        return {
            "exception": True,
            "code": code,
            "message": message,
            "data": data,
        }

    def _on_reply_channel_found(
        self,
        listener_message_metadata: ListenerMessageMetadata,
        response_body: bytes,
        response_properties: BasicProperties,
        task: Task[BaseChannel],
    ) -> None:
        if task.cancelled():
            return

        exception = task.exception()

        if exception is not None:
            self._call_exception_callback(
                exception=exception,
                listener_message_metadata=listener_message_metadata,
                message=f"error occured while getting channel for publishing response in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}`",
            )

            return

        if self._blocked_connection_check_callback():
            self._remote_logger.error(
                message=f"couldn't repond to rpc call on queue `{self._queue}` and listener `{listener_message_metadata.listener_name}` due to blocked connection",
                tags=[
                    "rabbitmq",
                    "reply_connection_blocked",
                    self._queue,
                    listener_message_metadata.listener_name,
                ],
                extra={
                    "serviceType": "rabbitmq",
                    "queue": self._queue,
                    "listenerName": listener_message_metadata.listener_name,
                },
            )

            return

        assert listener_message_metadata.properties.reply_to is not None

        try:
            with task.result() as channel:
                channel.basic_publish(
                    exchange=DEFAULT_EXCHANGE,
                    routing_key=listener_message_metadata.properties.reply_to,
                    properties=response_properties,
                    body=response_body,
                )
        except Exception as e:
            self._call_exception_callback(
                exception=e,
                listener_message_metadata=listener_message_metadata,
                message=f"error occured while publishing response to rpc call in listener `{listener_message_metadata.listener_name}` and queue `{self._queue}`",
            )

            return

        self._logger.debug(
            "sent a reply to `%s` for request from queue `%s` and listener `%s`",
            listener_message_metadata.properties.reply_to,
            self._queue,
            listener_message_metadata.listener_name,
        )

    def __call__(self, listener: type[L]) -> type[L]:
        setattr(listener, LISTENER_ATTRIBUTE, self)

        return listener


@dataclass
class ListenerMethodMetadata:
    listener_type: type[Listener]
    listener_name: str | None = None
    retry_policy: RetryPolicy | None = None


class Consumer(Listener):
    def __init__(
        self,
        queue: str,
        prefetch_count: int = 250,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        super().__init__(
            queue=queue,
            listener_name_header_key="target",
            prefetch_count=prefetch_count,
            retry_policy=retry_policy,
        )

    def consume(
        self, target: str | None = None, retry_policy: RetryPolicy | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(consumer_method: Callable[..., Any]) -> Callable[..., Any]:
            if not callable(consumer_method):
                raise TypeError(
                    f"consumer method argument not a callable, got {type(consumer_method)}"
                )

            self._register_listener_method(
                listener_name=target,
                listener_method=consumer_method,
                parameters=signature(consumer_method).parameters,
                retry_policy=retry_policy,
            )

            return consumer_method

        return wrapper


def consumer(
    queue: str,
    prefetch_count: int = 250,
    retry_policy: RetryPolicy | None = None,
) -> Consumer:
    return Consumer(
        queue=queue,
        prefetch_count=prefetch_count,
        retry_policy=retry_policy,
    )


def consume(
    target: str | None = None, retry_policy: RetryPolicy | None = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(consumer_method: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(consumer_method):
            raise TypeError(
                f"consumer method argument not a callable, got {type(consumer_method)}"
            )

        setattr(
            consumer_method,
            CONSUMER_ATTRIBUTE,
            ListenerMethodMetadata(
                listener_type=Consumer,
                listener_name=target,
                retry_policy=retry_policy,
            ),
        )

        return consumer_method

    return wrapper


class RpcWorker(Listener):
    def __init__(self, queue: str, prefetch_count: int = 250) -> None:
        super().__init__(
            queue=queue,
            listener_name_header_key="procedure",
            prefetch_count=prefetch_count,
            purge_on_startup=True,
        )

    def execute(
        self, procedure: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(worker_method: Callable[..., Any]) -> Callable[..., Any]:
            if not callable(worker_method):
                raise TypeError(
                    f"worker method argument not a callable, got {type(worker_method)}"
                )

            self._register_listener_method(
                listener_name=procedure,
                listener_method=worker_method,
                parameters=signature(worker_method).parameters,
            )

            return worker_method

        return wrapper


def rpc_worker(queue: str, prefetch_count: int = 250) -> RpcWorker:
    return RpcWorker(queue=queue, prefetch_count=prefetch_count)


def execute(
    procedure: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(worker_method: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(worker_method):
            raise TypeError(
                f"worker method argument not a callable, got {type(worker_method)}"
            )

        setattr(
            worker_method,
            RPC_WORKER_ATTRIBUTE,
            ListenerMethodMetadata(
                listener_type=RpcWorker, listener_name=procedure
            ),
        )

        return worker_method

    return wrapper


class ListenerBase:
    _LISTENER_ATTRIBUTES = {CONSUMER_ATTRIBUTE, RPC_WORKER_ATTRIBUTE}

    def get_inner_listener(self) -> Listener:
        listener = getattr(self, LISTENER_ATTRIBUTE, None)

        if listener is None or not isinstance(listener, Listener):
            raise TypeError(
                f"{self.__class__.__name__} not a listener, possibly no annotated with either `Consumer` or `RpcWorker`"
            )

        return cast(Listener, listener)

    def register_listener_methods(self) -> Listener:
        listener = self.get_inner_listener()
        listener_method_attribute = None

        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name, None)

            if attribute is None:
                continue

            listener_method_attribute = None
            listener_method = None
            listener_method_metadata = None

            for listener_attribute in self._LISTENER_ATTRIBUTES:
                if (
                    listener_method is not None
                    and listener_method_metadata is not None
                ):
                    break

                (
                    listener_method_attribute,
                    listener_method,
                    listener_method_metadata,
                ) = self._validate_listener_method_attribute(
                    attribute=attribute,
                    listener_method_attribute=listener_attribute,
                    previous_listener_method_attribute=listener_method_attribute,
                    listener=listener,
                )

            if listener_method is None or listener_method_metadata is None:
                continue

            listener.add_listener_method(
                listener_name=listener_method_metadata.listener_name,
                listener_method=listener_method,
                retry_policy=listener_method_metadata.retry_policy,
            )

        return listener

    def _validate_listener_method_attribute(
        self,
        attribute: Any,
        listener_method_attribute: str,
        previous_listener_method_attribute: str | None,
        listener: Listener,
    ) -> tuple[
        str | None, Callable[..., Any] | None, ListenerMethodMetadata | None
    ]:
        listener_method_metadata = getattr(
            attribute, listener_method_attribute, None
        )

        if listener_method_metadata is None:
            return previous_listener_method_attribute or None, None, None

        if not isinstance(listener_method_metadata, ListenerMethodMetadata):
            raise TypeError(
                f"expected `{listener_method_attribute}` to by of type `ListenerMethodMetadata`, "
                f"got {type(listener_method_metadata)}"
            )

        if (
            previous_listener_method_attribute is not None
            and listener_method_attribute != previous_listener_method_attribute
        ):
            raise ValueError("listener methods cannot be of different type")

        if not callable(attribute):
            raise TypeError(
                f"object annotated with `{listener_method_attribute}` is not callable"
            )

        if (
            listener_method_metadata.listener_type
            not in listener.__class__.mro()
        ):
            listener_mro = ", ".join(
                map(lambda c: c.__name__, listener.__class__.mro())
            )

            raise TypeError(
                f"listener method is not correct member of `{listener_method_metadata.listener_type.__name__}`, "
                f"got `[{listener_mro}]` super classes"
            )

        return listener_method_attribute, attribute, listener_method_metadata
