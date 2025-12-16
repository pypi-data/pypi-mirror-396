from asyncio import gather
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from prometheus_client import Enum as PrometheusEnum
from punq import Container, Scope

from ..exception_handling import (
    AbstractServiceExceptionHandler,
    ExceptionHandlerServiceType,
    ExceptionHandlingManager,
)
from ..exceptions import KafkaDisconnectedError
from ..logging import LoggerFactory
from ..remotelogging import BaseRemoteLogSender
from ._consumer import (
    CONSUMER_ATTRIBUTE,
    Consumer,
    ConsumerBase,
    ConsumerConfigs,
)
from ._exception_handlers import (
    KafkaGeneralExceptionHandler,
    KafkaServiceExceptionHandler,
    KafkaValidationErrorHandler,
)
from ._producer import Producer, ProducerConfigs, ProducerManager


class SecurityProtocol(str, Enum):
    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"


class SaslMechanism(str, Enum):
    PLAIN = "PLAIN"
    GSSAPI = "GSSAPI"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512"
    OAUTHBEARER = "OAUTHBEARER"


@dataclass
class KafkaCommonConfigs:
    bootstrap_servers: str
    security_protocol: SecurityProtocol = SecurityProtocol.PLAINTEXT
    sasl_mechanism: SaslMechanism = SaslMechanism.PLAIN
    sasl_plain_username: str | None = None
    sasl_plain_password: str | None = None
    extra_consumer_configs: dict[str, Any] | None = None
    extra_producer_configs: dict[str, Any] | None = None


class KafkaManager:
    _KAFKA_CONNECTION_STATE = PrometheusEnum(
        name="kafka_connection_state",
        documentation="Kafka connection state",
        states=["connected", "disconnected"],
    )

    def __init__(
        self,
        remote_logger: BaseRemoteLogSender,
        bootstrap_servers: str,
        security_protocol: SecurityProtocol = SecurityProtocol.PLAINTEXT,
        sasl_mechanism: SaslMechanism = SaslMechanism.PLAIN,
        sasl_plain_username: str | None = None,
        sasl_plain_password: str | None = None,
        extra_consumer_configs: dict[str, Any] | None = None,
        extra_producer_configs: dict[str, Any] | None = None,
        container: Container | None = None,
    ):
        self._kafka_common_configs = KafkaCommonConfigs(
            bootstrap_servers=bootstrap_servers,
            security_protocol=security_protocol,
            sasl_mechanism=sasl_mechanism,
            sasl_plain_username=sasl_plain_username,
            sasl_plain_password=sasl_plain_password,
            extra_consumer_configs=extra_consumer_configs,
            extra_producer_configs=extra_producer_configs,
        )
        self._remote_logger = remote_logger
        self._connected = False
        self._disconnected = False
        self._container = container or Container()
        self._exception_handler = ExceptionHandlingManager(
            service_type=ExceptionHandlerServiceType.KAFKA,
            container=self._container,
            remote_logger=self._remote_logger,
            label_name=["topics", "group_id", "target", "exception"],
        )
        self._consumers: list[Consumer] = []
        self._producer_manager = ProducerManager()
        self._logger = LoggerFactory.get_logger("rabbitmq")

    @property
    def container(self) -> Container:
        return self._container

    def init_default_exception_handlers(self) -> None:
        self._exception_handler.set_exception_handlers(
            KafkaGeneralExceptionHandler,
            KafkaServiceExceptionHandler,
            KafkaValidationErrorHandler,
        )

    def include_consumer(self, consumer: Consumer | type[ConsumerBase]) -> None:
        if isinstance(consumer, Consumer):
            self._consumers.append(consumer)

            return

        if isinstance(consumer, type) and issubclass(consumer, ConsumerBase):
            self._register_consumer_classes(consumer)

            return

        raise TypeError(
            f"consumer is {type(consumer)}, expected instance of type or subclass of `ConsumerBase` or `type[ConsumerBase]`"
        )

    def set_exception_handlers(
        self, *exception_handlers: type[AbstractServiceExceptionHandler]
    ) -> None:
        self._exception_handler.set_exception_handlers(*exception_handlers)

    def _register_consumer_classes(self, consumer_class: type) -> None:
        inner_consumer = getattr(consumer_class, CONSUMER_ATTRIBUTE, None)

        if inner_consumer is None:
            raise AttributeError("consumer is not valid")

        if not isinstance(inner_consumer, Consumer):
            raise TypeError(
                f"consumer class {type(consumer_class)} is not a type `Consumer`"
            )

        self._container.register(
            service=ConsumerBase, factory=consumer_class, scope=Scope.singleton
        )

    async def connect(self) -> None:
        self._resolve_consumer_classes()
        self._exception_handler.resolve_exception_handlers()
        consumer_configs = ConsumerConfigs(
            bootstrap_servers=self._kafka_common_configs.bootstrap_servers,
            security_protocol=self._kafka_common_configs.security_protocol,
            sasl_mechanism=self._kafka_common_configs.sasl_mechanism,
            sasl_plain_username=self._kafka_common_configs.sasl_plain_username,
            sasl_plain_password=self._kafka_common_configs.sasl_plain_password,
            extra_configs=self._kafka_common_configs.extra_consumer_configs
            or {},
        )

        for consumer in self._consumers:
            await consumer.configure(
                configs=consumer_configs,
                container=self._container,
                remote_logger=self._remote_logger,
                on_exception_callback=self._exception_handler.submit_exception,
            )

        self._connected = True
        consumer_count = 0
        consumer_label = "consumer"

        if (consumer_count := len(self._consumers)) > 1:
            consumer_label = "consumers"

        self._logger.info(
            "connected to kafka, `%s` with `%d` `%s`",
            self._kafka_common_configs.bootstrap_servers,
            consumer_count,
            consumer_label,
        )
        self._KAFKA_CONNECTION_STATE.state("connected")

    async def disconnect(self) -> None:
        if self._disconnected:
            raise RuntimeError("already disconnected from kafka")

        if not self._connected:
            raise RuntimeError("not connected to kafka yet")

        self._disconnected = True

        await self._wait_for_consumers()
        self._KAFKA_CONNECTION_STATE.state("disconnected")

    async def _wait_for_consumers(self) -> None:
        _ = await gather(
            *(consumer.cancel() for consumer in self._consumers),
            return_exceptions=True,
        )

    def _resolve_consumer_classes(self) -> None:
        self._consumers.extend(
            consumer.register_consumer_methods()
            for consumer in cast(
                list[ConsumerBase], self._container.resolve_all(ConsumerBase)
            )
        )

    async def producer(
        self,
        topic: str,
        target: str | None = None,
        partition: int | None = None,
        timestamp_ms: int | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Producer:
        if not self._connected or self._disconnected:
            raise KafkaDisconnectedError("not connected to kafka yet")

        return await self._producer_manager.get_producer(
            configs=ProducerConfigs(
                bootstrap_servers=self._kafka_common_configs.bootstrap_servers,
                security_protocol=self._kafka_common_configs.security_protocol,
                sasl_mechanism=self._kafka_common_configs.sasl_mechanism,
                sasl_plain_username=self._kafka_common_configs.sasl_plain_username,
                sasl_plain_password=self._kafka_common_configs.sasl_plain_password,
                extra_configs=self._kafka_common_configs.extra_producer_configs
                or {},
            ),
            topic=topic,
            target=target or "__default__",
            partition=partition,
            timestamp_ms=timestamp_ms,
            headers=headers,
        )
