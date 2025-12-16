from collections.abc import Iterable
from typing import Any, cast

from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic_core import to_jsonable_python

from ..exception_handling import (
    ExceptionHandlerServiceType,
    GeneralExceptionHandler,
    ServiceExceptionHandler,
    ServiceInformation,
)
from ..exceptions import (
    HTTPServiceError,
    ServiceException,
    Severity,
)
from ..logging import LoggerFactory
from ..remotelogging import BaseRemoteLogSender

__all__ = [
    "AbstractHttpExceptionHandler",
    "HttpGeneralExceptionHandler",
    "HTTPServiceExceptionHandler",
    "RequestValidationErrorHandler",
]

HTTP_EXCEPTION_HANDLER_LOGGER_NAME = "http.exception_handler"


class AbstractHttpExceptionHandler:
    @property
    def exception(self) -> type[Exception]:
        raise NotImplementedError()


class HTTPServiceExceptionHandler(
    ServiceExceptionHandler, AbstractHttpExceptionHandler
):
    def __init__(self, remote_logger: BaseRemoteLogSender):
        super().__init__(remote_logger)

        self._logger = LoggerFactory.get_logger(
            HTTP_EXCEPTION_HANDLER_LOGGER_NAME
        )

    def __call__(
        self, request: Request, exception: ServiceException
    ) -> Response:
        severity = exception.severity or Severity.LOW
        user_agent = request.headers.get("user-agent", "__unknown__")
        tags = [
            "HTTP",
            request.method,
            request.url.path,
            exception.__class__.__name__,
        ]
        extra = {
            "serviceType": "HTTP",
            "method": request.method,
            "path": request.url.path,
            "userAgent": user_agent,
            "exception": exception.__class__.__name__,
        }
        message = exception.message

        if severity is Severity.HIGH:
            message = "something went wrong"

        content: dict[str, Any] = {
            "severity": severity.name,
            "message": message,
        }
        status_code = self._status_code_from_severity(exception.severity)
        headers = None

        if isinstance(exception, HTTPServiceError):
            if exception.body is not None:
                extra_body = to_jsonable_python(exception.body)
                is_updated = False

                try:
                    if isinstance(extra_body, Iterable):
                        content.update(extra_body)

                        is_updated = True
                except:
                    pass

                if not is_updated:
                    content["data"] = extra_body

            if exception.response_code is not None:
                content["code"] = exception.response_code

            if exception.corrective_action is not None:
                content["correctiveAction"] = exception.corrective_action

            if exception.status_code is not None:
                status_code = exception.status_code

            if exception.headers is not None:
                headers = exception.headers

        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.HTTP,
                tags=tags,
                extra=extra,
            ),
            exception=exception,
        )

        return JSONResponse(
            content=content,
            status_code=status_code,
            headers=headers,
        )

    def _status_code_from_severity(self, severity: Severity | None) -> int:
        if (
            severity is None
            or severity is Severity.LOW
            or severity is Severity.MEDIUM
        ):
            return cast(int, status.HTTP_400_BAD_REQUEST)

        return cast(int, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestValidationErrorHandler(AbstractHttpExceptionHandler):
    @property
    def exception(self) -> type[Exception]:
        return cast(type[Exception], RequestValidationError)

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("http.exception_handler")

    def __call__(
        self, request: Request, error: RequestValidationError
    ) -> Response:
        message = "invalid request data"

        self._logger.warning(
            "\n%s %s\n%s", request.method, request.url.path, message
        )

        return JSONResponse(
            content={
                "severity": Severity.MEDIUM.name,
                "message": message,
                "code": 100,
                "detail": to_jsonable_python(error.errors()),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class HttpGeneralExceptionHandler(
    GeneralExceptionHandler, AbstractHttpExceptionHandler
):
    def __call__(self, request: Request, exception: Exception) -> Response:
        user_agent = request.get("user-agent", "__unknown__")

        self.handle(
            service_information=ServiceInformation(
                service_type=ExceptionHandlerServiceType.HTTP,
                tags=[
                    "HTTP",
                    request.method,
                    request.url.path,
                    exception.__class__.__name__,
                ],
                extra={
                    "serviceType": "HTTP",
                    "method": request.method,
                    "path": request.url.path,
                    "userAgent": user_agent,
                    "exception": exception.__class__.__name__,
                },
                message=f"something went wrong on endpoint `{request.method} {request.url.path}`",
            ),
            exception=exception,
        )

        return JSONResponse(
            content={
                "severity": Severity.HIGH.name,
                "message": "something went wrong",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
