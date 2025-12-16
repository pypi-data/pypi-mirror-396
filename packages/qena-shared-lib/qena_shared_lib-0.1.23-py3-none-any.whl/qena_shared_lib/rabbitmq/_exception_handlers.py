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
from ._listener import ListenerContext

__all__ = [
    "RabbitMqServiceExceptionHandler",
    "RabbitMqServiceExceptionHandler",
    "RabbitMqValidationErrorHandler",
]

RABBITMQ_EXCEPTION_HANDLER_LOGGER_NAME = "rabbitmq.exception_handler"


class RabbitMqServiceExceptionHandler(ServiceExceptionHandler):
    def __init__(self, remote_logger: BaseRemoteLogSender):
        super().__init__(remote_logger)

        self._logger = LoggerFactory.get_logger(
            RABBITMQ_EXCEPTION_HANDLER_LOGGER_NAME
        )

    def __call__(
        self,
        context: ListenerContext,
        exception: ServiceException,
    ) -> None:
        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.RABBIT_MQ,
                tags=[
                    "RabbitMQ",
                    context.queue,
                    context.listener_name or "__default__",
                    exception.__class__.__name__,
                ],
                extra={
                    "serviceType": "RabbitMQ",
                    "queue": context.queue,
                    "listenerName": context.listener_name,
                    "exception": exception.__class__.__name__,
                },
                message=f"queue = `{context.queue}` listener_name = `{context.listener_name}` {exception.message}",
            ),
            exception=exception,
        )


class RabbitMqValidationErrorHandler(ValidationErrorHandler):
    def __call__(
        self,
        context: ListenerContext,
        exception: ValidationError,
    ) -> None:
        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.RABBIT_MQ,
                tags=[
                    "RabbitMQ",
                    context.queue,
                    context.listener_name or "__default__",
                    "ValidationError",
                ],
                extra={
                    "serviceType": "RabbitMQ",
                    "queue": context.queue,
                    "listenerName": context.listener_name,
                    "exception": "ValidationError",
                },
                message=f"invalid rabbitmq request data at queue `{context.queue}` and listener `{context.listener_name}`",
            ),
            exception=exception,
        )


class RabbitMqGeneralExceptionHandler(GeneralExceptionHandler):
    def __call__(
        self,
        context: ListenerContext,
        exception: Exception,
    ) -> None:
        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.RABBIT_MQ,
                tags=[
                    "RabbitMQ",
                    context.queue,
                    context.listener_name or "__default__",
                    exception.__class__.__name__,
                ],
                extra={
                    "serviceType": "RabbitMQ",
                    "queue": context.queue,
                    "listenerName": context.listener_name,
                    "exception": exception.__class__.__name__,
                },
                message=f"something went wrong while consuming message on queue `{context.queue}` and listener `{context.listener_name}`",
            ),
            exception=exception,
        )
