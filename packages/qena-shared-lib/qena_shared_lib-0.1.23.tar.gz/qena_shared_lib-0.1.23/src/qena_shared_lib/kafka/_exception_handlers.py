from pydantic import ValidationError

from ..exception_handling import (
    ExceptionHandlerServiceType,
    GeneralExceptionHandler,
    ServiceExceptionHandler,
    ServiceInformation,
    ValidationErrorHandler,
)
from ..exceptions import ServiceException
from ..logging import LoggerFactory
from ..remotelogging import BaseRemoteLogSender
from ._consumer import ConsumerContext, group_id_repr, topics_repr

__all__ = [
    "KafkaServiceExceptionHandler",
    "KafkaValidationErrorHandler",
    "KafkaGeneralExceptionHandler",
]

KAFKA_EXCEPTION_HANDLER_LOGGER_NAME = "kafka.exception_handler"


class KafkaServiceExceptionHandler(ServiceExceptionHandler):
    def __init__(self, remote_logger: BaseRemoteLogSender):
        super().__init__(remote_logger)

        self._logger = LoggerFactory.get_logger(
            KAFKA_EXCEPTION_HANDLER_LOGGER_NAME
        )

    def __call__(
        self,
        context: ConsumerContext,
        exception: ServiceException,
    ) -> None:
        topics = topics_repr(context.topics)
        group_id = group_id_repr(context.group_id)

        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.KAFKA,
                tags=[
                    "Kafka",
                    *context.topics,
                    group_id,
                    context.target,
                    exception.__class__.__name__,
                ],
                extra={
                    "serviceType": "Kafka",
                    "topics": topics,
                    "groupId": group_id,
                    "target": context.target,
                    "exception": exception.__class__.__name__,
                },
                message=f"topics = `{topics}` , group id = `{group_id}` , target = `{context.target}` {exception.message}",
            ),
            exception=exception,
        )


class KafkaValidationErrorHandler(ValidationErrorHandler):
    def __call__(
        self,
        context: ConsumerContext,
        exception: ValidationError,
    ) -> None:
        topics = topics_repr(context.topics)
        group_id = group_id_repr(context.group_id)

        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.KAFKA,
                tags=[
                    "Kafka",
                    *context.topics,
                    group_id,
                    context.target,
                    "ValidationError",
                ],
                extra={
                    "serviceType": "Kafka",
                    "topics": topics,
                    "groupId": group_id,
                    "target": context.target,
                    "exception": "ValidationError",
                },
                message=f"invalid kafka event at topics `{topics}` , group id `{group_id}` and target `{context.target}`",
            ),
            exception=exception,
        )


class KafkaGeneralExceptionHandler(GeneralExceptionHandler):
    def __call__(
        self,
        context: ConsumerContext,
        exception: Exception,
    ) -> None:
        topics = topics_repr(context.topics)
        group_id = group_id_repr(context.group_id)

        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.KAFKA,
                tags=[
                    "Kafka",
                    *context.topics,
                    group_id,
                    context.target,
                    exception.__class__.__name__,
                ],
                extra={
                    "serviceType": "Kafka",
                    "topics": topics,
                    "groupId": group_id,
                    "target": context.target,
                    "exception": exception.__class__.__name__,
                },
                message=f"something went wrong while consuming event on topics `{topics}` , group id `{group_id}` and target `{context.target}`",
            ),
            exception=exception,
        )
