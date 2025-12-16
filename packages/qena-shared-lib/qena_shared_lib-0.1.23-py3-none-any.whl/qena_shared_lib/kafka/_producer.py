from asyncio import Lock
from dataclasses import dataclass
from inspect import Traceback
from typing import Any

from aiokafka.producer import AIOKafkaProducer
from pydantic_core import to_json
from typing_extensions import Self

from ..utils import yield_now


@dataclass
class ProducerConfigs:
    bootstrap_servers: str
    security_protocol: str
    sasl_mechanism: str
    sasl_plain_username: str | None
    sasl_plain_password: str | None
    extra_configs: dict[str, Any]


class KafkaProducerContainer:
    def __init__(self, configs: ProducerConfigs) -> None:
        self._lock = Lock()
        self._kafka_producer = AIOKafkaProducer(
            bootstrap_servers=configs.bootstrap_servers,
            security_protocol=configs.security_protocol,
            sasl_mechanism=configs.sasl_mechanism,
            sasl_plain_username=configs.sasl_plain_username,
            sasl_plain_password=configs.sasl_plain_password,
            **configs.extra_configs,
        )

    @classmethod
    async def create(cls, configs: ProducerConfigs) -> "KafkaProducerContainer":
        kafka_producer_container = KafkaProducerContainer(configs)

        await kafka_producer_container.start()

        return kafka_producer_container

    async def start(self) -> None:
        await self._kafka_producer.start()

    async def aquire(self) -> None:
        await self._lock.acquire()

    def get_kafka_producer(self) -> AIOKafkaProducer:
        return self._kafka_producer

    def release(self) -> None:
        self._lock.release()


class Producer:
    def __init__(
        self,
        topic: str,
        target: str,
        partition: int | None,
        timestamp_ms: int | None,
        headers: dict[str, Any] | None,
        kafka_producer_container: KafkaProducerContainer,
    ) -> None:
        self._topic = topic
        self._partition = partition
        self._timestamp_ms = timestamp_ms
        self._headers = headers or {}
        self._headers["target"] = target
        self._kafka_producer_container = kafka_producer_container

    async def __aenter__(self) -> Self:
        await self._kafka_producer_container.aquire()

        return self

    async def send(self, key: Any, value: Any) -> None:
        await self._kafka_producer_container.get_kafka_producer().send_and_wait(
            topic=self._topic,
            key=to_json(key),
            value=to_json(value),
            partition=self._partition,
            timestamp_ms=self._timestamp_ms,
            headers=[(k, to_json(v)) for k, v in self._headers.items()],
        )

    async def __aexit__(
        self,
        exception_type: type[Exception],
        exception: Exception,
        traceback: Traceback,
    ) -> None:
        del exception_type, exception, traceback

        await yield_now()
        self._kafka_producer_container.release()


class ProducerManager:
    def __init__(self) -> None:
        self._producers: dict[str, KafkaProducerContainer] = {}

    async def get_producer(
        self,
        configs: ProducerConfigs,
        topic: str,
        target: str,
        partition: int | None,
        timestamp_ms: int | None,
        headers: dict[str, Any] | None,
    ) -> Producer:
        if not self._kafka_producer_exits(topic):
            await self._register_kafka_producer(configs=configs, topic=topic)

        kafka_producer_container = self._producers[topic]

        return Producer(
            topic=topic,
            target=target,
            partition=partition,
            timestamp_ms=timestamp_ms,
            headers=headers,
            kafka_producer_container=kafka_producer_container,
        )

    def _kafka_producer_exits(self, topic: str) -> bool:
        return topic in self._producers

    async def _register_kafka_producer(
        self, configs: ProducerConfigs, topic: str
    ) -> None:
        self._producers[topic] = await KafkaProducerContainer.create(configs)
