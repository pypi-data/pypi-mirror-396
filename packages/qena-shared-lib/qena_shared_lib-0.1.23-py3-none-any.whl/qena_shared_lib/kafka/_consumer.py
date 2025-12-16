from asyncio import Task, gather, iscoroutinefunction
from dataclasses import dataclass
from functools import partial
from inspect import Parameter, signature
from types import MappingProxyType
from typing import Any, Callable, Generic, TypeVar, cast

try:
    from aiokafka.consumer import AIOKafkaConsumer
    from aiokafka.structs import ConsumerRecord
except ImportError:
    pass
from punq import Container
from pydantic_core import from_json

from ..dependencies.miscellaneous import validate_annotation
from ..exception_handling import ServiceContext
from ..logging import LoggerFactory
from ..remotelogging import BaseRemoteLogSender
from ..utils import AsyncEventLoopMixin, TypeAdapterCache

C = TypeVar("C")
K = TypeVar("K")
V = TypeVar("V")

DEFAULT_TARGET = "__default__"
CONSUMER_ATTRIBUTE = "__kafka_consumer__"
CONSUMER_METHOD_ATTRIBUTE = "__kafka_consumer_method__"
KEY_PARAMETER_POSITION = 1
KEY_PARAMETER_NAME = "key"
VALUE_PARAMETER_POSITION = 2
VALUE_PARAMETER_NAME = "value"


@dataclass
class ConsumerContext(ServiceContext):
    topics: list[str]
    group_id: str | None
    target: str
    key: bytes | None
    value: bytes | None


@dataclass
class ConsumerConfigs:
    bootstrap_servers: str
    security_protocol: str
    sasl_mechanism: str
    sasl_plain_username: str | None
    sasl_plain_password: str | None
    extra_configs: dict[str, Any]


@dataclass
class ConsumerMethodContainer(Generic[K, V], AsyncEventLoopMixin):
    consumer_method: Callable[..., Any]
    parameters: MappingProxyType[str, Parameter]
    key_type: type[K] | None
    value_type: type[V] | None
    dependency_types: dict[str, type[Any]]

    def __post_init__(self) -> None:
        self._is_async_consumer = iscoroutinefunction(self.consumer_method)

    async def __call__(
        self,
        key: bytes | None,
        value: bytes | None,
        container: Container,
        topics: list[str],
        target: str,
        group_id: str | None,
    ) -> Any:
        consumer_method_args, consumer_method_kwargs = self._parse_args(
            key=key,
            value=value,
            container=container,
            topics=topics,
            target=target,
            group_id=group_id,
        )

        if self._is_async_consumer:
            await self.consumer_method(
                *consumer_method_args, **consumer_method_kwargs
            )
        else:
            await self.loop.run_in_executor(
                executor=None,
                func=partial(
                    self.consumer_method,
                    *consumer_method_args,
                    **consumer_method_kwargs,
                ),
            )

    def _parse_args(
        self,
        key: bytes | None,
        value: bytes | None,
        container: Container,
        topics: list[str],
        target: str,
        group_id: str | None,
    ) -> tuple[list[Any], dict[str, Any]]:
        if key is not None:
            key = from_json(key)

        if value is not None:
            value = from_json(value)

        consumer_method_args = []
        consumer_method_kwargs = {}
        assigned_args = []

        for parameter_position, (parameter_name, parameter) in enumerate(
            iterable=self.parameters.items(), start=1
        ):
            if parameter_name in assigned_args:
                raise RuntimeError(
                    f"parameter {parameter_name} has already been assigned an argument"
                )

            arg: Any = None

            if parameter_position == KEY_PARAMETER_POSITION:
                if self.key_type is None:
                    arg = key
                else:
                    arg = self._validate_key_value(
                        object=key, object_type=self.key_type
                    )
            elif parameter_position == VALUE_PARAMETER_POSITION:
                if self.value_type is None:
                    arg = value
                else:
                    arg = self._validate_key_value(
                        object=value, object_type=self.value_type
                    )
            else:
                if parameter.annotation is Parameter.empty:
                    raise TypeError(
                        f"parameter {parameter_name} has no annotation"
                    )
                elif parameter.annotation is ConsumerContext:
                    arg = ConsumerContext(
                        topics=topics,
                        group_id=group_id,
                        target=target,
                        key=key,
                        value=value,
                    )
                else:
                    dependency_type = self.dependency_types.get(parameter_name)

                    if dependency_type is not None:
                        arg = container.resolve(dependency_type)
                    elif (
                        parameter_name not in assigned_args
                        and parameter.default is Parameter.empty
                    ):
                        raise ValueError(
                            f"parameter {parameter_name} has no default value"
                        )

            assigned_args.append(parameter_name)

            match parameter.kind:
                case (
                    Parameter.POSITIONAL_ONLY
                    | Parameter.VAR_POSITIONAL
                    | Parameter.POSITIONAL_OR_KEYWORD
                ):
                    consumer_method_args.append(arg)
                case Parameter.KEYWORD_ONLY | Parameter.VAR_KEYWORD:
                    consumer_method_kwargs[parameter_name] = arg

        return consumer_method_args, consumer_method_kwargs

    def _validate_key_value(self, object: Any, object_type: type) -> Any:
        return TypeAdapterCache.get_type_adapter(object_type).validate_python(
            object
        )


def topics_repr(topics: list[str]) -> str:
    return ", ".join(topics)


def group_id_repr(group_id: str | None) -> str:
    return group_id or "no_group_id"


class Consumer(AsyncEventLoopMixin):
    def __init__(self, topics: list[str], group_id: str | None = None) -> None:
        self._topics = topics
        self._group_id = group_id
        self._consumers: dict[str, ConsumerMethodContainer[object, object]] = {}
        self._consumers_tasks: list[Task[Any]] = []
        self._cancelled = False
        self._logger = LoggerFactory.get_logger("kafka.consumer")

    def consume(
        self, target: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(consumer_method: Callable[..., Any]) -> Callable[..., Any]:
            if not callable(consumer_method):
                raise TypeError(
                    f"consumer method argument not a callable, got {type(consumer_method)}"
                )

            self._register_consumer_method(
                target=target,
                consumer_method=consumer_method,
                parameters=signature(consumer_method).parameters,
            )

            return consumer_method

        return wrapper

    def add_consumer_method(
        self,
        target: str | None,
        consumer_method: Callable[..., Any],
    ) -> None:
        self._register_consumer_method(
            target=target,
            consumer_method=consumer_method,
            parameters=signature(consumer_method).parameters,
        )

    def _register_consumer_method(
        self,
        target: str | None,
        consumer_method: Callable[..., Any],
        parameters: MappingProxyType[str, Parameter],
    ) -> None:
        target = target or DEFAULT_TARGET

        if target in self._consumers:
            self._logger.warning(
                "consumer with a target `%s` already exists", target
            )

        key_parameter_type = None
        value_parameter_type = None
        dependency_types = {}

        for parameter_position, (parameter_name, parameter) in enumerate(
            iterable=parameters.items(), start=1
        ):
            if parameter.annotation is Parameter.empty:
                continue

            if parameter_position == KEY_PARAMETER_POSITION:
                if parameter_name != KEY_PARAMETER_NAME:
                    raise ValueError(
                        f"key parameter name is not `{KEY_PARAMETER_NAME}` got `{parameter_name}`"
                    )

                if (
                    parameter.kind is Parameter.VAR_POSITIONAL
                    or parameter.kind is Parameter.VAR_KEYWORD
                ):
                    raise TypeError(
                        "`key` cannot be variable positional or keyword parameter"
                    )

                key_parameter_type = parameter.annotation

                TypeAdapterCache.cache_annotation(key_parameter_type)
            elif parameter_position == VALUE_PARAMETER_POSITION:
                if parameter_name != VALUE_PARAMETER_NAME:
                    raise ValueError(
                        f"value parameter name is not `{VALUE_PARAMETER_NAME}` got `{parameter_name}`"
                    )

                if (
                    parameter.kind is Parameter.VAR_POSITIONAL
                    or parameter.kind is Parameter.VAR_KEYWORD
                ):
                    raise TypeError(
                        "`value` cannot be variable positional or keyword parameter"
                    )

                value_parameter_type = parameter.annotation

                TypeAdapterCache.cache_annotation(value_parameter_type)
            else:
                if parameter.annotation is ConsumerContext:
                    continue

                dependency = validate_annotation(parameter=parameter)

                if dependency is None:
                    raise TypeError(
                        f"`{parameter_name}` has unsupported parameter type annotation"
                    )

                dependency_types[parameter_name] = dependency

        self._consumers[target] = ConsumerMethodContainer(
            consumer_method=consumer_method,
            parameters=parameters,
            key_type=key_parameter_type,
            value_type=value_parameter_type,
            dependency_types=dependency_types,
        )

    async def configure(
        self,
        configs: ConsumerConfigs,
        container: Container,
        remote_logger: BaseRemoteLogSender,
        on_exception_callback: Callable[[ConsumerContext, BaseException], bool],
    ) -> None:
        self._configs = configs
        self._container = container
        self._remote_logger = remote_logger
        self._on_exception_callback = on_exception_callback
        self._kafka_consumer = AIOKafkaConsumer(
            *self._topics,
            group_id=self._group_id,
            bootstrap_servers=configs.bootstrap_servers,
            security_protocol=configs.security_protocol,
            sasl_mechanism=configs.sasl_mechanism,
            sasl_plain_username=configs.sasl_plain_username,
            sasl_plain_password=configs.sasl_plain_password,
            **configs.extra_configs,
        )

        await self._start()

    async def _start(self) -> None:
        await self._kafka_consumer.start()
        self.loop.create_task(self._start_consuming())

    async def cancel(self) -> None:
        self._cancelled = True

        await self._kafka_consumer.stop()

        _ = await gather(*self._consumers_tasks, return_exceptions=True)

    async def _start_consuming(self) -> None:
        async for consumer_record in self._kafka_consumer:
            target = self._get_target(consumer_record)
            consumer = self._get_consumer(target)

            if consumer is None:
                topics = topics_repr(self._topics)
                group_id = group_id_repr(self._group_id)

                self._remote_logger.error(
                    message=f"no consumer registered for target `{target}` on topics `{topics}` and group id `{group_id}`",
                    tags=[
                        "kafka",
                        "consumer_doesnt_exist",
                        *self._topics,
                        group_id,
                        target,
                    ],
                    extra={
                        "serviceType": "kafka",
                        "topics": topics,
                        "groupId": group_id,
                        "target": target,
                    },
                )

                continue

            self._execute(
                target=target,
                consumer=consumer,
                key=consumer_record.key,
                value=consumer_record.value,
            )

    def _get_target(self, consumer_record: ConsumerRecord) -> str:
        target = dict(consumer_record.headers).get("target")

        if target is not None:
            return cast(str, from_json(target))

        return DEFAULT_TARGET

    def _get_consumer(
        self, target: str
    ) -> ConsumerMethodContainer[object, object] | None:
        return self._consumers.get(target)

    def _execute(
        self,
        target: str,
        consumer: ConsumerMethodContainer[K, V],
        key: bytes | None,
        value: bytes | None,
    ) -> None:
        consumer_task = self.loop.create_task(
            consumer(
                key=key,
                value=value,
                container=self._container,
                topics=self._topics,
                target=target,
                group_id=self._group_id,
            )
        )

        self._consumers_tasks.append(consumer_task)
        consumer_task.add_done_callback(
            partial(
                self._consumer_done_callback,
                target=target,
                key=key,
                value=value,
            )
        )

    def _consumer_done_callback(
        self,
        task: Task[Any],
        target: str,
        key: bytes | None,
        value: bytes | None,
    ) -> None:
        if not self._cancelled and task in self._consumers_tasks:
            self._consumers_tasks.remove(task)

        if task.cancelled():
            return

        exception = task.exception()
        topics = topics_repr(self._topics)
        group_id = group_id_repr(self._group_id)

        if exception is not None:
            tags = ["kafka", "consumer_error", *self._topics, group_id, target]
            extra = {
                "serviceType": "kafka",
                "topics": topics,
                "groupId": group_id,
                "target": target,
            }

            try:
                exception_callback_succeeded = self._on_exception_callback(
                    ConsumerContext(
                        topics=self._topics,
                        group_id=self._group_id,
                        target=target,
                        key=key,
                        value=value,
                    ).set_labels(
                        {
                            "topics": topics,
                            "group_id": group_id,
                            "target": target,
                            "exception": exception.__class__.__name__,
                        }
                    ),
                    exception,
                )
            except:
                self._remote_logger.exception(
                    message=f"error occured while invoking kafka exception handler callback for target `{target}` , group id `{group_id}` and topics `{topics}`",
                    tags=tags,
                    extra=extra,
                )
            else:
                if not exception_callback_succeeded:
                    self._remote_logger.error(
                        message=f"error occured while consuming event in consumer `{target}` and for topic `{topics}` and group id `{group_id}`",
                        tags=tags,
                        extra=extra,
                        exception=exception,
                    )

            return

        self._logger.debug(
            "event from topics `%s` and group id `%s` consumed by consumer `%s`",
            topics,
            group_id,
            target,
        )

    def __call__(self, consumer: type[C]) -> type[C]:
        setattr(consumer, CONSUMER_ATTRIBUTE, self)

        return consumer


@dataclass
class ConsumerMethodMetadata:
    target: str | None = None


def consumer(
    topics: list[str],
    group_id: str | None = None,
) -> Consumer:
    return Consumer(
        topics=topics,
        group_id=group_id,
    )


def consume(
    target: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(consumer_method: Callable[..., Any]) -> Callable[..., Any]:
        if not callable(consumer_method):
            raise TypeError(
                f"consumer method argument not a callable, got {type(consumer_method)}"
            )

        setattr(
            consumer_method,
            CONSUMER_METHOD_ATTRIBUTE,
            ConsumerMethodMetadata(target=target),
        )

        return consumer_method

    return wrapper


class ConsumerBase:
    def get_inner_consumer(self) -> Consumer:
        consumer = getattr(self, CONSUMER_ATTRIBUTE, None)

        if not isinstance(consumer, Consumer):
            raise TypeError(
                f"{self.__class__.__name__} not a consumer, possibly no annotated with either `consumer`"
            )

        return consumer

    def register_consumer_methods(self) -> Consumer:
        consumer = self.get_inner_consumer()

        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name, None)

            if attribute is None:
                continue

            consumer_method_metadata = self._validate_consumer_method_attribute(
                attribute=attribute,
                consumer=consumer,
            )

            if consumer_method_metadata is None:
                continue

            consumer.add_consumer_method(
                target=consumer_method_metadata.target,
                consumer_method=attribute,
            )

        return consumer

    def _validate_consumer_method_attribute(
        self,
        attribute: Any,
        consumer: Consumer,
    ) -> ConsumerMethodMetadata | None:
        consumer_method_metadata = getattr(
            attribute, CONSUMER_METHOD_ATTRIBUTE, None
        )

        if consumer_method_metadata is None:
            return None

        if not isinstance(consumer_method_metadata, ConsumerMethodMetadata):
            raise TypeError(
                f"expected `{CONSUMER_METHOD_ATTRIBUTE}` to be of type `ConsumerMethodMetadata`, got {type(consumer_method_metadata)}"
            )

        if not callable(attribute):
            raise TypeError(
                f"object annotated with `{CONSUMER_METHOD_ATTRIBUTE}` is not callable"
            )

        if Consumer not in consumer.__class__.mro():
            consumer_mro = ", ".join(
                map(lambda c: c.__name__, consumer.__class__.mro())
            )

            raise TypeError(
                f"consumer method is not correct member of `Consumer` got `[{consumer_mro}]` super classes"
            )

        return consumer_method_metadata
