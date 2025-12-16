from asyncio import Future, Task, iscoroutinefunction
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Any, Callable, TypeVar, cast

from prometheus_client import Counter
from punq import Container, Scope
from pydantic import ValidationError
from pydantic.alias_generators import to_snake
from typing_extensions import Self

from .exceptions import (
    HTTPServiceError,
    RabbitMQServiceException,
    ServiceException,
    Severity,
)
from .logging import LoggerFactory
from .remotelogging import BaseRemoteLogSender
from .utils import AsyncEventLoopMixin

__all__ = [
    "AbstractServiceExceptionHandler",
    "ExceptionHandlerServiceType",
    "ExceptionHandlingManager",
    "GeneralExceptionHandler",
    "ServiceContext",
    "ServiceInformation",
    "ServiceExceptionHandler",
    "ValidationErrorHandler",
]


ServiceContextDataType = TypeVar("ServiceContextDataType")


class ExceptionHandlerServiceType(str, Enum):
    RABBIT_MQ = "RABBITMQ"
    HTTP = "HTTP"
    KAFKA = "KAFKA"


class ServiceContext:
    def add_data(
        self,
        data_type: type[ServiceContextDataType],
        value: ServiceContextDataType,
    ) -> Self:
        if getattr(self, "_data", None):
            self._data = {}

        self._data[data_type] = value

        return self

    def get_data(
        self, data_type: type[ServiceContextDataType]
    ) -> ServiceContextDataType | None:
        if getattr(self, "_data", None) is None:
            return None

        return cast(
            dict[type[ServiceContextDataType], ServiceContextDataType],
            self._data,
        )[data_type]

    def set_labels(self, labels: dict[str, Any]) -> Self:
        self._labels = labels

        return self

    def get_labels(self) -> dict[str, Any]:
        if getattr(self, "_labels", None) is None:
            raise ValueError("service context labels not set")

        return self._labels


@dataclass
class ServiceInformation:
    service_type: ExceptionHandlerServiceType
    tags: list[str]
    extra: dict[str, str]
    message: str | None = None


class AbstractServiceExceptionHandler:
    @property
    def exception(self) -> type[Exception]:
        raise NotImplementedError()

    def handle(
        self, service_information: ServiceInformation, exception: BaseException
    ) -> None:
        del service_information, exception

        raise NotImplementedError()


@dataclass
class ExceptionHandlerMetadata:
    exception_handler: AbstractServiceExceptionHandler

    def __post_init__(self) -> None:
        self._is_async_exception_handler = self._check_async_exception_handler(
            self.exception_handler
        )

    def _check_async_exception_handler(
        self, exception_handler: AbstractServiceExceptionHandler
    ) -> bool:
        exception_handler_callable = getattr(
            exception_handler, "__call__", None
        )

        if exception_handler_callable is None:
            raise RuntimeError(
                "exception handler has no `__call__(ServiceContext, BaseException)` method"
            )

        return iscoroutinefunction(exception_handler_callable)

    @property
    def is_async_listener(self) -> bool:
        return self._is_async_exception_handler


class ExceptionHandlingManager(AsyncEventLoopMixin):
    _HANDLER_EXCEPTIONS_COUNTER_METRICS: dict[
        ExceptionHandlerServiceType, Counter
    ] = {}

    def __init__(
        self,
        service_type: ExceptionHandlerServiceType,
        container: Container,
        remote_logger: BaseRemoteLogSender,
        label_name: list[str],
    ):
        self._service_type = service_type
        self._container = container
        self._exception_handlers: dict[
            type[Exception], ExceptionHandlerMetadata
        ] = {}
        self._remote_logger = remote_logger
        self._exception_handling_done_hook: (
            Callable[[ServiceContext], None] | None
        ) = None

        if service_type not in self._HANDLER_EXCEPTIONS_COUNTER_METRICS:
            self._HANDLER_EXCEPTIONS_COUNTER_METRICS[service_type] = Counter(
                name=f"{to_snake(service_type.name)}_handled_exceptions",
                documentation=f"{service_type.name.capitalize()} handled exceptions",
                labelnames=label_name,
            )

    def set_exception_handlers(
        self, *exception_handlers: type[AbstractServiceExceptionHandler]
    ) -> None:
        for index, exception_handler in enumerate(exception_handlers):
            if not isinstance(exception_handler, type) or not issubclass(
                exception_handler, AbstractServiceExceptionHandler
            ):
                raise TypeError(
                    f"exception handler {index} is {type(exception_handler)}, expected instance of type or subclass of `AbstractServiceExceptionHandler`"
                )

            self._container.register(
                service=AbstractServiceExceptionHandler,
                factory=exception_handler,
                scope=Scope.singleton,
            )

    def set_exception_handling_done_hook(
        self, exception_handling_done_hook: Callable[[ServiceContext], None]
    ) -> None:
        if not callable(exception_handling_done_hook):
            raise ValueError("`exception_handler_done_hook` is not a callable")

        self._exception_handling_done_hook = exception_handling_done_hook

    def resolve_exception_handlers(self) -> None:
        for exception_handler in self._container.resolve_all(
            AbstractServiceExceptionHandler
        ):
            exception_handler = cast(
                AbstractServiceExceptionHandler, exception_handler
            )

            if not callable(exception_handler):
                raise ValueError(
                    f"exception handler {exception_handler.__class__.__name__} is not callable"
                )

            self._exception_handlers[exception_handler.exception] = (
                ExceptionHandlerMetadata(exception_handler)
            )

    def submit_exception(
        self,
        context: ServiceContext,
        exception: BaseException,
    ) -> bool:
        exception_handler_metadata = None

        for exception_type in type(exception).mro():
            exception_handler_metadata = self._exception_handlers.get(
                exception_type
            )

            if exception_handler_metadata is not None:
                break

        if exception_handler_metadata is None:
            return False

        assert callable(exception_handler_metadata.exception_handler)

        if exception_handler_metadata.is_async_listener:
            self.loop.create_task(
                exception_handler_metadata.exception_handler(context, exception)
            ).add_done_callback(
                partial(self._on_exception_handler_done, context)
            )
        else:
            self.loop.run_in_executor(
                executor=None,
                func=partial(
                    exception_handler_metadata.exception_handler,
                    context,
                    exception,
                ),
            ).add_done_callback(
                partial(self._on_exception_handler_done, context)
            )

        self._HANDLER_EXCEPTIONS_COUNTER_METRICS[self._service_type].labels(
            *context.get_labels()
        ).inc()

        return True

    def _on_exception_handler_done(
        self, context: ServiceContext, task_or_future: Task[Any] | Future[Any]
    ) -> None:
        if task_or_future.cancelled():
            return

        exception = task_or_future.exception()
        service_information = context.get_data(ServiceInformation)

        if service_information is not None:
            service_type = service_information.service_type.name.lower()
            tags = service_information.tags
            extra = service_information.extra
        else:
            service_type = "unknown"
            tags = ["exception_handling"]
            extra = {"serviceType": "exception_handling"}

        if exception is not None:
            self._remote_logger.error(
                message=f"error occured in {service_type} service exception handler",
                tags=tags,
                extra=extra,
                exception=exception,
            )

        if self._exception_handling_done_hook is None:
            return

        try:
            self._exception_handling_done_hook(context)
        except:
            tags.append("exception_handler_done_hook")
            self._remote_logger.exception(
                message="error occured while executing `exception_handler_done_hook`",
                tags=tags,
                extra=extra,
            )


EXCEPTION_HANDLING_LOGGER_NAME = "exception_handling"


class ServiceExceptionHandler(AbstractServiceExceptionHandler):
    @property
    def exception(self) -> type[Exception]:
        return cast(type[Exception], ServiceException)

    def __init__(self, remote_logger: BaseRemoteLogSender):
        self._logger = LoggerFactory.get_logger(EXCEPTION_HANDLING_LOGGER_NAME)
        self._remote_logger = remote_logger

    def handle(
        self,
        service_information: ServiceInformation,
        exception: BaseException,
    ) -> None:
        if not isinstance(exception, ServiceException):
            self._logger.warning(
                "%s cannot be handled by handler", exception.__class__.__name__
            )

            return

        match exception:
            case HTTPServiceError() as http_service_error:
                if http_service_error.status_code is not None:
                    str_status_code = str(http_service_error.status_code)
                    service_information.extra["statusCode"] = str_status_code

                    service_information.tags.append(str_status_code)

                if http_service_error.response_code is not None:
                    str_response_code = str(http_service_error.response_code)
                    service_information.extra["responseCode"] = (
                        str_response_code
                    )

                    service_information.tags.append(str_response_code)
            case RabbitMQServiceException() as rabbitmq_service_exception:
                str_error_code = str(rabbitmq_service_exception.code)
                service_information.extra["code"] = str_error_code

                service_information.tags.append(str_error_code)

        if exception.tags:
            service_information.tags.extend(exception.tags)

        if exception.extra:
            service_information.extra.update(exception.extra)

        exc_info = (
            (type(exception), exception, exception.__traceback__)
            if exception.extract_exc_info
            else None
        )

        match exception.severity:
            case Severity.HIGH:
                remote_logger_method = self._remote_logger.error
                logger_method = self._logger.error
            case Severity.MEDIUM:
                remote_logger_method = self._remote_logger.warning
                logger_method = self._logger.warning
            case _:
                remote_logger_method = self._remote_logger.info
                logger_method = self._logger.info

        if exception.remote_logging:
            remote_logger_method(
                message=service_information.message or exception.message,
                tags=service_information.tags,
                extra=service_information.extra,
                exception=exception if exception.extract_exc_info else None,
            )
        else:
            logger_method(
                "[service_type = `%s`] `%s`",
                service_information.service_type.name.lower(),
                service_information.message or exception.message,
                exc_info=exc_info,
            )


class ValidationErrorHandler(AbstractServiceExceptionHandler):
    @property
    def exception(self) -> type[Exception]:
        return cast(type[Exception], ValidationError)

    def __init__(self, remote_logger: BaseRemoteLogSender):
        self._remote_logger = remote_logger

    def handle(
        self,
        service_information: ServiceInformation,
        exception: ValidationError,
    ) -> None:
        self._remote_logger.error(
            message=service_information.message
            or f"invalid request data for {service_information.service_type.name.lower()} service",
            tags=service_information.tags,
            extra=service_information.extra,
            exception=exception,
        )


class GeneralExceptionHandler(AbstractServiceExceptionHandler):
    @property
    def exception(self) -> type[Exception]:
        return Exception

    def __init__(self, remote_logger: BaseRemoteLogSender):
        self._remote_logger = remote_logger

    def handle(
        self,
        service_information: ServiceInformation,
        exception: BaseException,
    ) -> None:
        self._remote_logger.error(
            message=service_information.message
            or f"something went wrong while processing data for {service_information.service_type.name.lower()} service",
            tags=service_information.tags,
            extra=service_information.extra,
            exception=exception,
        )
